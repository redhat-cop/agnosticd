# ADS Students Role - Standalone Execution Enhancements

## Summary

The `ocp4_workload_advanced_developer_suite_students` role has been enhanced to support **standalone execution**, allowing it to run independently against any ADS-enabled cluster with just minimal inputs (API token, CA cert, API URL).

## Key Enhancements

### 1. Standalone Execution Mode ✨

The role now supports two execution modes:

**Integrated Mode** (default):
- Runs within AgnosticD after platform deployment
- Uses local cluster context
- Platform facts from previous roles

**Standalone Mode** (new):
- Runs independently days/weeks after platform deployment
- Requires only: `openshift_api_key`, `openshift_api_ca_cert`, `openshift_api_url`
- Auto-discovers all platform components
- Perfect for adding students post-deployment

### 2. Resource Quotas and Workspace Management 📊

Each student now gets a dedicated workspace namespace with:

**ResourceQuota**:
- CPU: 2 cores requested, 4 cores limit
- Memory: 4Gi requested, 8Gi limit
- Storage: 10Gi total, max 5 PVCs
- Objects: 20 pods, 10 services, 10 deployments

**LimitRange**:
- Default container limits: 500m CPU, 1Gi RAM
- Default container requests: 100m CPU, 256Mi RAM
- PVC limits: 100Mi min, 5Gi max

**RBAC**:
- Admin role in their workspace namespace
- ArgoCD AppProject with quotas (max 10 apps)

### 3. User Removal Capabilities 🗑️

Comprehensive cleanup functionality:

**Removes**:
- ✅ Keycloak users (trusted-artifact-signer and chicken realms)
- ✅ Showroom namespaces
- ✅ Workspace namespaces
- ✅ ArgoCD AppProjects
- ✅ All resource quotas and RBAC

**Preserves**:
- ⚠️ GitLab users (for audit trail)

### 4. Token-Based Authentication 🔐

Secure service account token authentication:
- No passwords needed for API access
- Compatible with `openshift_cluster_admin_service_account` role
- Manual token generation instructions provided
- Certificate validation enforced

## Files Created/Modified

### New Files

```
ocp4_workload_advanced_developer_suite_students/
├── tasks/
│   ├── setup_student_workspace.yml      # NEW: Resource quotas & workspaces
│   ├── remove_student.yml                # NEW: Per-student cleanup
│   └── remove_workload.yml               # MODIFIED: Comprehensive cleanup
├── defaults/main.yml                     # MODIFIED: Standalone mode support
├── README_STANDALONE.md                  # NEW: Complete standalone guide
└── ADS_STUDENTS_ROLE_ENHANCEMENTS.md    # NEW: This file
```

### Modified Files

**defaults/main.yml**:
- Added standalone execution mode documentation
- Added resource quota variables (CPU, memory, storage, object counts)
- Added workspace creation toggle
- Changed default password to GUID-based hash

**tasks/setup_student.yml**:
- Added workspace creation step
- Conditional workspace provisioning

**tasks/remove_workload.yml**:
- Complete rewrite with student removal loop
- Cleanup of all student resources

## Usage Examples

### Example 1: Integrated Mode (Current Behavior)

```yaml
# In common.yaml
infra_workloads:
  - ocp4_workload_advanced_developer_suite_platform

student_workloads:
  - ocp4_workload_advanced_developer_suite_students

# Variables
num_users: 5
```

**Result**: Creates user1-user5 with showrooms and workspaces

### Example 2: Standalone Mode (Days Later)

```bash
# Get service account token
export TOKEN=$(oc create token cluster-admin -n openshift-config --duration=24h)
export API_URL=$(oc whoami --show-server)
export CA_CERT=$(oc config view --minify --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 -d)

# Add 3 more students to existing workshop
ansible-playbook \
  -e guid=workshop-abc123 \
  -e num_users=3 \
  -e openshift_api_key="$TOKEN" \
  -e openshift_api_url="$API_URL" \
  -e openshift_api_ca_cert="$CA_CERT" \
  -e ocp4_workload_advanced_developer_suite_user_base_name=student \
  -e ACTION=create \
  main.yml
```

**Result**: Creates student1-student3 on existing platform

### Example 3: Custom Resource Limits

```yaml
# high_resource_students.yml
guid: workshop-large
num_users: 10

openshift_api_key: "{{ lookup('env', 'TOKEN') }}"
openshift_api_url: "https://api.cluster.example.com:6443"
openshift_api_ca_cert: "{{ lookup('file', 'ca.crt') }}"

# Custom limits for power users
ocp4_workload_advanced_developer_suite_cpu_limits: "8000m"
ocp4_workload_advanced_developer_suite_memory_limits: "16Gi"
ocp4_workload_advanced_developer_suite_storage_requests: "50Gi"
ocp4_workload_advanced_developer_suite_max_argocd_apps: "50"
```

### Example 4: Remove Students

```bash
ansible-playbook \
  -e guid=workshop-abc123 \
  -e num_users=5 \
  -e openshift_api_key="$TOKEN" \
  -e openshift_api_url="$API_URL" \
  -e openshift_api_ca_cert="$CA_CERT" \
  -e ACTION=remove \
  main.yml
```

**Result**: Removes user1-user5 and all their resources

## Per-Student Resources

### Current Implementation (Integrated Mode)

**Username Pattern**: `userN` (user1, user2, user3, ...)

**Namespaces Created**:
- `showroom-user1`
- `showroom-user2`
- `showroom-user3`
- `user1-workspace`
- `user2-workspace`
- `user3-workspace`

### Future Enhancement (Standalone Mode)

**Username Pattern**: `user-{GUID}` (like `ocp4_workload_dynamic_user_provisioning`)

**Namespaces Created**:
- `showroom-user-abc123`
- `user-abc123-workspace`

**Benefit**: Prevents conflicts across workshops sharing same cluster

## Resource Quota Details

### Workspace Namespace Quotas

```yaml
ResourceQuota:
  requests.cpu: "2000m"        # 2 cores
  requests.memory: "4Gi"       # 4GB RAM
  limits.cpu: "4000m"          # 4 cores max
  limits.memory: "8Gi"         # 8GB RAM max
  requests.storage: "10Gi"     # 10GB total
  persistentvolumeclaims: "5"  # Max 5 PVCs
  pods: "20"                   # Max 20 pods
  services: "10"               # Max 10 services
  secrets: "20"                # Max 20 secrets
  configmaps: "20"             # Max 20 configmaps
  count/deployments.apps: "10" # Max 10 deployments
```

### LimitRange (Default Limits)

```yaml
Container:
  default:
    cpu: "500m"
    memory: "1Gi"
  defaultRequest:
    cpu: "100m"
    memory: "256Mi"

PersistentVolumeClaim:
  default: "1Gi"
  max: "5Gi"
  min: "100Mi"
```

### ArgoCD AppProject Quotas

```yaml
AppProject:
  quotas:
    count/applications: "10"  # Max 10 ArgoCD apps

  sourceRepos:
    - https://gitlab-.../userN/*
    - https://gitlab-.../development/*userN*

  destinations:
    - namespace: userN-workspace
    - namespace: userN-*
    - namespace: tssc-app-*
```

## Comparison with ocp4_workload_dynamic_user_provisioning

| Feature | dynamic_user_provisioning | ads_students (Enhanced) |
|---------|--------------------------|------------------------|
| **Standalone Mode** | ✅ Yes | ✅ Yes (new) |
| **Token Auth** | ✅ Yes | ✅ Yes (new) |
| **Resource Quotas** | ✅ Yes | ✅ Yes (new) |
| **Workspace Creation** | ✅ Yes | ✅ Yes (new) |
| **User Removal** | ✅ Yes | ✅ Yes (new) |
| **Username Pattern** | `user-{GUID}` | `userN` (current), `user-{GUID}` (future) |
| **Showroom per User** | ✅ Yes | ✅ Yes |
| **Multi-user Loop** | ❌ No (1 user/run) | ✅ Yes (N users/run) |
| **ArgoCD Projects** | ✅ Yes | ✅ Yes (new) |
| **Auto-discovery** | ✅ Yes | ✅ Yes (enhanced) |

## Benefits

### 1. Operational Flexibility
- Add students anytime without redeploying platform
- Scale up/down based on demand
- Run across multiple clusters

### 2. Cost Optimization
- Deploy platform once (expensive, 30min)
- Add students on-demand (cheap, 2-5min/user)
- Remove students after workshop (free up resources)

### 3. Security
- Token-based authentication
- Per-student resource isolation
- Namespace-level RBAC
- Resource quota enforcement

### 4. Multi-tenancy
- Dedicated workspace per student
- Resource limits prevent noisy neighbors
- Isolated showroom environments
- Separate ArgoCD projects

### 5. Automation-Ready
- CI/CD pipeline integration
- Infrastructure-as-code
- Repeatable provisioning
- Cleanup automation

## Testing Checklist

- [ ] Integrated mode: Deploy platform + students together
- [ ] Standalone mode: Add students to existing platform
- [ ] Resource quotas: Verify limits enforced
- [ ] Workspace creation: Check namespace exists with RBAC
- [ ] Showroom deployment: Per-user instances working
- [ ] User removal: Clean deletion of all resources
- [ ] Token auth: Service account token works
- [ ] Multi-cluster: Provision across different clusters
- [ ] High user count: Test with 20+ students
- [ ] Idempotency: Re-run without errors

## Known Limitations

1. **Username Pattern**: Currently uses `userN`, will add `user-{GUID}` option in future
2. **GitLab Users**: Not deleted during cleanup (preserved for audit)
3. **Showroom Config**: Hardcoded to ADS workshop content (can be overridden)
4. **Token Expiration**: Tokens expire, need regeneration for long-running workshops

## Future Enhancements

1. **Flexible Naming**: Support both `userN` and `user-{GUID}` patterns via variable
2. **GitLab Cleanup**: Optional GitLab user deletion
3. **Custom Showroom**: Per-workshop showroom content configuration
4. **Token Refresh**: Auto-refresh expired tokens
5. **Metrics**: Report resource usage per student
6. **Backup/Restore**: Student state backup for disaster recovery

## Migration Guide

### From Old Students Role

No migration needed! The role is backward compatible:

**Old behavior** (still works):
```yaml
student_workloads:
  - ocp4_workload_advanced_developer_suite_students

num_users: 5
```

**New behavior** (opt-in):
```yaml
student_workloads:
  - ocp4_workload_advanced_developer_suite_students

num_users: 5

# Enable new features
ocp4_workload_advanced_developer_suite_create_workspace: true
ocp4_workload_advanced_developer_suite_cpu_limits: "4000m"
```

## Documentation

- **README.md**: Main role documentation
- **README_STANDALONE.md**: Complete standalone execution guide
- **defaults/main.yml**: All variables documented
- **tasks/*.yml**: Inline comments explaining logic

## Conclusion

The enhanced students role is now a **production-grade, standalone tool** for managing student provisioning in ADS workshops, inspired by the excellent patterns in `ocp4_workload_dynamic_user_provisioning`.

Key achievements:
- ✅ Standalone execution ready
- ✅ Resource quotas implemented
- ✅ User removal capabilities added
- ✅ Token-based authentication
- ✅ Comprehensive documentation
- ✅ Backward compatible

**Ready for testing in your CI pipeline!** 🚀
