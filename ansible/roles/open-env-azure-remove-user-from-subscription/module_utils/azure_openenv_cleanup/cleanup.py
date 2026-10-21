# Copyright: (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Hardened Azure subscription / resource-group cleanup for open environments.

Ported from pool_mgmt/clean_sub.py (ARO NAT teardown, AIServices blockers,
topo-sorted RG delete, leftover abort). Does NOT release pool allocations —
Sandbox API owns that (standalone clean_sub is the ops exception).
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re
import sys
import time
from collections import defaultdict, deque

try:
    import requests
    from azure.identity import AzureCliCredential, DefaultAzureCredential
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.network import NetworkManagementClient
    HAS_AZURE = True
    IMPORT_ERROR = None
except Exception as e:  # pragma: no cover - reported by Ansible module
    HAS_AZURE = False
    IMPORT_ERROR = e
    requests = None
    AzureCliCredential = None
    DefaultAzureCredential = None
    ResourceManagementClient = None
    NetworkManagementClient = None

try:
    from azure.mgmt.redhatopenshift import AzureRedHatOpenShiftClient
    HAS_ARO = True
except Exception:
    HAS_ARO = False
    AzureRedHatOpenShiftClient = None


NETWORK_LISTERS = (
    "load_balancers",
    "network_interfaces",
    "nat_gateways",
    "virtual_networks",
    "public_ip_addresses",
    "application_gateways",
    "private_endpoints",
    "network_security_groups",
    "route_tables",
    "bastion_hosts",
)

RG_ID_RE = re.compile(
    r"/subscriptions/[^/]+/resourcegroups/([^/]+)",
    re.IGNORECASE,
)

# Nested ARM types that block RG delete (must go before begin_delete on the RG).
# Note: managedComputeDeployments and moveResources do NOT appear in
# resources.list(); they must be enumerated via their parent collection APIs.
BLOCKING_RESOURCE_TYPES = (
    ("microsoft.cognitiveservices/accounts/deployments", "2024-10-01"),
    ("microsoft.migrate/movecollections/moveresources", "2023-08-01"),
    ("microsoft.monitor/accounts", "2023-04-03"),
)

# Foundry/AIServices managed-compute deployments use a separate child type
# (not Microsoft.CognitiveServices/accounts/deployments). API versions are
# only registered under 2026-* / 2099-01-01 today.
AISERVICES_ACCOUNT_API = "2024-10-01"
MANAGED_COMPUTE_API = "2026-01-15-preview"
MOVE_COLLECTION_API = "2023-08-01"
ARM_BASE = "https://management.azure.com"

SUBNET_ID_RE = re.compile(
    r"/resourcegroups/([^/]+)/providers/microsoft\.network/virtualnetworks/([^/]+)/subnets/([^/]+)",
    re.IGNORECASE,
)


def _rg_from_arm_id(resource_id: str | None) -> str | None:
    if not resource_id:
        return None
    match = RG_ID_RE.search(resource_id)
    return match.group(1) if match else None


# Subnet/PIP ipConfigurations point at consumers (NICs, LBs). Walking those
# would reverse the real delete order (VNet RG would look like it uses the cluster RG).
_REVERSE_REF_KEYS = {"ip_configurations", "ipconfigurations"}


def _walk_arm_ids(obj, skip_reverse: bool = False) -> list[str]:
    found: list[str] = []
    if obj is None:
        return found
    if hasattr(obj, "as_dict"):
        obj = obj.as_dict()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if skip_reverse and key.lower().replace("-", "_") in _REVERSE_REF_KEYS:
                continue
            found.extend(_walk_arm_ids(value, skip_reverse=skip_reverse))
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            found.extend(_walk_arm_ids(item, skip_reverse=skip_reverse))
    elif isinstance(obj, str) and "/resourcegroups/" in obj.lower():
        found.append(obj)
    return found


def _canonical_rg(name: str | None, known: dict[str, str]) -> str | None:
    if not name:
        return None
    return known.get(name.lower())


def collect_rg_dependencies(credential, sub_id: str, rg_names: list[str]) -> dict[str, set[str]]:
    """Return {user_rg: {provider_rg, ...}} where user_rg must be deleted first.

    A load balancer / NIC in the cluster RG pointing at a subnet in openshift-rg
    means the cluster RG uses openshift-rg and must go first.
    """
    known = {name.lower(): name for name in rg_names}
    deps: dict[str, set[str]] = {name: set() for name in rg_names}

    network = NetworkManagementClient(credential, sub_id)
    for lister_name in NETWORK_LISTERS:
        lister = getattr(network, lister_name, None)
        if lister is None or not hasattr(lister, "list_all"):
            continue
        try:
            resources = list(lister.list_all())
        except Exception as e:
            print(f"WARNING: could not list {lister_name} for dependency scan: {e}")
            continue
        # VNet/PIP ipConfigurations are reverse pointers (consumers). NIC/LB
        # ip_configurations are the real outbound subnet/PIP edges.
        skip_reverse = lister_name in ("virtual_networks", "public_ip_addresses")
        for resource in resources:
            owner = _canonical_rg(_rg_from_arm_id(getattr(resource, "id", None)), known)
            if not owner:
                continue
            for arm_id in _walk_arm_ids(resource, skip_reverse=skip_reverse):
                other = _canonical_rg(_rg_from_arm_id(arm_id), known)
                if other and other != owner:
                    deps[owner].add(other)
    return deps


def deletion_order(rg_names: list[str], deps: dict[str, set[str]]) -> list[str]:
    """Topological sort: RGs that use others are deleted first."""
    providers: dict[str, set[str]] = defaultdict(set)
    indegree = {name: 0 for name in rg_names}
    for user, used in deps.items():
        for provider in used:
            if provider not in indegree:
                continue
            if user not in providers[provider]:
                providers[provider].add(user)
                indegree[provider] += 1

    queue = deque(sorted(name for name, n in indegree.items() if n == 0))
    ordered: list[str] = []
    while queue:
        user = queue.popleft()
        ordered.append(user)
        for provider, users in list(providers.items()):
            if user not in users:
                continue
            users.remove(user)
            indegree[provider] -= 1
            if indegree[provider] == 0:
                queue.append(provider)

    leftover = sorted(name for name in rg_names if name not in ordered)
    return ordered + leftover


def _arm_headers(credential) -> dict[str, str]:
    token = credential.get_token("https://management.azure.com/.default").token
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _arm_get(credential, path: str, api: str) -> tuple[int, dict | list | str]:
    url = f"{ARM_BASE}{path}?api-version={api}"
    resp = requests.get(url, headers=_arm_headers(credential), timeout=60)
    try:
        body = resp.json()
    except Exception:
        body = resp.text
    return resp.status_code, body


def _arm_delete_and_wait(
    credential, path: str, api: str, subname: str, label: str
) -> None:
    url = f"{ARM_BASE}{path}?api-version={api}"
    print(f"Deleting blocking {label} in {subname}")
    resp = requests.delete(url, headers=_arm_headers(credential), timeout=60)
    if resp.status_code in (200, 202, 204):
        async_url = resp.headers.get("Azure-AsyncOperation") or resp.headers.get(
            "Location"
        )
        if async_url and resp.status_code == 202:
            deadline = time.time() + 1800
            while time.time() < deadline:
                poll = requests.get(
                    async_url, headers=_arm_headers(credential), timeout=60
                )
                try:
                    body = poll.json()
                except Exception:
                    body = {}
                status = str(
                    body.get("status")
                    or body.get("properties", {}).get("provisioningState")
                    or ""
                ).lower()
                if poll.status_code in (200, 201) and status in (
                    "succeeded",
                    "failed",
                    "canceled",
                    "cancelled",
                ):
                    if status != "succeeded":
                        print(
                            f"WARNING: {subname}: async delete of {label} ended {status}"
                        )
                    return
                if poll.status_code == 404:
                    return
                time.sleep(10)
            print(f"WARNING: {subname}: timed out waiting for delete of {label}")
        return
    if resp.status_code == 404:
        return
    print(
        f"WARNING: {subname}: failed to delete {label}: "
        f"{resp.status_code} {resp.text[:300]}"
    )


def _normalize_rg_filter(only_resource_groups):
    if not only_resource_groups:
        return None
    return {name.lower(): name for name in only_resource_groups}


def _rg_allowed(name, allowed_map):
    if allowed_map is None:
        return True
    return name.lower() in allowed_map


def _ignore_leftover(name, ignore_prefixes):
    lower = name.lower()
    for prefix in ignore_prefixes or ():
        if lower.startswith(prefix.lower()):
            return True
    return False


def delete_aiservices_blockers(
    credential, sub_id, subname, dryrun, only_resource_groups=None
):
    """Delete AIServices/Foundry managed-compute + model deployments before RG delete."""
    code, body = _arm_get(
        credential,
        f"/subscriptions/{sub_id}/providers/Microsoft.CognitiveServices/accounts",
        AISERVICES_ACCOUNT_API,
    )
    if code != 200 or not isinstance(body, dict):
        if code != 200:
            print(
                f"WARNING: {subname}: could not list Cognitive Services accounts: {code}"
            )
        return
    for acct in body.get("value") or []:
        acct_id = acct.get("id")
        acct_name = acct.get("name")
        if not acct_id or not acct_name:
            continue
        rg = _rg_from_arm_id(acct_id)
        if not _rg_allowed(rg or "", only_resource_groups):
            continue
        # Managed compute (Foundry) — not returned by resources.list()
        mcode, mbody = _arm_get(
            credential, f"{acct_id}/managedComputeDeployments", MANAGED_COMPUTE_API
        )
        if mcode == 200 and isinstance(mbody, dict):
            for dep in mbody.get("value") or []:
                dep_id = dep.get("id")
                dep_name = dep.get("name")
                if not dep_id:
                    continue
                label = f"managedComputeDeployment {acct_name}/{dep_name}"
                if dryrun:
                    print(f"Would delete blocking {label} in {subname}")
                    continue
                _arm_delete_and_wait(
                    credential, dep_id, MANAGED_COMPUTE_API, subname, label
                )
        elif mcode not in (200, 404) and "ApiVersionNotRegistered" not in str(mbody):
            print(
                f"WARNING: {subname}: list managedComputeDeployments "
                f"for {acct_name} failed: {mcode} {str(mbody)[:200]}"
            )
        # Standard Cognitive / OpenAI deployments
        dcode, dbody = _arm_get(
            credential, f"{acct_id}/deployments", AISERVICES_ACCOUNT_API
        )
        if dcode == 200 and isinstance(dbody, dict):
            for dep in dbody.get("value") or []:
                dep_id = dep.get("id")
                dep_name = dep.get("name")
                if not dep_id:
                    continue
                label = f"deployment {acct_name}/{dep_name}"
                if dryrun:
                    print(f"Would delete blocking {label} in {subname}")
                    continue
                _arm_delete_and_wait(
                    credential, dep_id, AISERVICES_ACCOUNT_API, subname, label
                )


def delete_move_collection_blockers(
    credential, resource_client, subname, dryrun, only_resource_groups=None
):
    """Delete moveResources inside Azure Resource Mover collections."""
    try:
        collections = [
            res
            for res in resource_client.resources.list()
            if (getattr(res, "type", "") or "").lower()
            == "microsoft.migrate/movecollections"
            and _rg_allowed(_rg_from_arm_id(getattr(res, "id", None)) or "", only_resource_groups)
        ]
    except Exception as e:
        print(f"WARNING: {subname}: could not list move collections: {e}")
        return
    for coll in collections:
        code, body = _arm_get(
            credential, f"{coll.id}/moveResources", MOVE_COLLECTION_API
        )
        if code != 200 or not isinstance(body, dict):
            if code != 200:
                print(
                    f"WARNING: {subname}: list moveResources for {coll.name} "
                    f"failed: {code}"
                )
            continue
        for item in body.get("value") or []:
            item_id = item.get("id")
            item_name = item.get("name")
            if not item_id:
                continue
            label = f"moveResource {coll.name}/{item_name}"
            if dryrun:
                print(f"Would delete blocking {label} in {subname}")
                continue
            _arm_delete_and_wait(
                credential, item_id, MOVE_COLLECTION_API, subname, label
            )


def delete_blocking_resources(
    resource_client, credential, sub_id, subname, dryrun, only_resource_groups=None
):
    """Delete nested resources that cause ResourceGroupDeletionBlocked."""
    delete_aiservices_blockers(
        credential, sub_id, subname, dryrun, only_resource_groups=only_resource_groups
    )
    delete_move_collection_blockers(
        credential, resource_client, subname, dryrun,
        only_resource_groups=only_resource_groups,
    )

    wanted = {t: api for t, api in BLOCKING_RESOURCE_TYPES}
    by_type = defaultdict(list)
    try:
        for res in resource_client.resources.list():
            t = (getattr(res, "type", None) or "").lower()
            if t in wanted and _rg_allowed(
                _rg_from_arm_id(getattr(res, "id", None)) or "", only_resource_groups
            ):
                by_type[t].append(res)
    except Exception as e:
        print(f"WARNING: {subname}: could not list subscription resources: {e}")
        return
    for type_name, api in BLOCKING_RESOURCE_TYPES:
        for res in by_type.get(type_name, []):
            print(f"Deleting blocking {res.type} {res.name} in {subname}")
            if dryrun:
                continue
            try:
                poller = resource_client.resources.begin_delete_by_id(res.id, api)
                poller.result()
            except Exception as e:
                if "NotFound" in str(e) or "ResourceNotFound" in str(e):
                    continue
                print(f"WARNING: {subname}: Failed to delete {res.id}: {e}")


def _subnet_parts(subnet_id: str) -> tuple[str, str, str] | None:
    match = SUBNET_ID_RE.search(subnet_id)
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3)


def clear_subnet_nat_gateways(network: NetworkManagementClient, subnet_ids: list[str], subname: str) -> None:
    seen: set[str] = set()
    for subnet_id in subnet_ids:
        if not subnet_id or subnet_id in seen:
            continue
        seen.add(subnet_id)
        parts = _subnet_parts(subnet_id)
        if not parts:
            continue
        rg_name, vnet_name, subnet_name = parts
        try:
            subnet = network.subnets.get(rg_name, vnet_name, subnet_name)
        except Exception as e:
            print(f"WARNING: {subname}: could not get subnet {subnet_id}: {e}")
            continue
        if not getattr(subnet, "nat_gateway", None):
            continue
        print(f"Disassociating NAT gateway from {subnet_id} ({subname})")
        subnet.nat_gateway = None
        try:
            network.subnets.begin_create_or_update(
                rg_name, vnet_name, subnet_name, subnet
            ).result()
        except Exception as e:
            print(f"WARNING: {subname}: failed to clear NAT on {subnet_id}: {e}")


def delete_nat_gateways_for_subnets(
    network: NetworkManagementClient, subnet_ids: list[str], subname: str
) -> None:
    """Remove NAT GWs in ARO VNet RGs so ARO delete does not need natGateways/join."""
    target_rgs = set()
    for subnet_id in subnet_ids:
        parts = _subnet_parts(subnet_id or "")
        if parts:
            target_rgs.add(parts[0].lower())
    if not target_rgs:
        return
    try:
        gateways = list(network.nat_gateways.list_all())
    except Exception as e:
        print(f"WARNING: {subname}: could not list NAT gateways: {e}")
        return
    for gw in gateways:
        gw_rg = _rg_from_arm_id(getattr(gw, "id", None))
        if not gw_rg or gw_rg.lower() not in target_rgs:
            continue
        print(f"Deleting NAT gateway {gw.name} in {gw_rg} ({subname})")
        try:
            network.nat_gateways.begin_delete(gw_rg, gw.name).result()
        except Exception as e:
            print(f"WARNING: {subname}: failed to delete NAT gateway {gw.name}: {e}")


def _aro_subnet_ids(cluster) -> list[str]:
    ids: list[str] = []
    master = getattr(cluster, "master_profile", None)
    if master and getattr(master, "subnet_id", None):
        ids.append(master.subnet_id)
    worker = getattr(cluster, "worker_profiles", None) or []
    for profile in worker:
        if getattr(profile, "subnet_id", None):
            ids.append(profile.subnet_id)
    return ids


def _aro_managed_rg(cluster) -> str | None:
    profile = getattr(cluster, "cluster_profile", None)
    rgid = getattr(profile, "resource_group_id", None) if profile else None
    if not rgid:
        return None
    return rgid.rstrip("/").split("/")[-1]


def aro_protected_resource_groups(aro_client) -> set[str]:
    """Customer + managed RGs that must not be deleted while an ARO cluster exists."""
    protected: set[str] = set()
    for cluster in list(aro_client.open_shift_clusters.list()):
        protected.add(cluster.id.split("/")[4])
        managed = _aro_managed_rg(cluster)
        if managed:
            protected.add(managed)
        for subnet_id in _aro_subnet_ids(cluster):
            parts = _subnet_parts(subnet_id)
            if parts:
                protected.add(parts[0])
    return {name.lower() for name in protected}



def _aro_cluster_in_scope(cluster, only_resource_groups):
    if only_resource_groups is None:
        return True
    rg_name = cluster.id.split("/")[4]
    if _rg_allowed(rg_name, only_resource_groups):
        return True
    managed = _aro_managed_rg(cluster)
    if managed and _rg_allowed(managed, only_resource_groups):
        return True
    for subnet_id in _aro_subnet_ids(cluster):
        parts = _subnet_parts(subnet_id)
        if parts and _rg_allowed(parts[0], only_resource_groups):
            return True
    return False



def _az_aro_list(sub_id):
    """List ARO clusters via Azure CLI when SDK is unavailable."""
    import json
    import subprocess
    try:
        out = subprocess.check_output(
            [
                "az", "aro", "list",
                "--subscription", sub_id,
                "-o", "json",
            ],
            stderr=subprocess.STDOUT,
            text=True,
        )
        return json.loads(out or "[]")
    except Exception as e:
        print("WARNING: az aro list failed: {0}".format(e))
        return []


def _az_aro_delete(sub_id, rg_name, cluster_name, subname):
    import subprocess
    print(
        "Deleting ARO cluster {0} in {1} ({2}) via az cli".format(
            cluster_name, rg_name, subname
        )
    )
    try:
        subprocess.check_call(
            [
                "az", "aro", "delete",
                "--subscription", sub_id,
                "--resource-group", rg_name,
                "--name", cluster_name,
                "--yes",
            ]
        )
    except Exception as e:
        print("WARNING: {0}: az aro delete failed: {1}".format(subname, e))


def leftover_aro_clusters(credential, sub_id, only_resource_groups=None):
    if HAS_ARO:
        aro_client = AzureRedHatOpenShiftClient(credential, sub_id)
        return [
            c.name
            for c in aro_client.open_shift_clusters.list()
            if _aro_cluster_in_scope(c, only_resource_groups)
        ]
    names = []
    for c in _az_aro_list(sub_id):
        # CLI JSON uses id / name / resourceGroup
        cid = c.get("id") or ""
        rg = c.get("resourceGroup") or (cid.split("/")[4] if "/resourceGroups/" in cid else "")
        name = c.get("name")
        if not name:
            continue
        if only_resource_groups is None or _rg_allowed(rg, only_resource_groups):
            names.append(name)
    return names


def wait_for_aro_absent(aro_client, rg_name: str, cluster_name: str, subname: str, timeout: int = 1800) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            cluster = aro_client.open_shift_clusters.get(rg_name, cluster_name)
        except Exception as e:
            if "NotFound" in str(e) or "not found" in str(e).lower():
                return True
            print(f"WARNING: {subname}: ARO get {cluster_name} failed: {e}")
            return False
        state = getattr(cluster, "provisioning_state", "?")
        print(f"Waiting for ARO cluster {cluster_name} ({state}) ({subname})...")
        time.sleep(20)
    print(f"WARNING: {subname}: timed out waiting for ARO cluster {cluster_name}")
    return False


def delete_aro_clusters(credential, sub_id, subname, dryrun, only_resource_groups=None):
    if not HAS_ARO:
        for c in _az_aro_list(sub_id):
            cid = c.get("id") or ""
            rg_name = c.get("resourceGroup") or (
                cid.split("/")[4] if "/resourceGroups/" in cid else ""
            )
            name = c.get("name")
            if not name or not rg_name:
                continue
            if only_resource_groups is not None and not _rg_allowed(
                rg_name, only_resource_groups
            ):
                continue
            if dryrun:
                print(
                    "Would delete ARO cluster {0} in {1} ({2})".format(
                        name, rg_name, subname
                    )
                )
                continue
            _az_aro_delete(sub_id, rg_name, name, subname)
        return

    aro_client = AzureRedHatOpenShiftClient(credential, sub_id)
    network = NetworkManagementClient(credential, sub_id)
    for cluster in list(aro_client.open_shift_clusters.list()):
        if not _aro_cluster_in_scope(cluster, only_resource_groups):
            continue
        rg_name = cluster.id.split("/")[4]
        state = getattr(cluster, "provisioning_state", "")
        print(f"Deleting ARO cluster {cluster.name} in {rg_name} ({subname}) state={state}")
        if dryrun:
            continue
        if state == "Deleting":
            wait_for_aro_absent(aro_client, rg_name, cluster.name, subname)
            continue
        subnet_ids = _aro_subnet_ids(cluster)
        clear_subnet_nat_gateways(network, subnet_ids, subname)
        delete_nat_gateways_for_subnets(network, subnet_ids, subname)
        try:
            poller = aro_client.open_shift_clusters.begin_delete(rg_name, cluster.name)
            poller.result()
        except Exception as e:
            err = str(e)
            if "RequestNotAllowed" in err and "Deleting" in err:
                wait_for_aro_absent(aro_client, rg_name, cluster.name, subname)
                continue
            if "InvalidLinkedSubnet" in err or "LinkedAuthorizationFailed" in err:
                print(f"WARNING: {subname}: ARO delete blocked on NAT; retrying after NAT teardown")
                clear_subnet_nat_gateways(network, subnet_ids, subname)
                delete_nat_gateways_for_subnets(network, subnet_ids, subname)
                try:
                    poller = aro_client.open_shift_clusters.begin_delete(rg_name, cluster.name)
                    poller.result()
                    continue
                except Exception as e2:
                    err = str(e2)
            print(f"WARNING: {subname}: ARO cluster delete failed: {e}")
            print(f"Continuing with resource group cleanup ({subname})...")


def delete_resource_groups(
    resource_client,
    credential,
    sub_id,
    subname,
    dryrun,
    only_resource_groups=None,
):
    rg_names = [
        rg.name
        for rg in resource_client.resource_groups.list()
        if _rg_allowed(rg.name, only_resource_groups)
    ]
    if not rg_names:
        return []

    deps = collect_rg_dependencies(credential, sub_id, rg_names)
    ordered = deletion_order(rg_names, deps)

    if HAS_ARO:
        aro_client = AzureRedHatOpenShiftClient(credential, sub_id)
        protected = aro_protected_resource_groups(aro_client)
    else:
        protected = set()
        for c in _az_aro_list(sub_id):
            cid = c.get("id") or ""
            rg = (c.get("resourceGroup") or "").lower()
            if rg:
                protected.add(rg)
            if "/resourceGroups/" in cid:
                protected.add(cid.split("/")[4].lower())
    if protected:
        print(f"Skipping ARO-protected resource groups while clusters exist ({subname}): {', '.join(sorted(protected))}")

    print(f"Resource group deletion order for {subname}:")
    for name in ordered:
        used = sorted(deps.get(name) or [])
        extra = f" (uses {', '.join(used)})" if used else ""
        skip = " [skip: ARO still present]" if name.lower() in protected else ""
        print(f"  - {name}{extra}{skip}")

    remaining = [name for name in ordered if name.lower() not in protected]
    failed_rgs: list[str] = []
    while remaining:
        failed_this_pass: list[str] = []
        for name in remaining:
            print(f"Deleting resource group {name} in {subname}")
            if dryrun:
                continue
            try:
                poller = resource_client.resource_groups.begin_delete(name)
                poller.result()
            except Exception as e:
                err = str(e)
                if "ResourceGroupNotFound" in err:
                    print(f"Resource group {name} already gone ({subname})")
                    continue
                if "DenyAssignmentAuthorizationFailed" in err:
                    print(f"WARNING: {subname}: deny assignment on {name}; leaving for ARO/platform cleanup")
                failed_this_pass.append(name)
                print(f"WARNING: {subname}: Failed to delete resource group {name}: {e}")
                print(f"Continuing with remaining cleanup ({subname})...")
        if dryrun:
            break
        if not failed_this_pass or failed_this_pass == remaining:
            failed_rgs = failed_this_pass
            break
        print(
            f"Retrying {len(failed_this_pass)} resource group(s) after dependents deleted..."
        )
        remaining = failed_this_pass
    return failed_rgs


def leftover_resource_groups(resource_client) -> list[str]:
    """Re-list RGs so we never release a sub that still has Azure leftovers."""
    try:
        return sorted(rg.name for rg in resource_client.resource_groups.list())
    except Exception as e:
        print(f"WARNING: could not re-list resource groups: {e}")
        return ["<list-failed>"]



def get_credential(auth_source="cli"):
    """Return an azure-identity credential after Ansible has logged in."""
    if not HAS_AZURE:
        raise RuntimeError("Azure SDK dependencies missing: {0}".format(IMPORT_ERROR))
    if auth_source == "cli":
        return AzureCliCredential()
    if auth_source == "env":
        return DefaultAzureCredential(exclude_interactive_browser_credential=True)
    raise ValueError("Unsupported auth_source: {0}".format(auth_source))


class CleanupResult(object):
    def __init__(self, failed_rgs=None, leftover_rgs=None, leftover_aro=None, messages=None):
        self.failed_rgs = list(failed_rgs or [])
        self.leftover_rgs = list(leftover_rgs or [])
        self.leftover_aro = list(leftover_aro or [])
        self.messages = list(messages or [])

    @property
    def ok(self):
        return not self.failed_rgs and not self.leftover_rgs and not self.leftover_aro


def cleanup_azure_subscription(
    subscription_id,
    auth_source="cli",
    dry_run=False,
    only_resource_groups=None,
    ignore_leftover_prefixes=None,
    label=None,
    credential=None,
    log=None,
):
    """Clean Azure resources in a subscription (or a subset of RGs).

    :param subscription_id: Azure subscription GUID
    :param auth_source: 'cli' (AzureCliCredential) or 'env' (DefaultAzureCredential)
    :param dry_run: preview only
    :param only_resource_groups: if set, only delete these RG names (shared-sub safe)
    :param ignore_leftover_prefixes: leftover RGs with these prefixes do not fail the run
           (e.g. VisualStudioOnline-)
    :param label: log label (defaults to subscription_id)
    :param credential: optional pre-built credential
    :param log: callable(msg) for output (defaults to print)
    :returns: CleanupResult
    """
    if not HAS_AZURE:
        raise RuntimeError("Azure SDK dependencies missing: {0}".format(IMPORT_ERROR))
    if not HAS_ARO:
        # ARO SDK optional — delete_aro_clusters falls back to `az aro`.
        pass

    def _default_log(msg):
        sys.stdout.write(str(msg) + "\n")
        sys.stdout.flush()

    _log = log or _default_log
    # rebind print used by helpers via monkeypatch style — helpers call print();
    # temporarily replace builtins.print
    import builtins
    orig_print = builtins.print

    def _print(*args, **kwargs):
        sep = kwargs.get("sep", " ")
        _log(sep.join(str(a) for a in args))

    builtins.print = _print
    try:
        subname = label or subscription_id
        cred = credential or get_credential(auth_source)
        allowed = _normalize_rg_filter(only_resource_groups)
        ignore_prefixes = list(ignore_leftover_prefixes or [])

        delete_aro_clusters(
            cred, subscription_id, subname, dry_run, only_resource_groups=allowed
        )

        resource_client = ResourceManagementClient(cred, subscription_id)
        delete_blocking_resources(
            resource_client,
            cred,
            subscription_id,
            subname,
            dry_run,
            only_resource_groups=allowed,
        )

        failed_rgs = delete_resource_groups(
            resource_client,
            cred,
            subscription_id,
            subname,
            dry_run,
            only_resource_groups=allowed,
        )

        leftover = []
        still_aro = []
        if not dry_run:
            leftover_all = leftover_resource_groups(resource_client)
            if allowed is not None:
                leftover = [n for n in leftover_all if n.lower() in allowed]
            else:
                leftover = leftover_all
            leftover = [n for n in leftover if not _ignore_leftover(n, ignore_prefixes)]
            still_aro = leftover_aro_clusters(
                cred, subscription_id, only_resource_groups=allowed
            )

        result = CleanupResult(
            failed_rgs=failed_rgs,
            leftover_rgs=leftover,
            leftover_aro=still_aro,
        )
        if not result.ok and not dry_run:
            _log("WARNING: Azure cleanup incomplete for {0}:".format(subname))
            for name in dict.fromkeys(list(failed_rgs) + list(leftover)):
                _log("  - RG {0}".format(name))
            for name in still_aro:
                _log("  - ARO {0}".format(name))
        return result
    finally:
        builtins.print = orig_print
