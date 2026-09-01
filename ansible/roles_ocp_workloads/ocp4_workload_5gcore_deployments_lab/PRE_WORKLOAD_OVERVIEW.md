# Pre-Workload Tasks Overview (5G Core Lab)

The `pre_workload.yml` file contains the initial setup and preparation tasks for the **5G Core** lab environment. It configures the hypervisor with dependencies, services, and **12 MNO VMs** (3 masters + 9 workers in 3 failure domains). Lab materials are taken from the **5g-core-deployments-on-ocp-lab** repository.

## What Pre-Workload Does

### 1. System Validation & Requirements
- Validates pull secret and system resources (memory, CPU, OS).
- Ensures RHEL 9 / CentOS 9 / Fedora.

### 2. Storage Configuration
- Extra disk for libvirt, XFS, mount at `/var/lib/libvirt`, kcli storage pools.

### 3. Dependency Installation
- libvirt, qemu-kvm, podman, dnsmasq, Python modules, OpenShift tools (oc, kubectl, openshift-installer), kcli.

### 4. Network Infrastructure
- Lab networks (main, SR-IOV, PTP), DNSMasq, NetworkManager, firewall.
- **DNS (dnsmasq)**: Files from 5g-core repo for **hub**, **infrastructure-host**, and **mno** (one file per context, e.g. `mno.ipv4` for MNO nodes).

### 5. Container Registry
- Podman registry on port 8443, auth, SSL, systemd service.

#### 5b. OCP Release and Operator Mirroring (oc-mirror)
- Runs immediately after the registry is up and its certificate is trusted.
- Downloads `imageset-mirror-core.yaml` (ImageSetConfiguration) from the lab repo (`lab-materials/lab-env-data/registry/`).
- Executes a single **`oc-mirror`** run (async, configurable timeout via `oc_mirror_timeout`, default 7200s / 2h) targeting `docker://infra.5g-deployment.lab:8443`, mirroring:
  - OCP releases **4.18**, **4.19**, and **4.20**
  - All operator indexes for the 5G Core RDS stack: ODF, NMState, SR-IOV, PTP, MetalLB, Numaresources, Logging, PerformanceProfile/SCTP
- Applies the resulting **IDMS/ITMS** manifests on the hypervisor so they are available for both Hub installation and future MNO deployment.
- **Toggle**: set `run_oc_mirror: false` to skip this block when the registry is already pre-populated.

### 6. S3 Storage (MinIO)
- **Enabled by default** (`lab_deploy_minio: true`). MinIO is required to provide S3 storage for **RHACM multi-cluster observability** on the Hub. Disable with `lab_deploy_minio: false` if not needed.
- When enabled: MinIO on port 9002, buckets, `mc` client.

### 7. Git Server (Gitea)
- Gitea on port 3000, admin user, **migration of 5g-core-deployments-on-ocp-lab** from GitHub.

### 8. Web Cache
- Web cache service, RHCOS downloads (if enabled).

### 9. Redfish (ksushy)
- ksushy on port 9000 for BMC simulation. Sushy check uses **ocp-mno-master-00** (first MNO master).

### 10. Lab VM Preparation (5G Core topology)
- **Hub VM**: Same as RAN (e.g. 16 CPU, 48GB RAM, 200GB disk).
- **MNO VMs** (all created with plan=hub):
  - **3 masters**: `ocp-mno-master-00`, `ocp-mno-master-01`, `ocp-mno-master-02` (12 CPU, 16GB RAM, 120GB disk each).
  - **9 workers**: `ocp-mno-worker-00`–`02`, `ocp-mno-worker-10`–`12`, `ocp-mno-worker-20`–`22` (12 CPU, 16GB RAM, 120GB + **120GB extra disk for ODF** each).
- MACs and UUIDs follow the 5G Core lab plan (e.g. aa:aa:aa:aa:02:01 … 02:12).

### 11. Lab Content
- Clone/cache of **5g-core-deployments-on-ocp-lab**, showroom, Apache/Wetty/Firefox/Traefik as in lab.

### 12. User Account
- Lab user, SSH keys, Git config, credentials.

## Key Services

| Service           | Port | Purpose              | Notes                    |
|-------------------|------|----------------------|--------------------------|
| Container Registry| 8443 | OpenShift images (oc-mirror) | Always                                        |
| Gitea             | 3000 | Lab repo (5G Core)           | Always                                        |
| MinIO             | 9002 | S3 for RHACM observability   | Always (default); disable with `lab_deploy_minio: false` |
| Web Cache         | 8080 | Image caching                | Always                                        |
| Redfish (ksushy)  | 9000 | BMC simulation               | Always                                        |
| Lab Showroom      | 80   | Lab docs                     | Always                                        |

## Network

- Main: 192.168.125.0/24 (e.g. 5g-deployment.lab).
- SR-IOV: 192.168.100.0/24, PTP: 192.168.200.0/24.
- DNS: dnsmasq with hub, infrastructure-host, and **mno** entries from repo.

## What Happens After Pre-Workload

- Hub cluster can be deployed.
- **MNO cluster is not deployed by this role**; the 12 MNO VMs are created and ready for you to deploy the MNO using **ClusterInstance** and **PolicyGenerators** from the 5g-core-deployments-on-ocp-lab repo.
- Operators (ODF, NMState, SR-IOV, PTP, MetalLB, Numaresources, Logging, etc.) are installed on the MNO per the lab repo, not by this role’s workload phase.

## Troubleshooting

- Ensure minimum memory/CPU, valid pull secret, and enough disk.
- If the 5g-core repo uses different dnsmasq file names (e.g. one file per node), adjust the `get_url` list in `pre_workload.yml` for `lab-materials/lab-env-data/dnsmasq/` accordingly.
- **kcli_rpm**: Default points to `alosadagrande/5g-core-deployments-on-ocp-lab` releases; if no release exists, override with a working RPM URL (e.g. from the RAN repo).
