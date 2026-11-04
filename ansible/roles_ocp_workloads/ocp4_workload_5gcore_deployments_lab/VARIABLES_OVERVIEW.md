# Important Variables (5G Core Lab)

The `defaults/main.yml` for **ocp4_workload_5gcore_deployments_lab** defines configuration for the 5G Core lab: 1 Hub + 12 MNO VMs (3 masters, 9 workers in 3 failure domains). The MNO cluster is **not** deployed by the role; you deploy it with **ClusterInstance** and **PolicyGenerators** following the lab instructions.

## Essential (often set at runtime)

- **ocp4_pull_secret**: OpenShift pull secret JSON (required; not in defaults).
- **student_name**: e.g. `lab-user`.
- **student_password**: Lab user password (recommended at runtime).

## Lab repository and version (5G Core)

| Variable     | Default          | Description                    |
|-------------|------------------|--------------------------------|
| `lab_version` | `"main"`       | Branch/tag of lab repo         |
| `repo_user`   | `"RHsyseng"` | GitHub user for lab repo     |
| `lab_repo`    | `https://github.com/{{ repo_user }}/5g-core-deployments-on-ocp-lab.git` | Lab Git URL |
| `lab_release` | `"4.20"`       | Used for lab material          |
| `lab_url`     | Labs URL for 5G Core | Documentation link        |

## Hub VM

| Variable                | Default | Description        |
|-------------------------|---------|--------------------|
| `lab_hub_vm_cpus`       | `16`    | Hub CPU cores      |
| `lab_hub_vm_memory`     | `48000` | Hub memory (MB)    |
| `lab_hub_vm_disk`       | `200`   | Hub disk (GB)      |

## MNO VMs (3 masters + 9 workers, 3 failure domains)

| Variable                       | Default | Description                     |
|--------------------------------|---------|---------------------------------|
| `lab_mno_master_count`         | `3`     | Number of master VMs            |
| `lab_mno_worker_count`         | `9`     | Number of worker VMs             |
| `lab_mno_failure_domains`      | `3`     | Failure domains (3 workers each)|
| `lab_mno_master_vm_cpus`       | `12`    | CPUs per master                 |
| `lab_mno_master_vm_memory`     | `16384` | Memory per master (MB)          |
| `lab_mno_master_vm_disk`       | `120`   | Disk per master (GB)            |
| `lab_mno_worker_vm_cpus`       | `12`    | CPUs per worker                 |
| `lab_mno_worker_vm_memory`     | `16384` | Memory per worker (MB)          |
| `lab_mno_worker_vm_disk`       | `120`   | Root disk per worker (GB)       |
| `lab_mno_worker_vm_extra_disk` | `120`   | Extra disk per worker for ODF (GB) |

## MinIO (enabled by default – RHACM observability)

| Variable          | Default | Description                                                                  |
|-------------------|---------|------------------------------------------------------------------------------|
| `lab_deploy_minio` | `true` | Deploy MinIO for RHACM multi-cluster observability S3 storage (enabled by default) |

## Registry mirroring (oc-mirror)

| Variable               | Default                     | Description                                                                      |
|------------------------|-----------------------------|----------------------------------------------------------------------------------|
| `run_oc_mirror`        | `true`                      | Run oc-mirror in pre_workload to populate the local registry; set `false` to skip if already pre-populated |
| `oc_mirror_timeout`    | `7200`                      | Async timeout in seconds for the oc-mirror run (2h default; increase for slow connections) |
| `imageset_config_file` | `imageset-mirror-core.yaml` | ImageSetConfiguration downloaded from `lab-materials/lab-env-data/registry/` in the lab repo |

## Network and services

- `lab_network_cidr`, `lab_network_domain`, `lab_sriov_cidr`, `lab_ptp_cidr`, `lab_registry_host`, `lab_api_host`, `upstream_dns` (same idea as RAN; values in defaults).

## Hypervisor and optional features

- `hypervisor_min_memory_mb`, `hypervisor_min_cpus`, `hypervisor_supported_distributions`
- `install_lab_dependencies`, `download_rhcos_isos`, `extra_disk_libvirt_images`
- `disconnected_update` (default: `false`): keep `false`; oc-mirror handles registry population in pre_workload. Setting to `true` would instruct kcli to mirror the Hub release and operators itself, which is not the intended flow for this lab.
- OpenShift and RHCOS image variables (`ocp4_major_release`, `ocp4_minor_release`, `rhcos_*`).

## Override examples

```bash
# Command line
ansible-playbook -i inventory run-role.yml \
  -e "ocp4_pull_secret='$(cat pull-secret.json)'" \
  -e "lab_version=main" \
  -e "repo_user=alosadagrande"
```

```yaml
# Inventory or group_vars
lab_version: "main"
repo_user: "alosadagrande"
lab_mno_worker_vm_extra_disk: 120
run_oc_mirror: false  # set false only if registry is already pre-populated
```

## Notes

1. **Pull secret** must be provided at runtime.
2. **MNO cluster** is not deployed by this role; use the lab repo’s ClusterInstance and PolicyGenerators.
3. **MinIO** is enabled by default for RHACM multi-cluster observability S3 storage; set `lab_deploy_minio: false` to skip it.
4. **kcli_rpm** defaults to the 5g-core repo releases; if no asset exists, override with a working URL (e.g. from the RAN repo).
