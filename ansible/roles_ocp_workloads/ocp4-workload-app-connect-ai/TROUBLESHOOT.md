# Workload Troubleshooting Guide

This document covers known issues, their symptoms, and resolutions for the `ocp4-workload-app-connect-ai` workload.

---

## Service Interconnect

### AccessToken shows `Error: 404 (Not Found) No such access granted`

**Symptoms**

```
$ oc get accesstoken token-user1 -n shared-database
NAME          REDEEMED   STATUS   MESSAGE
token-user1              Error    Controller got failed response: 404 (Not Found) No such access granted
```

The AccessGrant shows `Ready` and may show `REDEMPTIONS MADE: 1`, but no Link is created in `shared-database`.

**Cause**

When an AccessToken is deleted, Skupper does not clean up the associated **Secret** and **Link** resources in the same namespace. If a new AccessToken is created with the same name, the controller finds the stale Secret and silently fails to process the redemption.

**Resolution**

Delete the orphaned Secret and Link before recreating the AccessToken:

```bash
oc delete accesstoken token-user1 -n shared-database
oc delete link token-user1 -n shared-database
oc delete secret token-user1 -n shared-database
```

Then recreate the AccessGrant and AccessToken from scratch. If the AccessGrant was already consumed (`REDEMPTIONS MADE: 1`), delete and recreate it too.

**Prevention**

Always delete the Link and Secret when cleaning up an AccessToken. The teardown script (`test_feature2_v2/docs/teardown-link.sh`) handles this automatically.

---

### YAML parsing error when creating AccessToken: `invalid Yaml document separator`

**Symptoms**

```
error: error parsing STDIN: invalid Yaml document separator: --END CERTIFICATE-----
```

This happens when pasting the AccessToken YAML with the CA certificate inline.

**Cause**

The PEM certificate contains `-----END CERTIFICATE-----` which YAML interprets as a document separator (`---`). If the certificate is not properly indented under a block scalar (`|`), the parser breaks.

**Resolution**

Extract the grant details into shell variables and use proper YAML block scalar notation:

```bash
URL=$(oc get accessgrant grant-user1 -n user1-devspaces -o jsonpath='{.status.url}')
CODE=$(oc get accessgrant grant-user1 -n user1-devspaces -o jsonpath='{.status.code}')
CA=$(oc get accessgrant grant-user1 -n user1-devspaces -o jsonpath='{.status.ca}' | sed 's/^/    /')

cat <<EOF | oc apply -f -
apiVersion: skupper.io/v2alpha1
kind: AccessToken
metadata:
  name: token-user1
  namespace: shared-database
spec:
  url: "${URL}"
  code: "${CODE}"
  ca: |
${CA}
EOF
```

The `sed 's/^/    /'` adds 4-space indentation to each line of the certificate, and the `|` block scalar preserves the multi-line format.

---

### AccessToken name rejected by admission policy

**Symptoms**

```
The accesstokens "token-user1" is invalid: ValidatingAdmissionPolicy 'accesstoken-naming-policy'
denied request: AccessToken name must be 'token-<your-username>'
```

**Cause**

A ValidatingAdmissionPolicy enforces that the AccessToken name must match `token-<your-username>`. This prevents students from accidentally overwriting each other's tokens. The policy checks the authenticated username from the request.

**Resolution**

- Ensure you are logged in as the correct user (`oc whoami`).
- Ensure the token name matches `token-<your-username>` (e.g. `user3` must create `token-user3`).
- Admins cannot create tokens on behalf of students unless the policy binding is temporarily removed.

---

### Skupper controller has `certificates already exists` errors

**Symptoms**

Controller logs show errors like:

```
Error configuring site: certificates.skupper.io "skupper-site-ca" already exists
Error ensuring SecuredAccess for RouterAccess: securedaccesses.skupper.io "skupper-router" already exists
```

Sites appear `Ready` but Links are never created after AccessToken redemption.

**Cause**

Stale Skupper internal resources (Certificates, SecuredAccesses) survive across Site delete/recreate cycles. The controller tries to create them during site recovery but they already exist, leaving the controller in a partially broken state.

**Resolution**

Full teardown — delete all Sites, wait for internal resources to be cleaned up, then restart the controller:

```bash
# Delete all sites
oc delete site user1-site -n user1-devspaces
oc delete site database-site -n shared-database

# Wait for internal resources to clean up
sleep 15
oc get certificates.skupper.io,securedaccesses.skupper.io -n shared-database
oc get certificates.skupper.io,securedaccesses.skupper.io -n user1-devspaces
# Both should show "No resources found"

# Restart the controller
oc delete pod -l app.kubernetes.io/part-of=skupper -n openshift-operators

# Wait for the controller to restart, then recreate sites
```

---

### Link stuck at `Not Operational` despite active router connections

**Symptoms**

```
$ oc get link token-user1 -n shared-database
NAME          STATUS    REMOTE SITE   MESSAGE
token-user1   Pending                 Not Operational
```

The router data plane is connected (verifiable via `oc exec` into the router pod and running `skstat -c`), inter-router connections show TLSv1.3 with computed next hops, but the Link CR never transitions to Ready. Listeners show `No matching connectors`. TCP connectivity through the network actually works.

**Cause**

The `kube-adaptor` sidecar in the `skupper-router` pod manages a leader lease (`skupper-site-leader`). If the lease is lost due to a transient infrastructure issue (e.g., etcd timeout), the kube-adaptor re-acquires the lease but may fail to restart the site event controller. This failure is not retried — the site controller stays down permanently. The local site stops appearing in the `skupper-network-status` ConfigMap, so the controller never marks Links as Ready.

**Diagnosis**

Check the kube-adaptor logs for a failed site controller restart:

```bash
oc logs -n shared-database deployment/skupper-router -c kube-adaptor | grep -i "failed\|lost leader\|site event"
```

Look for the pattern:
```
COLLECTOR: Lost leader lock after ...
COLLECTOR: Became leader. Starting status sync and site controller after ...
COLLECTOR: Failed to start controller for emitting site events: ...
```

Also check the `skupper-network-status` ConfigMap — if the local site is missing, this is the issue:

```bash
oc get configmap skupper-network-status -n shared-database -o jsonpath='{.data.NetworkStatus}' | jq '.siteStatus[].site.name'
```

**Resolution**

Delete the `skupper-router` pod in the affected namespace. The Deployment recreates it and the kube-adaptor starts cleanly:

```bash
oc delete pod -n shared-database -l app.kubernetes.io/part-of=skupper
oc wait --for=condition=Ready pod -l app.kubernetes.io/part-of=skupper -n shared-database --timeout=120s
```

Allow 30 seconds for the network status to fully reconcile, then verify:

```bash
oc get link -n shared-database
oc get listener -n user1-devspaces
```

---

### AccessToken redemption fails with `EOF` after controller restart

**Symptoms**

```
$ oc get accesstoken token-user1 -n shared-database
NAME          REDEEMED   STATUS   MESSAGE
token-user1              Error    Controller got error: Post "https://skupper-grant-server-...:443/...": EOF
```

No Link is created. The grant server route returns HTTP 000 (connection refused).

**Cause**

The `skupper-grant-server` Service selector includes the `pod-template-hash` label. This label is unique per ReplicaSet. If the Skupper controller Deployment is restarted via `oc rollout restart` (which creates a new ReplicaSet), the new pod gets a different hash. The controller reconciles the Service selector with the **old** hash from its previous state, causing a mismatch. The Service has no endpoints and the grant server becomes unreachable.

**Diagnosis**

Compare the pod hash with the service selector hash:

```bash
# Pod hash
oc get pod -n openshift-operators -l app.kubernetes.io/name=skupper-controller \
  -o jsonpath='{.items[0].metadata.labels.pod-template-hash}'

# Service selector hash
oc get svc skupper-grant-server -n openshift-operators \
  -o jsonpath='{.spec.selector.pod-template-hash}'

# Check endpoints
oc get endpoints skupper-grant-server -n openshift-operators
```

If the hashes differ and endpoints show `<none>`, this is the issue.

**Resolution**

Delete the controller pod directly (do **not** use `oc rollout restart`):

```bash
oc delete pod -n openshift-operators -l app.kubernetes.io/name=skupper-controller
```

This creates a new pod within the same ReplicaSet, preserving the hash. The controller reconciles the Service selector correctly on startup.

**Prevention**

Never use `oc rollout restart` on the Skupper controller Deployment. Always use `oc delete pod` to restart the controller.

---

## Shared Database

### PostgreSQL init script not running

**Symptoms**

The database starts but per-user schemas, roles, and data are missing.

**Cause**

The Red Hat PostgreSQL 16 image (`registry.redhat.io/rhel9/postgresql-16`) only executes `.sh` files from `/opt/app-root/src/postgresql-init/`. SQL files (`.sql`) are ignored. Additionally, init scripts run **before** the container creates the `POSTGRESQL_DATABASE` and `POSTGRESQL_USER`, so the target database does not exist when the script runs.

**Resolution**

- The init script must be a `.sh` file (not `.sql`)
- It must connect to the `postgres` database first to create the target database and admin user
- Per-user schemas are then created by connecting to the target database

See `templates/shared-db-init.sh.j2` for the correct implementation.

---

### Database crash: `role "dbadmin" does not exist`

**Symptoms**

PostgreSQL pod crashes with:

```
ERROR: role "dbadmin" does not exist
```

**Cause**

The init script tries to connect to the target database using `psql -U postgres -d ${POSTGRESQL_DATABASE}`, but the database doesn't exist yet during the init phase. Init scripts run before the container creates `POSTGRESQL_DATABASE` and `POSTGRESQL_USER`.

**Resolution**

The init script must connect to the `postgres` database first, create the target database and admin role, then connect to the target database for schema creation. See `templates/shared-db-init.sh.j2`.

---

## OpenShift Console & RBAC

### Student cannot see `shared-database` namespace

**Symptoms**

`oc projects` does not list `shared-database`. The OpenShift console does not show the namespace in the namespace picker.

**Cause**

The custom `shared-db-viewer` Role grants permissions inside the namespace, but OpenShift's project discovery also needs the user to have `get` permission on the Namespace resource itself.

**Resolution**

A ClusterRole and ClusterRoleBinding should exist to grant namespace visibility:

```bash
oc get clusterrole shared-db-namespace-viewer
oc get clusterrolebinding shared-db-namespace-viewer
```

If missing, re-run provisioning or create them manually:

```bash
cat <<EOF | oc apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: shared-db-namespace-viewer
rules:
  - apiGroups: [""]
    resources: ["namespaces"]
    resourceNames: ["shared-database"]
    verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: shared-db-namespace-viewer
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: shared-db-namespace-viewer
subjects:
  - apiGroup: rbac.authorization.k8s.io
    kind: Group
    name: system:authenticated
EOF
```

---

### Console warning: `clusterserviceversions is forbidden`

**Symptoms**

The OpenShift console shows a warning when viewing `shared-database` under the Operators section:

```
clusterserviceversions.operators.coreos.com is forbidden: User "user1" cannot list resource
"clusterserviceversions" in API group "operators.coreos.com" in the namespace "shared-database"
```

**Cause**

The custom `shared-db-viewer` Role is missing read permissions for ClusterServiceVersions, which the console's operator view requires.

**Resolution**

The `shared-db-viewer` Role should include:

```yaml
- apiGroups: ["operators.coreos.com"]
  resources: ["clusterserviceversions"]
  verbs: ["get", "list", "watch"]
```

This is included in the current provisioning scripts. If missing, update the Role manually or re-run provisioning.

---

### Students can see each other's AccessTokens

**Symptoms**

`user2` can run `oc get accesstoken token-user1 -n shared-database` and see the full contents including `url`, `code`, and `ca`.

**Cause**

The `view` ClusterRole grants broad read access to all resources including Skupper CRDs. This was replaced with a custom `shared-db-viewer` Role, but if the old RoleBindings still reference the `view` ClusterRole, students retain full read access.

**Resolution**

Verify the RoleBindings reference the custom Role, not the `view` ClusterRole:

```bash
oc get rolebinding -n shared-database -o custom-columns=NAME:.metadata.name,ROLE:.roleRef.name | grep view
```

Expected output should show `shared-db-viewer`, not `view`. If incorrect, delete the old RoleBinding (you cannot change `roleRef` in place) and recreate it:

```bash
oc delete rolebinding user1-view -n shared-database
# Then re-run provisioning or create manually referencing shared-db-viewer
```

---

## Showroom / Documentation

### Username not showing in documentation pages

**Symptoms**

The `{username}` attribute in the documentation renders as blank or literal text instead of the logged-in user's name.

**Cause**

Showroom loads content in an iframe. If the iframe points to the Showroom route (different origin), the username cookie set on the `docs` proxy domain is not accessible to the JavaScript inside the iframe due to same-origin policy.

**Resolution**

The nginx proxy must use `sub_filter` to rewrite the iframe `src` from the full Showroom URL to a relative path. This keeps everything on the same origin so the cookie is accessible:

```nginx
sub_filter_once off;
sub_filter_types text/html;
sub_filter 'src="https://showroom-<namespace>.<domain>/' 'src="/';
```

Also ensure the Showroom public route has been deleted — all access must go through the `docs` proxy route.
