# Students Role Architecture - RHDH-Centric Approach

## Design Philosophy

This role follows a **RHDH (Red Hat Developer Hub) first** approach:

- **RHDH manages namespaces**: Software templates create namespaces (tssc-app-*, user*-dev, etc.)
- **We manage quotas**: ClusterResourceQuota applies limits across all user's namespaces
- **We manage users**: Keycloak, GitLab, TPA user provisioning
- **We manage showroom**: Per-user workshop UI

## What We DON'T Create

❌ **No workspace namespaces** - RHDH software templates create namespaces when users scaffold applications
❌ **No namespace-level ResourceQuota** - Would only apply to one namespace
❌ **No predefined project structure** - RHDH templates define the structure

## What We DO Create

### 1. Per-Student User Accounts

**Keycloak**:
- User in `trusted-artifact-signer` realm (for OpenShift/RHDH login)
- User in `chicken` realm (for TPA - Trusted Profile Analyzer)
- Member of `tssc` group

**GitLab**:
- User account (synced from Keycloak via OIDC)
- Member of `development` group (Maintainer access)

### 2. Per-Student Showroom

**Namespace**: `showroom-user1`, `showroom-user2`, ...

**Purpose**: Workshop UI with embedded terminals, instructions, and environment variables

**Variables Injected**:
- OpenShift console URL
- RHDH URL
- GitLab URL
- All service credentials

### 3. Cluster-Level Resource Quota

**Resource**: `ClusterResourceQuota` (OpenShift-specific)

**Scope**: Applies across **ALL namespaces** created by or for the user

**Selector**:
```yaml
selector:
  annotations:
    openshift.io/requester: user1
  labels:
    matchLabels:
      user: user1
```

**Limits** (total across all namespaces):
- CPU: 2 cores requested, 4 cores max
- Memory: 4Gi requested, 8Gi max
- Storage: 10Gi total, max 5 PVCs
- Pods: 20 max
- Services: 10 max
- Routes: 20 max
- Deployments: 10 max

**Why ClusterResourceQuota?**
- User creates 3 namespaces via RHDH templates? All 3 share the same quota pool
- User hits pod limit? Can't create more pods in ANY namespace
- Fair resource distribution across all students

### 4. ArgoCD AppProject

**Resource**: `AppProject` in `tssc-gitops` namespace

**Purpose**: Isolate GitOps deployments per student

**Source Repos Allowed**:
- `https://gitlab-.../user1/*` (personal repos)
- `https://gitlab-.../development/user1*` (team repos)
- `https://gitlab-.../development/*` (shared repos)

**Destination Namespaces Allowed**:
- `tssc-app-*` (RHDH default pattern)
- `user1-*` (user-prefixed namespaces)
- `*-user1` (user-suffixed namespaces)
- `*-user1-*` (user anywhere in name)

**Quota**:
- Max 10 ArgoCD Applications per student

**RBAC**:
- `user1` can create/sync/delete apps in their project
- `user1` can read repos in their project
- `user1` CANNOT modify project quotas

## RHDH Software Template Workflow

### Student Experience

1. **Login to RHDH** → Keycloak SSO (created by us)
2. **Browse Software Catalog** → Templates available
3. **Create Component**:
   - Template: "Spring Boot Microservice"
   - Name: `my-app`
   - GitLab Group: `development`
   - Namespace: `tssc-app-my-app` (template decides)
4. **RHDH Actions**:
   - Creates GitLab repo: `development/user1-my-app`
   - Creates namespace: `tssc-app-my-app` (requester: user1)
   - Creates ArgoCD Application in user1's AppProject
   - Triggers GitOps deployment
5. **Quota Enforcement**:
   - ClusterResourceQuota counts resources in `tssc-app-my-app`
   - If user1 already has 18 pods across other namespaces, only 2 more allowed

### Example: Student Creates 3 Apps

```
user1 scaffolds apps via RHDH:
├── app1 → namespace: tssc-app-petclinic (10 pods, 2Gi RAM)
├── app2 → namespace: tssc-app-inventory (5 pods, 1Gi RAM)
└── app3 → namespace: user1-frontend (3 pods, 500Mi RAM)

ClusterResourceQuota user1-quota:
  Status:
    Used:
      pods: 18/20
      requests.memory: 3.5Gi/4Gi
      limits.memory: 7Gi/8Gi

  Result: user1 can create 2 more pods total across ALL namespaces
```

## Cleanup Process

### What Gets Deleted

When removing a student:

1. **Keycloak users** (both realms)
2. **Showroom namespace** (`showroom-user1`)
3. **ClusterResourceQuota** (`user1-quota`)
4. **All RHDH-created namespaces**:
   - Identified by: `openshift.io/requester: user1`
   - Identified by: `label: user=user1`
   - Examples: `tssc-app-*`, `user1-*`, etc.
5. **ArgoCD AppProject** (`user1-project`)

### What Gets Preserved

- **GitLab user** (for audit trail)
- **GitLab repositories** (preserve code)

## Resource Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    Student Provisioning                      │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  Create user1 in:                                            │
│  • Keycloak (trusted-artifact-signer + chicken)              │
│  • GitLab (development group)                                │
│  • Showroom (showroom-user1 namespace)                       │
│  • ClusterResourceQuota (user1-quota)                        │
│  • ArgoCD AppProject (user1-project)                         │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│           Student Uses RHDH Software Templates               │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  RHDH Template Creates:                                      │
│  • GitLab Repo: development/user1-petclinic                  │
│  • Namespace: tssc-app-petclinic                             │
│    └─ annotation: openshift.io/requester=user1              │
│  • ArgoCD Application: petclinic-app                         │
│    └─ in AppProject: user1-project                           │
│  • Deployments, Services, Routes in namespace                │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│         ClusterResourceQuota Enforcement                     │
│                                                              │
│  Counts resources across:                                   │
│  • showroom-user1 (our showroom)                             │
│  • tssc-app-petclinic (RHDH created)                         │
│  • tssc-app-inventory (RHDH created)                         │
│  • user1-frontend (RHDH created)                             │
│                                                              │
│  Total: 18/20 pods, 3.5/4Gi RAM → 2 pods remaining          │
└──────────────────────────────────────────────────────────────┘
```

## Key Benefits

### 1. RHDH-Native
- Students use familiar developer portal workflow
- Templates enforce standards and best practices
- No manual namespace/repo creation

### 2. Fair Resource Distribution
- ClusterResourceQuota prevents one student from hogging resources
- Limits apply across all student's namespaces
- Clear feedback when quota exceeded

### 3. GitOps Isolation
- Each student's ArgoCD apps isolated in their AppProject
- Can't accidentally sync other students' apps
- Clear ownership and RBAC

### 4. Clean Separation
- Platform team manages: users, quotas, showrooms
- RHDH manages: namespaces, apps, GitOps
- Students manage: their code and deployments

## Variables Summary

### Cluster Quota Settings

```yaml
# defaults/main.yml
ocp4_workload_advanced_developer_suite_enable_cluster_quotas: true
ocp4_workload_advanced_developer_suite_cpu_requests: "2000m"
ocp4_workload_advanced_developer_suite_cpu_limits: "4000m"
ocp4_workload_advanced_developer_suite_memory_requests: "4Gi"
ocp4_workload_advanced_developer_suite_memory_limits: "8Gi"
ocp4_workload_advanced_developer_suite_storage_requests: "10Gi"
ocp4_workload_advanced_developer_suite_pvc_count: "5"
ocp4_workload_advanced_developer_suite_max_pods: "20"
ocp4_workload_advanced_developer_suite_max_services: "10"
ocp4_workload_advanced_developer_suite_max_routes: "20"
ocp4_workload_advanced_developer_suite_max_deployments: "10"
ocp4_workload_advanced_developer_suite_max_argocd_apps: "10"
```

### Disable Cluster Quotas

```yaml
# If you don't want quotas (e.g., small class, trusted users)
ocp4_workload_advanced_developer_suite_enable_cluster_quotas: false
```

## Comparison: Old vs. New Approach

| Aspect | Old (Workspace) | New (RHDH-Centric) |
|--------|----------------|-------------------|
| **Namespace Creation** | `user1-workspace` | RHDH templates create |
| **Quota Scope** | Single namespace | All user's namespaces |
| **RHDH Integration** | Manual setup | Native workflow |
| **Resource Limits** | Per workspace | Cluster-wide per user |
| **Cleanup** | 1 workspace namespace | All RHDH-created namespaces |
| **GitOps** | Not integrated | ArgoCD AppProject |

## Testing Scenarios

### Scenario 1: Student Creates App

```bash
# As user1 in RHDH:
1. Click "Create Component"
2. Select "Spring Boot Microservice"
3. Name: "inventory-service"
4. Click "Create"

# Expected:
✅ GitLab repo created: development/user1-inventory-service
✅ Namespace created: tssc-app-inventory-service
✅ ArgoCD app created in user1-project
✅ Resources counted in user1-quota
✅ Deployment succeeds (within quota)
```

### Scenario 2: Student Exceeds Quota

```bash
# As user1 (already has 19/20 pods):
1. Create new app that needs 5 pods
2. Template tries to deploy

# Expected:
❌ Deployment fails: "exceeded quota: user1-quota"
✅ Error message shown in RHDH
✅ Student reduces replica count or deletes old apps
✅ Retry succeeds
```

### Scenario 3: Student Removal

```bash
# As admin:
ansible-playbook -e ACTION=remove -e num_users=1

# Expected:
✅ Keycloak user deleted
✅ showroom-user1 namespace deleted
✅ ClusterResourceQuota user1-quota deleted
✅ tssc-app-* namespaces deleted (if requester=user1)
✅ user1-project AppProject deleted
✅ GitLab user preserved
```

## Summary

This architecture provides:
- ✅ **RHDH-native workflow** for students
- ✅ **Cluster-level quota enforcement** across all namespaces
- ✅ **GitOps isolation** via ArgoCD AppProjects
- ✅ **Clean separation** between platform and application concerns
- ✅ **Fair resource distribution** among students
- ✅ **Comprehensive cleanup** of all student resources

Perfect for workshop environments where students use RHDH to scaffold applications!
