# ocp4_workload_dynamic_user_provisioning

## Description

This AgnosticD workload enables dynamic user provisioning for existing Red Hat Advanced Developer Suite workshops. It allows adding new users on-demand to running workshop environments without affecting existing users or requiring full workshop redeployment.

The workload creates users across all workshop components:
- **Red Hat Build of Keycloak (RHBK)**: Creates SSO user account
- **GitLab**: Creates GitLab user account  
- **Showroom**: Deploys dedicated showroom instance for the user

## Prerequisites

- Existing REDHAT_ADS_WKS workshop must be deployed and running
- OpenShift admin credentials required
- Workshop GUID must be available

## Usage

### Adding a User

```bash
# Add user to workshop with GUID abc123
ansible-playbook main.yml \
  -e guid=abc123 \
  -e ACTION=create \
  -e ocp4_workload_dynamic_user_provisioning_admin_user=admin \
  -e ocp4_workload_dynamic_user_provisioning_admin_password=your-admin-password \
  -e ocp4_workload_dynamic_user_provisioning_openshift_console_url=https://console-openshift-console.apps.cluster-lnj4s.dynamic.redhatworkshops.io
```

This will create user: `user-abc123`

### Removing a User

```bash
# Remove user from workshop
ansible-playbook main.yml \
  -e guid=abc123 \
  -e ACTION=remove \
  -e ocp4_workload_dynamic_user_provisioning_admin_user=admin \
  -e ocp4_workload_dynamic_user_provisioning_admin_password=your-admin-password \
  -e ocp4_workload_dynamic_user_provisioning_openshift_console_url=https://console-openshift-console.apps.cluster-lnj4s.dynamic.redhatworkshops.io
```

## Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `guid` | Workshop GUID (auto-available in AgnosticD) | `abc123` |
| `ocp4_workload_dynamic_user_provisioning_admin_user` | OpenShift admin username | `admin` |
| `ocp4_workload_dynamic_user_provisioning_admin_password` | OpenShift admin password | `password123` |
| `ocp4_workload_dynamic_user_provisioning_openshift_console_url` | OpenShift Console URL | `https://console-openshift-console.apps.cluster-lnj4s.dynamic.redhatworkshops.io` |

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

1. **Missing admin credentials**: Ensure OpenShift admin user/password are correct
2. **Workshop not deployed**: Verify REDHAT_ADS_WKS workshop is running
3. **Network connectivity**: Check routes and ingress configuration
4. **Namespace conflicts**: Ensure GUID is unique across workshops

### Debug Mode

Run with increased verbosity for troubleshooting:

```bash
ansible-playbook main.yml -vvv \
  -e guid=abc123 \
  -e ACTION=create \
  -e ocp4_workload_dynamic_user_provisioning_admin_user=admin \
  -e ocp4_workload_dynamic_user_provisioning_admin_password=password123
```

## Security Considerations

- Uses workshop-consistent password generation
- Leverages existing Keycloak admin credentials
- No hardcoded secrets or tokens
- Proper namespace isolation for multi-tenancy