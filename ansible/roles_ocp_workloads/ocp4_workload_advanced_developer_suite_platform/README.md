# ocp4_workload_advanced_developer_suite_platform

## Description

Platform-only infrastructure deployment for Red Hat Advanced Developer Suite (ADS) / Trusted Application Pipeline (TAP).

This role deploys all platform components **without** user provisioning:
- Red Hat Developer Hub (RHDH) with orchestrator plugins
- GitLab with development group
- Keycloak with realms and groups
- Advanced Cluster Security (ACS)
- Jenkins
- OpenShift GitOps (Argo CD)
- OpenShift DevSpaces
- Quay Registry
- Trusted Profile Analyzer (TPA)
- Orchestrator workflows

## Purpose

This role provides **clear separation** between infrastructure and student provisioning:
- **Platform Role** (this role): Deploy infrastructure once (~20-30 minutes)
- **Students Role** (`ocp4_workload_advanced_developer_suite_students`): Provision users on-demand (~2-5 minutes per user)

## Architecture

```
┌─────────────────────────────────────────────┐
│   Platform Role (One-Time Deployment)      │
├─────────────────────────────────────────────┤
│ • Operators & Platform Components          │
│ • Keycloak Realms/Groups (no users)        │
│ • GitLab Groups (no user membership)       │
│ • RHDH + Orchestrator                      │
│ • ACS, Jenkins, GitOps, DevSpaces          │
│ • Admin user creation                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Students Role (On-Demand Provisioning)   │
├─────────────────────────────────────────────┤
│ • Loop over num_users                      │
│ • Create Keycloak users                    │
│ • Add users to GitLab groups               │
│ • Deploy per-user showroom instances       │
│ • Report user credentials                  │
└─────────────────────────────────────────────┘
```

## Role Variables

### Required Variables

```yaml
# Common password for admin accounts
common_password: "password"

# GUID for resource naming
guid: "unique-guid"
```

### Platform Configuration

```yaml
# TSSC CLI Configuration
ocp4_workload_advanced_developer_suite_tssc_cli_repo: https://github.com/redhat-appstudio/rhtap-cli
ocp4_workload_advanced_developer_suite_tssc_cli_revision: release-1.6

# Namespace Configuration
ocp4_workload_advanced_developer_suite_keycloak_namespace: tssc-keycloak
ocp4_workload_advanced_developer_suite_dh_namespace: tssc-dh
ocp4_workload_advanced_developer_suite_gitlab_namespace: gitlab
ocp4_workload_advanced_developer_suite_jenkins_namespace: jenkins
ocp4_workload_advanced_developer_suite_acs_namespace: tssc-acs
ocp4_workload_advanced_developer_suite_tssc_gitops_namespace: tssc-gitops
ocp4_workload_advanced_developer_suite_tssc_tpa_namespace: tssc-tpa

# Admin User
ocp4_workload_advanced_developer_suite_admin_user: admin
ocp4_workload_advanced_developer_suite_admin_password: password
ocp4_workload_advanced_developer_suite_remove_kubeadmin: true

# Orchestrator Configuration
ocp4_workload_advanced_developer_suite_dh_orchestrator_enabled: true
```

See `defaults/main.yml` for full variable list.

## Platform Outputs

This role sets the following facts for use by the students role:

```yaml
_ocp_apps_domain: apps.cluster.example.com
_gitlab_url: https://gitlab-gitlab.apps.cluster.example.com
_gitlab_root_token: <token>
_gitlab_development_group_id: <id>
_keycloak_access_token: <token>
_keycloak_group_id: <group-id>
_dh_url: https://backstage-developer-hub-tssc-dh.apps.cluster.example.com
_gitops_url: https://tssc-gitops-server-tssc-gitops.apps.cluster.example.com
_jenkins_url: https://jenkins-jenkins.apps.cluster.example.com
_devspaces_url: https://devspaces.apps.cluster.example.com
_quay_url: https://quay-guid.apps.cluster.example.com
_acs_url: https://central-tssc-acs.apps.cluster.example.com
_tpa_url: https://server-tssc-tpa.apps.cluster.example.com
```

## Usage in AgnosticD

### In your catalog config (e.g., `common.yaml`):

```yaml
infra_workloads:
  - ocp4_workload_external_odf
  - ocp4_workload_cert_manager
  - ocp4_workload_kubernetes_image_puller
  - ocp4_workload_rhacm
  - ocp4_workload_quay_operator
  - ocp4_workload_jenkins
  - ocp4_workload_openshift_gitops
  - ocp4_workload_openshift_devspaces
  - ocp4_workload_gitops_gitlab
  - ocp4_workload_rhdh_orchestrator
  - ocp4_workload_advanced_developer_suite_platform  # Deploy platform
  - rhpds.ads.ocp4_workload_gitlab_runner

student_workloads:
  - ocp4_workload_advanced_developer_suite_students   # Provision users
```

## Dependencies

This role depends on the following workloads being deployed first:
- `ocp4_workload_external_odf` (or equivalent storage)
- `ocp4_workload_cert_manager`
- `ocp4_workload_openshift_gitops`
- `ocp4_workload_openshift_devspaces`
- `ocp4_workload_gitops_gitlab`
- `ocp4_workload_rhdh_orchestrator`

## What This Role Does NOT Do

- **No user provisioning**: Users are created by the `ocp4_workload_advanced_developer_suite_students` role
- **No showroom deployment**: Showroom instances are deployed per-user by the students role
- **No user credential reporting**: Handled by the students role

## Benefits

1. **Faster Student Onboarding**: Deploy platform once, add users on-demand
2. **Immutable Infrastructure**: Platform deployment is idempotent
3. **Independent Scaling**: Add/remove users without touching infrastructure
4. **GitOps Ready**: Separate platform deployment from user lifecycle
5. **Cost Optimization**: Single platform deployment for multiple user batches

## Testing

To test platform deployment:

```bash
ansible-playbook -e @vars.yml workload.yml
```

Where `vars.yml` contains:
```yaml
ACTION: create
guid: test-guid
common_password: test123
```

## Next Steps

After platform deployment completes:
1. Verify all platform URLs are accessible
2. Run the `ocp4_workload_advanced_developer_suite_students` role to provision users
3. Each user will get their own showroom instance

## Author

Red Hat Platform Engineering
