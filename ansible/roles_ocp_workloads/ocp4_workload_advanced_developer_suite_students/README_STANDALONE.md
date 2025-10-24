# Standalone Execution Guide

## Overview

The `ocp4_workload_advanced_developer_suite_students` role can run in **two modes**:

1. **Integrated Mode** (default): Runs within AgnosticD after platform deployment
2. **Standalone Mode**: Runs independently against any cluster with ADS platform deployed

This guide focuses on **Standalone Mode** - perfect for adding students days/weeks after initial platform deployment.

## Use Cases

- **Add students post-deployment**: Workshop started, need to add more participants
- **Dynamic scaling**: Add/remove students based on demand
- **Multi-cluster**: Provision students across multiple workshop clusters
- **Automation**: CI/CD pipelines that provision students on-demand
- **Testing**: Test student provisioning without full platform deployment

## Prerequisites

### Required

1. **ADS Platform Deployed**: `ocp4_workload_advanced_developer_suite_platform` must be running
2. **OpenShift Service Account Token**: Cluster-admin privileges required
3. **CA Certificate**: OpenShift API CA certificate
4. **API URL**: OpenShift cluster API endpoint

### How to Get Required Credentials

#### Option 1: Using `openshift_cluster_admin_service_account` Role (Recommended)

If your cluster has the `openshift_cluster_admin_service_account` role deployed:

```yaml
# In your AgnosticV config
infra_workloads:
  - openshift_cluster_admin_service_account
  - ocp4_workload_advanced_developer_suite_students

# Variables are automatically available:
# - openshift_api_key (service account token)
# - openshift_api_ca_cert (cluster CA)
# - openshift_api_url (API endpoint)
```

#### Option 2: Manual Token Generation

```bash
# 1. Create service account
oc create serviceaccount cluster-admin -n openshift-config

# 2. Grant cluster-admin privileges
oc create clusterrolebinding cluster-admin:sa:openshift-config:cluster-admin \
  --clusterrole=cluster-admin \
  --serviceaccount=openshift-config:cluster-admin

# 3. Generate long-lived token (24 hours)
export OPENSHIFT_API_KEY=$(oc create token cluster-admin -n openshift-config --duration=24h)

# 4. Get CA certificate
export OPENSHIFT_API_CA_CERT=$(oc config view --minify --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 -d)

# 5. Get API URL
export OPENSHIFT_API_URL=$(oc whoami --show-server)
```

## Standalone Execution

### Method 1: Direct Ansible Playbook

```bash
# Create vars file
cat > student_vars.yml <<EOF
guid: workshop-abc123
num_users: 5

# OpenShift API Access
openshift_api_key: "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
openshift_api_url: "https://api.cluster-abc123.example.com:6443"
openshift_api_ca_cert: |
  -----BEGIN CERTIFICATE-----
  MIIDDDCCAfSgAwIBAgIBATANBgkqhkiG9w...
  -----END CERTIFICATE-----

# Student Configuration
ocp4_workload_advanced_developer_suite_user_base_name: user
ocp4_workload_advanced_developer_suite_user_password: openshift
ocp4_workload_advanced_developer_suite_user_count: "{{ num_users }}"

# Workspace Configuration (optional)
ocp4_workload_advanced_developer_suite_create_workspace: true
ocp4_workload_advanced_developer_suite_cpu_limits: "4000m"
ocp4_workload_advanced_developer_suite_memory_limits: "8Gi"
EOF

# Run playbook
ansible-playbook \
  -e @student_vars.yml \
  -e ACTION=create \
  path/to/agnosticd/ansible/main.yml
```

### Method 2: Using Environment Variables

```bash
# Export credentials
export GUID=workshop-abc123
export NUM_USERS=5
export OPENSHIFT_API_KEY="eyJhbGciOiJSUzI1NiIsImtpZCI6..."
export OPENSHIFT_API_URL="https://api.cluster-abc123.example.com:6443"
export OPENSHIFT_API_CA_CERT="-----BEGIN CERTIFICATE-----..."

# Run playbook
ansible-playbook \
  -e guid=$GUID \
  -e num_users=$NUM_USERS \
  -e openshift_api_key=$OPENSHIFT_API_KEY \
  -e openshift_api_url=$OPENSHIFT_API_URL \
  -e openshift_api_ca_cert="$OPENSHIFT_API_CA_CERT" \
  -e ACTION=create \
  main.yml
```

### Method 3: AgnosticV Catalog (Separate Provisioning)

Create a standalone catalog item:

```yaml
# catalog_item: ADS_STUDENT_PROVISIONING
---
include: /includes/ansible_control_plane/current_controller.yaml
include: /includes/secrets/ocp4_token.yaml  # Contains openshift_api_key, etc.

env_type: ocp-workload
cloud_provider: none
platform: none

# Student Configuration
num_users: 3
guid: "{{ existing_workshop_guid }}"

ocp4_workload_advanced_developer_suite_user_base_name: user
ocp4_workload_advanced_developer_suite_user_password: "{{ (guid[:5] | hash('md5') | int(base=16) | b64encode)[:8] }}"

# Run only student workload
student_workloads:
  - ocp4_workload_advanced_developer_suite_students

# Platform workloads: none (platform already deployed)
infra_workloads: []
```

## Variable Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `guid` | Workshop GUID | `workshop-abc123` |
| `num_users` | Number of students to provision | `5` |
| `openshift_api_key` | Service account token | `eyJhbGciOiJSU...` |
| `openshift_api_ca_cert` | Cluster CA certificate | `-----BEGIN CERTIFICATE-----...` |
| `openshift_api_url` | API server URL | `https://api.cluster.example.com:6443` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ocp4_workload_advanced_developer_suite_user_base_name` | `user` | Username prefix (creates user1, user2, etc.) |
| `ocp4_workload_advanced_developer_suite_user_password` | `guid hash` | Student password |
| `ocp4_workload_advanced_developer_suite_create_workspace` | `true` | Create workspace namespace with quotas |
| `ocp4_workload_advanced_developer_suite_cpu_limits` | `4000m` | CPU limit per student |
| `ocp4_workload_advanced_developer_suite_memory_limits` | `8Gi` | Memory limit per student |

See `defaults/main.yml` for complete list.

## What Gets Created (Per Student)

### 1. Keycloak User
- **Realm**: `trusted-artifact-signer`
- **Group**: `tssc`
- **Username**: `user1`, `user2`, ..., `userN`

### 2. TPA User
- **Realm**: `chicken`
- **Username**: `user1`, `user2`, ..., `userN`

### 3. GitLab Membership
- **Group**: `development`
- **Access Level**: Maintainer

### 4. Showroom Instance
- **Namespace**: `showroom-user1`, `showroom-user2`, etc.
- **Route**: `https://showroom-showroom-user1.apps.cluster.example.com`
- **Variables**: User-specific workshop environment

### 5. Workspace Namespace (if enabled)
- **Namespace**: `user1-workspace`, `user2-workspace`, etc.
- **ResourceQuota**: CPU, memory, storage limits
- **LimitRange**: Default container limits
- **RBAC**: Admin role for student
- **ArgoCD AppProject**: GitOps project with quotas

## Removing Students

```bash
# Remove all students
ansible-playbook \
  -e @student_vars.yml \
  -e ACTION=remove \
  main.yml
```

### What Gets Deleted

- ✅ Keycloak users (both realms)
- ✅ Showroom namespaces
- ✅ Workspace namespaces
- ✅ ArgoCD AppProjects
- ✅ Resource quotas and limit ranges
- ⚠️ GitLab users **preserved** (for audit trail)

To delete GitLab users, edit `tasks/remove_student.yml` and uncomment the deletion block.

## Examples

### Example 1: Add 10 Students to Existing Workshop

```bash
ansible-playbook \
  -e guid=workshop-prod-001 \
  -e num_users=10 \
  -e openshift_api_key="$TOKEN" \
  -e openshift_api_url="https://api.prod.example.com:6443" \
  -e openshift_api_ca_cert="$CA_CERT" \
  -e ACTION=create \
  main.yml
```

**Result**: Creates user1 through user10 with showrooms and workspaces

### Example 2: Add Students with Custom Settings

```yaml
# custom_students.yml
guid: workshop-qa-002
num_users: 3

openshift_api_key: "{{ lookup('env', 'OPENSHIFT_API_KEY') }}"
openshift_api_url: "https://api.qa.example.com:6443"
openshift_api_ca_cert: "{{ lookup('file', '/path/to/ca.crt') }}"

# Custom student configuration
ocp4_workload_advanced_developer_suite_user_base_name: student
ocp4_workload_advanced_developer_suite_user_password: "MySecurePass123"

# Custom resource limits
ocp4_workload_advanced_developer_suite_cpu_limits: "8000m"
ocp4_workload_advanced_developer_suite_memory_limits: "16Gi"
ocp4_workload_advanced_developer_suite_max_argocd_apps: "20"
```

```bash
ansible-playbook -e @custom_students.yml -e ACTION=create main.yml
```

**Result**: Creates student1, student2, student3 with higher resource limits

### Example 3: CI/CD Pipeline Integration

```yaml
# .gitlab-ci.yml
provision_students:
  stage: provision
  script:
    - |
      ansible-playbook \
        -e guid=$CI_PIPELINE_ID \
        -e num_users=$STUDENT_COUNT \
        -e openshift_api_key=$OPENSHIFT_TOKEN \
        -e openshift_api_url=$OPENSHIFT_API \
        -e openshift_api_ca_cert="$OPENSHIFT_CA" \
        -e ACTION=create \
        main.yml
  when: manual

cleanup_students:
  stage: cleanup
  script:
    - |
      ansible-playbook \
        -e guid=$CI_PIPELINE_ID \
        -e num_users=$STUDENT_COUNT \
        -e openshift_api_key=$OPENSHIFT_TOKEN \
        -e openshift_api_url=$OPENSHIFT_API \
        -e openshift_api_ca_cert="$OPENSHIFT_CA" \
        -e ACTION=remove \
        main.yml
  when: manual
```

## Troubleshooting

### Issue: "Namespace tssc-dh not found"

**Cause**: Platform role not deployed

**Solution**: Deploy `ocp4_workload_advanced_developer_suite_platform` first

```bash
# Verify platform is running
oc get ns | grep -E "tssc|gitlab|showroom"
```

### Issue: "401 Unauthorized"

**Cause**: Invalid or expired service account token

**Solution**: Regenerate token

```bash
oc create token cluster-admin -n openshift-config --duration=24h
```

### Issue: "Cannot find Keycloak admin credentials"

**Cause**: Keycloak not deployed or secret missing

**Solution**: Verify Keycloak deployment

```bash
oc get secret keycloak-initial-admin -n tssc-keycloak
```

### Issue: "Showroom deployment fails"

**Cause**: Helm chart issues or missing ocp4_workload_showroom role

**Solution**: Verify showroom role is available

```bash
ls ansible/roles_ocp_workloads/ocp4_workload_showroom
```

## Security Considerations

### Token Security
- Use short-lived tokens (24 hours recommended)
- Rotate tokens regularly
- Never commit tokens to version control
- Use CI/CD secrets management

### Certificate Validation
- Always provide valid CA certificates
- Don't disable certificate validation in production
- Store CA certs securely

### Resource Quotas
- Set appropriate limits based on cluster capacity
- Monitor resource usage per student
- Implement cluster-wide quotas

## Advanced Usage

### Running Against Multiple Clusters

```bash
# Cluster 1
ansible-playbook \
  -e @cluster1_students.yml \
  -e openshift_api_url=https://api.cluster1.example.com:6443 \
  -e ACTION=create \
  main.yml

# Cluster 2
ansible-playbook \
  -e @cluster2_students.yml \
  -e openshift_api_url=https://api.cluster2.example.com:6443 \
  -e ACTION=create \
  main.yml
```

### Custom Naming Patterns

For GUID-based naming (like `ocp4_workload_dynamic_user_provisioning`):

```yaml
# Use GUID pattern instead of sequential numbers
ocp4_workload_advanced_developer_suite_user_base_name: "user-{{ guid }}"
ocp4_workload_advanced_developer_suite_user_count: 1
```

This creates: `user-workshop-abc123` instead of `user1`

## Comparison: Integrated vs. Standalone

| Aspect | Integrated Mode | Standalone Mode |
|--------|----------------|-----------------|
| **Timing** | During platform deployment | Anytime post-deployment |
| **Credentials** | Local cluster context | Service account token + CA cert |
| **Use Case** | Initial workshop setup | Adding students later |
| **Platform Facts** | From previous role | Auto-discovered |
| **Flexibility** | Runs once | Run multiple times |
| **Multi-cluster** | Single cluster | Any cluster |

## Best Practices

1. **Token Management**: Use short-lived tokens, rotate regularly
2. **Resource Limits**: Set quotas based on workshop requirements
3. **Naming**: Use consistent username patterns
4. **Audit Trail**: Keep GitLab users for audit (don't delete)
5. **Testing**: Test with 1-2 users before provisioning many
6. **Monitoring**: Watch resource usage as students provision
7. **Documentation**: Document custom variables for your workshops

## Next Steps

- Review `defaults/main.yml` for all available variables
- Test with `num_users: 1` first
- Monitor cluster resources during provisioning
- Set up automated student cleanup after workshop ends
- Integrate with your CI/CD pipeline

## Support

For issues or questions:
- Check role README.md for detailed documentation
- Review task files for implementation details
- Check AgnosticD logs for error messages
