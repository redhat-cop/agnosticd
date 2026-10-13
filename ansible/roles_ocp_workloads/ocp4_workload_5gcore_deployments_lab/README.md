# Deploying 5G Core Deployments on OpenShift Lab

## Overview

The `ocp4_workload_5gcore_deployments_lab` Ansible role automates the preparation of a 5G Core lab environment on OpenShift. This lab provides **1 Hub cluster** and prepares **12 VMs** for a single **MNO (Multi Node OpenShift) cluster** (3 master nodes + 9 worker nodes in 3 failure domains). The role does **not** deploy the MNO cluster automatically; it prepares the Hub, ArgoCD, and infrastructure so you can deploy the MNO using **ClusterInstance** and **PolicyGenerators** from the 5g-core-deployments-on-ocp-lab repository.

## What This Lab Prepares

- **Hub Cluster**: Full OpenShift cluster with Multi-Cluster Management and ArgoCD.
- **MNO VMs**: 3 masters (`ocp-mno-master-00`–`02`) and 9 workers (`ocp-mno-worker-00`–`02`, `10`–`12`, `20`–`22`) in 3 failure domains (3 workers per MCP).
- **Infrastructure**: Gitea, container registry (pre-populated with OCP 4.18/4.19/4.20 and telco core RDS operators via oc-mirror), web cache, dnsmasq, and MinIO. **MinIO is enabled by default** to provide S3 storage for RHACM multi-cluster observability.
- **Lab content**: Materials from `alosadagrande/5g-core-deployments-on-ocp-lab` (branch/tag `main`).

## Prerequisites

### System Requirements

| Resource     | Minimum | Recommended |
|-------------|---------|-------------|
| **Memory**  | 128 GB  | 200+ GB     |
| **CPUs**    | 64 cores| 96+ cores   |
| **Storage** | 500 GB  | 1 TB+       |
| **OS**      | RHEL 9  | RHEL 9      |

### Required Software (installed by the role)

- kcli, Podman, Ansible, OpenShift CLI tools (oc, kubectl, openshift-installer).

## Quick Start

### 1. Prepare environment

```bash
sudo dnf update -y
sudo dnf install -y git ansible-core
# Clone agnosticd (or your playbook repo)
cd /path/to/agnosticd
```

### 2. Inventory

Create an inventory with your hypervisor:

```yaml
all:
  children:
    hypervisors:
      hosts:
        your-hypervisor-ip:
          ansible_user: root
          ansible_ssh_private_key_file: /path/to/your/ssh/key
```

### 3. Pull secret

Get an OpenShift pull secret from [console.redhat.com](https://console.redhat.com) and pass it at run time.

### 4. Run the role

```bash
ansible-playbook -i inventory run-role.yml -e "ocp4_pull_secret='$(cat pull-secret.json)'"
```

With custom variables:

```bash
ansible-playbook -i inventory run-role.yml \
  -e "ocp4_pull_secret='$(cat pull-secret.json)'" \
  -e "student_name=myuser" \
  -e "lab_version=main"
```

## Configuration Variables

### Essential

| Variable            | Default        | Description                    |
|---------------------|----------------|--------------------------------|
| `student_name`      | `lab-user`     | Lab user name                  |
| `student_password`  | (set at runtime)| Lab user password             |
| `ocp4_pull_secret`  | Required       | OpenShift pull secret JSON     |
| `hypervisor_min_memory_mb` | `204800` | Min hypervisor RAM (MB)  |
| `hypervisor_min_cpus`      | `64`     | Min hypervisor CPUs     |

### Lab and repo (5G Core)

| Variable      | Default        | Description                          |
|---------------|----------------|--------------------------------------|
| `lab_version` | `main`         | Branch/tag of lab repo               |
| `repo_user`   | `alosadagrande`| GitHub user for lab repo             |
| `lab_repo`    | 5g-core-deployments-on-ocp-lab | Lab Git URL (derived)     |
| `lab_release` | `4.20`         | Used for kcli RPM URL if needed      |

### Hub VM

| Variable             | Default | Description           |
|----------------------|---------|-----------------------|
| `lab_hub_vm_cpus`    | `16`    | Hub VM CPUs           |
| `lab_hub_vm_memory`  | `48000` | Hub VM memory (MB)    |
| `lab_hub_vm_disk`    | `200`   | Hub VM disk (GB)      |

### MNO VMs (3 masters + 9 workers)

| Variable                     | Default | Description                    |
|-----------------------------|---------|--------------------------------|
| `lab_mno_master_count`      | `3`     | Number of master VMs          |
| `lab_mno_worker_count`      | `9`     | Number of worker VMs           |
| `lab_mno_failure_domains`   | `3`     | Failure domains (3 workers each)|
| `lab_mno_master_vm_cpus`    | `12`    | CPUs per master VM            |
| `lab_mno_master_vm_memory`   | `16384` | Memory per master (MB)        |
| `lab_mno_master_vm_disk`    | `120`   | Disk per master (GB)          |
| `lab_mno_worker_vm_cpus`    | `12`    | CPUs per worker VM            |
| `lab_mno_worker_vm_memory`  | `16384` | Memory per worker (MB)        |
| `lab_mno_worker_vm_disk`    | `120`   | Root disk per worker (GB)     |
| `lab_mno_worker_vm_extra_disk` | `120` | Extra disk per worker for ODF (GB) |

### Feature toggles

| Variable                    | Default | Description                                                                 |
|-----------------------------|---------|-----------------------------------------------------------------------------|
| `lab_deploy_minio`          | `true`  | Deploy MinIO for RHACM multi-cluster observability S3 storage               |
| `install_lab_dependencies`  | `false` | Install extra lab tools                                                     |
| `download_rhcos_isos`       | `false` | Download RHCOS images                                                       |
| `extra_disk_libvirt_images` | `true`  | Use extra disk for libvirt                                                  |

### Disconnected registry mirroring (oc-mirror)

| Variable               | Default                        | Description                                                                 |
|------------------------|--------------------------------|-----------------------------------------------------------------------------|
| `run_oc_mirror`        | `true`                         | Run oc-mirror to populate the local registry; set `false` if registry is pre-populated |
| `oc_mirror_timeout`    | `7200`                         | Async timeout in seconds for the oc-mirror run (2h default)                 |
| `imageset_config_file` | `imageset-mirror-core.yaml`    | ImageSetConfiguration file downloaded from the lab repo                     |
| `disconnected_update`  | `false`                        | Keep `false`; oc-mirror handles registry population (kcli does not mirror)  |

## Deployment Process

### Phase 1: Pre-workload

- System validation, storage, kcli, Podman, dnsmasq, registry, Gitea, web cache.
- **oc-mirror**: downloads `imageset-mirror-core.yaml` from the lab repo and runs `oc-mirror` (async, up to 2h) to populate the local registry with OCP 4.18, 4.19, and 4.20 releases plus all required RDS Core operator indexes. Skippable via `run_oc_mirror: false`.
- MinIO deployed by default (`lab_deploy_minio: true`) for RHACM multi-cluster observability S3 storage.
- Creation of **12 MNO VMs**: 3 masters, 9 workers (hostnames and MACs as per plan).
- Lab materials from `5g-core-deployments-on-ocp-lab` (dnsmasq, forcedns, webcache, hub.yml, showroom).

### Phase 2: Workload (Hub only)

- Hub cluster deployment using the local disconnected registry pre-populated by oc-mirror (`disconnected_update: false`; kcli does not perform its own mirroring).
- ArgoCD setup, hub operators, Multi-Cluster Hub/Engine.
- **No** automatic MNO cluster deployment.
- After workload, the role finishes with Hub and ArgoCD ready; you deploy the MNO using **ClusterInstance** and **PolicyGenerators** from the lab repo.

### Phase 3: Your MNO deployment

- Use the 5g-core-deployments-on-ocp-lab repository (ClusterInstance, PolicyGenerators; no SiteConfig/PolicyGenTemplates in this role).
- Install the MNO cluster on the prepared VMs following the lab documentation.

## Post-deployment

### Access

- **Hub kubeconfig**: e.g. `kcli scp hub:/root/.kcli/clusters/hub/auth/kubeconfig ./hub-kubeconfig`
- **ArgoCD**: URL per lab (e.g. `https://argocd.5g-deployment.lab`), credentials per ArgoCD docs.
- **Gitea**: e.g. `http://infra.5g-deployment.lab:3000`
- **MinIO**: deployed by default; accessible for RHACM observability. Disable with `lab_deploy_minio: false`.

### MNO VM hostnames (OpenShift node names)

- Masters: `ocp-mno-master-00`, `ocp-mno-master-01`, `ocp-mno-master-02`
- Workers (MCP 0): `ocp-mno-worker-00`, `ocp-mno-worker-01`, `ocp-mno-worker-02`
- Workers (MCP 1): `ocp-mno-worker-10`, `ocp-mno-worker-11`, `ocp-mno-worker-12`
- Workers (MCP 2): `ocp-mno-worker-20`, `ocp-mno-worker-21`, `ocp-mno-worker-22`

## Cleanup

The role’s remove_workload logic uses `kcli delete plan hub --yes`, which removes the hub plan and all VMs created under it (Hub + 12 MNO VMs). Optional MinIO service is stopped only if `lab_deploy_minio` was true.

## Disconnected Registry Mirroring

The role uses **oc-mirror** to populate the local container registry before Hub deployment. This ensures a fully disconnected environment where the Hub (and later the MNO) can pull all required images from `infra.5g-deployment.lab:8443` without internet access at install time.

### How it works

1. `pre_workload.yml` starts the local podman registry (port 8443) and configures its certificate.
2. The `imageset-mirror-core.yaml` ImageSetConfiguration is downloaded from the lab repo.
3. `oc-mirror` runs asynchronously (default timeout: 2h) targeting `docker://infra.5g-deployment.lab:8443`, mirroring:
   - OCP releases 4.18, 4.19, and 4.20
   - All operator indexes required for the 5G Core RDS stack (ODF, NMState, SR-IOV, PTP, MetalLB, Numaresources, Logging, PerformanceProfile/SCTP)
4. The resulting IDMS/ITMS manifests are applied on the hypervisor.
5. `workload.yml` deploys the Hub using this pre-populated registry (`disconnected_update: false`; kcli does not perform its own image mirroring).

### Key variables

| Variable               | Default                     | Notes                                              |
|------------------------|-----------------------------|----------------------------------------------------|
| `run_oc_mirror`        | `true`                      | Set `false` to skip if registry is pre-populated   |
| `oc_mirror_timeout`    | `7200`                      | Increase for slow connections                      |
| `imageset_config_file` | `imageset-mirror-core.yaml` | Stored in `lab-materials/lab-env-data/registry/`   |
| `disconnected_update`  | `false`                     | oc-mirror handles mirroring; kcli does not         |

## Support and resources

- **Lab repo**: [alosadagrande/5g-core-deployments-on-ocp-lab](https://github.com/alosadagrande/5g-core-deployments-on-ocp-lab)
- **Lab version**: `main` (configurable via `lab_version`)
- **OpenShift**: [Red Hat OpenShift](https://docs.openshift.com/)

For variable details, see `VARIABLES_OVERVIEW.md`. For task breakdowns, see `PRE_WORKLOAD_OVERVIEW.md` and `WORKLOAD_OVERVIEW.md`.
