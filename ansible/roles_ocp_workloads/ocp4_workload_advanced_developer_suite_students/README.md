# ocp4_workload_advanced_developer_suite_students

## Description

Student provisioning role for Red Hat Advanced Developer Suite (ADS) / Trusted Application Pipeline (TAP).

This role provisions students on a pre-deployed ADS platform:
- Creates Keycloak users in trusted-artifact-signer realm
- Creates TPA users in chicken realm
- Adds users to GitLab development group
- Deploys per-user showroom instances
- Reports individual user credentials

## Purpose

This role provides **student lifecycle management** separate from platform infrastructure:
- **Platform Role** (`ocp4_workload_advanced_developer_suite_platform`): Deploy infrastructure once (~20-30 minutes)
- **Students Role** (this role): Provision users on-demand (~2-5 minutes per user)

## Prerequisites

The platform role **must** be deployed first. This role will fail if the following namespaces don't exist:
- `tssc-dh` (Developer Hub)
- `tssc-keycloak` (Keycloak)
- `gitlab` (GitLab)

## Architecture

```
For each user (user1, user2, ..., userN):
┌─────────────────────────────────────────────┐
│   Student Provisioning Loop                │
├─────────────────────────────────────────────┤
│ 1. Create Keycloak user                    │
│    └─ Realm: trusted-artifact-signer       │
│    └─ Group: tssc                           │
│                                             │
│ 2. Create TPA user                         │
│    └─ Realm: chicken                        │
│                                             │
│ 3. Add to GitLab group                     │
│    └─ Group: development (Maintainer)      │
│                                             │
│ 4. Deploy showroom                         │
│    └─ Namespace: showroom-user1            │
│    └─ Route: showroom-showroom-user1       │
│                                             │
│ 5. Report credentials                      │
│    └─ AgnosticD user_info                  │
└─────────────────────────────────────────────┘
```

## Role Variables

### Required Variables

```yaml
# Number of students to provision
num_users: 5

# Student username base (will create user1, user2, ..., userN)
ocp4_workload_advanced_developer_suite_user_base_name: user

# Student password (same for all students)
ocp4_workload_advanced_developer_suite_user_password: openshift

# GUID for resource naming
guid: unique-guid

# Common password (for admin accounts)
common_password: password
```

### Optional Variables

```yaml
# Showroom configuration
ocp4_workload_showroom_namespace: showroom
ocp4_workload_showroom_content_git_repo: https://github.com/rhpds/showroom-ads-workshop.git
ocp4_workload_showroom_content_git_repo_ref: main
ocp4_workload_showroom_deployer_chart_name: zerotouch
ocp4_workload_showroom_deployer_chart_version: "1.9.13"

# Namespace references (must match platform deployment)
ocp4_workload_advanced_developer_suite_keycloak_namespace: tssc-keycloak
ocp4_workload_advanced_developer_suite_dh_namespace: tssc-dh
ocp4_workload_advanced_developer_suite_gitlab_namespace: gitlab
```

See `defaults/main.yml` for full variable list.

## Per-Student Resources

Each student receives:

### 1. Keycloak Account
- **Realm**: trusted-artifact-signer
- **Group**: tssc
- **Username**: user1, user2, ..., userN
- **Password**: Configured via `ocp4_workload_advanced_developer_suite_user_password`

### 2. TPA Account
- **Realm**: chicken
- **Username**: user1, user2, ..., userN
- **Password**: Configured via `ocp4_workload_advanced_developer_suite_user_password`

### 3. GitLab Membership
- **Group**: development
- **Access Level**: Maintainer (50)
- **SSO**: Via Keycloak OIDC

### 4. Showroom Instance
- **Namespace**: showroom-user1, showroom-user2, etc.
- **Route**: https://showroom-showroom-user1.apps.cluster.example.com
- **Variables**: User-specific environment variables injected

### 5. Credentials Report
All credentials reported via AgnosticD `user_info` for each student

## Usage in AgnosticD

### In your catalog config (e.g., `common.yaml`):

```yaml
# Platform deployment (one time)
infra_workloads:
  - ocp4_workload_external_odf
  - ocp4_workload_cert_manager
  - ocp4_workload_kubernetes_image_puller
  - ocp4_workload_openshift_gitops
  - ocp4_workload_openshift_devspaces
  - ocp4_workload_gitops_gitlab
  - ocp4_workload_rhdh_orchestrator
  - ocp4_workload_advanced_developer_suite_platform
  - rhpds.ads.ocp4_workload_gitlab_runner

# Student provisioning (runs based on num_users)
student_workloads:
  - ocp4_workload_advanced_developer_suite_students

# Variables
ocp4_workload_advanced_developer_suite_user_base_name: user
ocp4_workload_advanced_developer_suite_user_password: "{{ common_password }}"
ocp4_workload_advanced_developer_suite_user_count: "{{ num_users }}"
```

### Catalog Parameter

```yaml
parameters:
  - name: num_users
    description: Number of students to provision
    formLabel: Student Count
    openAPIV3Schema:
      type: integer
      default: 1
      minimum: 1
      maximum: 50
```

## How It Works

### 1. Platform Facts Retrieval
The role first retrieves all necessary information from the deployed platform:
- Ingress domain
- Keycloak admin credentials → generates access token
- GitLab root token
- GitLab development group ID
- Keycloak tssc group ID
- Platform URLs

### 2. Student Loop
For each student (1 to num_users):
```yaml
- Create Keycloak user in trusted-artifact-signer realm
- Create TPA user in chicken realm
- Wait for GitLab user sync (from Keycloak OIDC)
- Add user to GitLab development group
- Deploy showroom in namespace showroom-userN
- Report credentials via agnosticd_user_info
```

### 3. Showroom Deployment
Each student gets an isolated showroom instance:
```yaml
ocp4_workload_showroom:
  namespace: showroom-user1
  variables:
    user: user1
    openshift_cluster_console_url: ...
    rhdh_url: ...
    gitlab_url: ...
    # All platform URLs injected
```

## Example Output

After provisioning 3 students:

```
Namespaces created:
- showroom-user1
- showroom-user2
- showroom-user3

Keycloak users (realm: trusted-artifact-signer):
- user1 (group: tssc)
- user2 (group: tssc)
- user3 (group: tssc)

TPA users (realm: chicken):
- user1
- user2
- user3

GitLab members (group: development):
- user1 (Maintainer)
- user2 (Maintainer)
- user3 (Maintainer)

Showroom URLs:
- https://showroom-showroom-user1.apps.cluster.example.com
- https://showroom-showroom-user2.apps.cluster.example.com
- https://showroom-showroom-user3.apps.cluster.example.com
```

## Idempotency

This role is designed to be idempotent:
- Keycloak user creation returns 201 or 409 (already exists)
- GitLab group membership returns 201 or 409 (already exists)
- Showroom deployment updates existing resources

You can safely re-run this role to add more students or update existing ones.

## Testing

To test student provisioning:

```bash
ansible-playbook -e @vars.yml workload.yml
```

Where `vars.yml` contains:
```yaml
ACTION: create
guid: test-guid
num_users: 2
common_password: test123
ocp4_workload_advanced_developer_suite_user_password: openshift
```

## Removal

To remove student provisioning (future enhancement):
```yaml
ACTION: destroy
```

This will remove showroom namespaces but keep Keycloak/GitLab users for audit purposes.

## Dependencies

This role depends on:
- `ocp4_workload_advanced_developer_suite_platform` (must be deployed first)
- `ocp4_workload_showroom` (included dynamically)

## Benefits

1. **Fast Onboarding**: Add 20 students in ~10 minutes
2. **On-Demand**: Provision students as needed, not during platform deployment
3. **Isolated Resources**: Each student has their own showroom namespace
4. **Clear Boundary**: Student lifecycle separate from platform
5. **Scalable**: Add students without redeploying infrastructure

## Troubleshooting

### Platform not found
```
Error: Namespace tssc-dh not found
Solution: Deploy ocp4_workload_advanced_developer_suite_platform first
```

### GitLab user not syncing
```
Error: GitLab user not found after 30 retries
Solution: Check Keycloak→GitLab OIDC sync configuration
```

### Showroom deployment fails
```
Error: Helm chart not found
Solution: Ensure ocp4_workload_showroom role is accessible
```

## Author

Red Hat Platform Engineering
