# ocp4_workload_dynamic_user_provisioning

## Description

This AgnosticD workload enables dynamic user provisioning for existing Red Hat Advanced
Developer Suite workshops. It allows adding new users on-demand to running workshop
environments without affecting existing users or requiring full workshop redeployment.

The workload creates users across all workshop components:
- **Red Hat Build of Keycloak (RHBK)**: Creates SSO user account
- **GitLab**: Creates GitLab user account
- **Showroom**: Deploys dedicated showroom instance for the user

## Prerequisites

- Existing REDHAT_ADS_WKS workshop must be deployed and running
- OpenShift service account token with cluster-admin privileges required
- Workshop GUID must be available
- OpenShift API CA certificate available

## Usage

### Adding a User

```bash
# Add user to workshop with GUID abc123 (variables set by openshift_cluster_admin_service_account role)
ansible-playbook main.yml \
  -e guid=abc123 \
  -e ACTION=create
```

This will create user: `user-abc123`

### Removing a User

```bash
# Remove user from workshop (variables set by openshift_cluster_admin_service_account role)
ansible-playbook main.yml \
  -e guid=abc123 \
  -e ACTION=remove
```

## Variables

### Required Variables

| Variable | Description | Set By | Example |
|----------|-------------|--------|---------|
| `guid` | Workshop GUID (auto-available in AgnosticD) | User/AgnosticD | `abc123` |
| `openshift_cluster_admin_token` | Service account token with cluster-admin privileges | `openshift_cluster_admin_service_account` role | `eyJhbGciOiJSUzI1NiIsImtpZCI6...` |
| `openshift_api_ca_cert` | OpenShift API CA certificate | `openshift_cluster_admin_service_account` role | `-----BEGIN CERTIFICATE-----...` |
| `openshift_api_url` | OpenShift API URL | `openshift_cluster_admin_service_account` role | `https://api.cluster-lnj4s.dynamic.redhatworkshops.io:6443` |

### Legacy Variables (Deprecated)

| Variable | Description | Status |
|----------|-------------|--------|
| `ocp4_workload_dynamic_user_provisioning_admin_user` | OpenShift admin username | **Deprecated** - Use token authentication |
| `ocp4_workload_dynamic_user_provisioning_admin_password` | OpenShift admin password | **Deprecated** - Use token authentication |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ocp4_workload_dynamic_user_provisioning_password` | `{{ (guid[:5] \| hash('md5') \| int(base=16) \| b64encode)[:8] }}` | Password for created user |
| `ocp4_workload_dynamic_user_provisioning_keycloak_namespace` | `tssc-keycloak` | Keycloak namespace |
| `ocp4_workload_dynamic_user_provisioning_gitlab_namespace` | `gitlab` | GitLab namespace |
| `ocp4_workload_dynamic_user_provisioning_showroom_namespace` | `showroom` | Base showroom namespace |
| `ocp4_workload_dynamic_user_provisioning_keycloak_realm` | `chicken` | Keycloak realm name |

## User Naming Convention

Users are automatically named using the pattern: `user-{GUID}`

- Workshop GUID: `abc123` → Username: `user-abc123`
- Workshop GUID: `xyz789` → Username: `user-xyz789`

This ensures:
- **Workshop Isolation**: Each workshop gets unique users
- **No Conflicts**: GUIDs prevent username collisions
- **Easy Cleanup**: All resources for a workshop can be identified by GUID

## Created Resources

### Keycloak (RHBK)
- User: `user-{guid}`
- Email: `user-{guid}@demo.redhat.com`
- Realm: `chicken`

### GitLab
- User: `user-{guid}`
- Email: `user-{guid}@demo.redhat.com`

### Showroom
- Namespace: `showroom-user-{guid}`
- Helm Release: `showroom-user-{guid}`
- Route: Auto-generated showroom URL

## Integration with Existing Workshop

The workload automatically detects and integrates with existing workshop components:

1. **Auto-discovers** Keycloak admin credentials from secrets
2. **Auto-detects** GitLab configuration and tokens
3. **Auto-configures** Showroom content from existing instances
4. **Preserves** all existing workshop functionality

## Error Handling

- Graceful handling of duplicate users (409 status codes)
- Comprehensive validation of required components
- Detailed status reporting for troubleshooting
- Safe cleanup with failure tolerance

## Example Output

```
Dynamic user user-abc123 has been successfully created for workshop abc123:

=== User Credentials ===
Username: user-abc123
Password: Xy9mK2pL

=== Access URLs ===
OpenShift Console: https://console-openshift-console.apps.cluster.example.com
Keycloak SSO: https://sso.apps.cluster.example.com
GitLab: https://gitlab-gitlab.apps.cluster.example.com
Showroom: https://showroom-user-abc123.apps.cluster.example.com

=== Status ===
Keycloak User: Created
GitLab User: Created
Showroom Instance: Ready
```

## Troubleshooting

### Common Issues

1. **Invalid service account token**: Ensure token has cluster-admin privileges and is not expired
2. **CA certificate mismatch**: Verify the CA certificate matches the OpenShift cluster
3. **Workshop not deployed**: Verify REDHAT_ADS_WKS workshop is running
4. **Network connectivity**: Check routes and ingress configuration
5. **Namespace conflicts**: Ensure GUID is unique across workshops

### Debug Mode

Run with increased verbosity for troubleshooting:

```bash
ansible-playbook main.yml -vvv \
  -e guid=abc123 \
  -e ACTION=create
```

## Authentication Methods

### Token-Based Authentication (Recommended)

The role now supports secure token-based authentication using service account tokens. This method is preferred for automation and CI/CD pipelines.

#### Integration with openshift_cluster_admin_service_account Role

For AgnosticV environments, use the `openshift_cluster_admin_service_account` role to generate the required token and CA certificate:

```yaml
# In your AgnosticV environment configuration
infra_workloads:
- openshift_cluster_admin_service_account
- ocp4_workload_dynamic_user_provisioning

# Variables are automatically available from the openshift_cluster_admin_service_account role:
# - openshift_cluster_admin_token
# - openshift_api_ca_cert
# - openshift_api_url
```

#### Manual Token Generation

If not using AgnosticV, create a service account token manually:

```bash
# Create service account with cluster-admin privileges
oc create serviceaccount cluster-admin -n openshift-config
oc create clusterrolebinding cluster-admin:serviceaccount:openshift-config:cluster-admin \
  --clusterrole=cluster-admin --serviceaccount=openshift-config:cluster-admin

# Generate long-lived token
oc create token cluster-admin -n openshift-config --duration=99999h
```

### Legacy Authentication (Deprecated)

Username/password authentication is deprecated but maintained for backward compatibility. Token-based authentication is strongly recommended for security and automation.

## Security Considerations

- **Token Security**: Service account tokens provide secure, time-limited access
- **Certificate Validation**: CA certificates ensure secure API connections
- **Password Generation**: Uses workshop-consistent password generation
- **Namespace Isolation**: Proper namespace isolation for multi-tenancy
- **No Hardcoded Secrets**: All credentials retrieved from cluster secrets
- **Least Privilege**: Service accounts can be scoped to specific permissions
