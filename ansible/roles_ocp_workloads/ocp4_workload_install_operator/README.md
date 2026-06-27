# ocp4_workload_install_operator

## Overview

Generic workload wrapper for the `install_operator` role. Allows catalog items to install any OpenShift operator using the standard workload pattern.

This workload is a thin wrapper that:
1. Maps `ocp4_workload_install_operator_*` variables to `install_operator_*` role variables
2. Calls the shared `install_operator` role
3. Waits for CSV to reach Succeeded status before completing
4. Supports operator removal via ACTION=remove

## Use Cases

- Installing AAP operator for lab environments
- Installing RHACM operator for multi-cluster management
- Installing any operator from OperatorHub or custom catalogs
- Creating catalog items that need operator dependencies

## Requirements

- OpenShift cluster with OLM (Operator Lifecycle Manager)
- Cluster admin permissions (for operator installation)
- Access to operator catalog (redhat-operators, community-operators, or custom)

## Role Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ocp4_workload_install_operator_name` | Name of operator (must match PackageManifest) | `ansible-automation-platform-operator` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ocp4_workload_install_operator_namespace` | `openshift-operators` | Namespace to install operator |
| `ocp4_workload_install_operator_catalog` | `redhat-operators` | Catalog source name |
| `ocp4_workload_install_operator_channel` | `""` (auto-detect) | Operator channel |
| `ocp4_workload_install_operator_starting_csv` | `""` (latest) | Pin to specific CSV version |
| `ocp4_workload_install_operator_automatic_install_plan_approval` | `true` | Auto-approve InstallPlans |
| `ocp4_workload_install_operator_manage_namespaces` | `[]` (all) | Namespaces for operator to watch |

See [defaults/main.yml](defaults/main.yml) for complete variable list.

## Example Usage

### AAP Operator Installation

```yaml
# In catalog item common.yaml
post_software_workloads:
  localhost:
    - ocp4_workload_install_operator

# Variables
ocp4_workload_install_operator_name: ansible-automation-platform-operator
ocp4_workload_install_operator_namespace: "{{ sandbox_openshift_namespace }}"
ocp4_workload_install_operator_catalog: redhat-operators
ocp4_workload_install_operator_channel: stable-2.7
ocp4_workload_install_operator_starting_csv: aap-operator.v2.7.0-0.1781768237
ocp4_workload_install_operator_manage_namespaces:
  - "{{ sandbox_openshift_namespace }}"
```

### RHACM Operator Installation

```yaml
ocp4_workload_install_operator_name: advanced-cluster-management
ocp4_workload_install_operator_namespace: open-cluster-management
ocp4_workload_install_operator_channel: release-2.11
ocp4_workload_install_operator_manage_namespaces:
  - open-cluster-management
```

### GitOps Operator Installation

```yaml
ocp4_workload_install_operator_name: openshift-gitops-operator
ocp4_workload_install_operator_namespace: openshift-gitops-operator
ocp4_workload_install_operator_channel: latest
ocp4_workload_install_operator_manage_namespaces: []  # Cluster-scoped
```

## Integration with Other Workloads

This workload is designed to run **before** workloads that deploy operator-managed applications:

```yaml
post_software_workloads:
  localhost:
    # Step 1: Install operator
    - ocp4_workload_install_operator
    
    # Step 2: Deploy application via Helm/manifests
    - ocp4_workload_helm_from_content_repo
```

## Wait Logic

The workload waits for:
1. InstallPlan creation (up to 100 retries × 10s = ~16 minutes)
2. CSV name resolution (up to 30 retries × 10s = 5 minutes)
3. CSV Succeeded status (up to 10 retries × 30s = 5 minutes)

Total maximum wait: ~26 minutes  
Typical AAP operator: ~20 seconds

## Operator Removal

Set `ACTION: remove` to uninstall the operator:

```yaml
remove_workloads:
  - ocp4_workload_install_operator
```

## Comparison to Direct Role Usage

**Before** (each workload duplicates operator logic):
```yaml
- name: Install operator
  ansible.builtin.include_role:
    name: install_operator
  vars:
    install_operator_name: my-operator
    install_operator_namespace: my-namespace
    # ... 20+ variable mappings ...
```

**After** (catalog item uses standard workload):
```yaml
post_software_workloads:
  localhost:
    - ocp4_workload_install_operator

ocp4_workload_install_operator_name: my-operator
ocp4_workload_install_operator_namespace: my-namespace
```

## Benefits

1. **Modularity**: Reusable across all catalog items needing operators
2. **Consistency**: Standard variable naming (`ocp4_workload_*` prefix)
3. **Simplicity**: Catalog items declare what, not how
4. **Maintainability**: Operator logic lives in one shared role
5. **AgnosticV compliance**: Follows workload patterns for validation

## Dependencies

- Role: `install_operator` (ansible/roles/install_operator/)
- Collection: `kubernetes.core`

## Author

RHDP Team
