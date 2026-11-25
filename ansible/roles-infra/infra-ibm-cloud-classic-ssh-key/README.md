# IBM Cloud Classic SSH Key Infrastructure Role

This role manages SSH keys in IBM Cloud Classic infrastructure. It can create, update, and destroy SSH keys using the IBM Cloud CLI.

## Requirements

- IBM Cloud account with Classic Infrastructure access
- Valid IBM Cloud API key with Classic Infrastructure permissions
- SSH key pair already generated locally (using `create_ssh_provision_key` role or manually)
- IBM Cloud CLI will be automatically installed if not present

## Authentication

This role uses the IBM Cloud API key for authentication. The API key must have Classic Infrastructure permissions.

## Role Variables

### Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ibm_cloud_classic_api_key` | IBM Cloud API key with Classic Infrastructure permissions | None (required) |
| `guid` | Unique identifier for the deployment | None (required) |
| `env_authorized_key_path` | Path to the private SSH key file | None (required) |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ssh_key_name` | Name of the SSH key in IBM Cloud Classic | `{{ guid }}-ssh-key` |
| `ssh_key_label` | Label for the SSH key | `AgnosticD SSH Key for {{ guid }}` |
| `ssh_provision_key_path` | Path to the private SSH key file | `{{ env_authorized_key_path }}` |
| `ssh_provision_pubkey_path` | Path to the public SSH key file | `{{ env_authorized_key_path_pub }}` |
| `wait_for_completion` | Whether to wait for operations to complete | `true` |
| `ssh_key_tags` | Tags to apply to the SSH key | See defaults/main.yml |
| `ibm_cloud_cli_install_url` | URL for IBM Cloud CLI installation script | `https://clis.cloud.ibm.com/install/linux` |

## Dependencies

- `create_ssh_provision_key` role should be run first to generate SSH keys
- `locate_env_authorized_key` role should be run to set up key paths

## Example Usage

### In a playbook:

```yaml
- name: Create SSH key in IBM Cloud Classic
  include_role:
    name: infra-ibm-cloud-classic-ssh-key
  vars:
    ACTION: provision
    ibm_cloud_classic_api_key: "{{ ibm_cloud_classic_api_key }}"
```

### In infrastructure deployment:

```yaml
- name: Create SSH key in IBM Cloud Classic
  include_role:
    name: "infra-ibm-cloud-classic-ssh-key"
  vars:
    ACTION: provision
    ibm_cloud_classic_api_key: "{{ ibm_cloud_classic_api_key }}"
  when: 
    - instances is defined
    - instances | length > 0
```

## Destroying SSH Keys

To destroy the SSH key:

```yaml
- name: Destroy SSH key in IBM Cloud Classic
  include_role:
    name: infra-ibm-cloud-classic-ssh-key
  vars:
    ACTION: destroy
    ibm_cloud_classic_api_key: "{{ ibm_cloud_classic_api_key }}"
```

## Return Values

The role sets the following facts that can be used by other roles:

- `ssh_key_id`: The ID of the created/found SSH key
- `env_authorized_key_id`: Same as ssh_key_id (for compatibility)

## How it works

1. **CLI Installation**: Automatically installs IBM Cloud CLI if not present
2. **Authentication**: Logs in using the provided API key
3. **Key Detection**: Checks if SSH key already exists by name
4. **Key Creation**: Creates new SSH key if it doesn't exist
5. **Information Storage**: Saves key information to output directory
6. **Fact Setting**: Sets ssh_key_id fact for use by other roles

## Integration with AgnosticD

This role is designed to work with AgnosticD's infrastructure deployment patterns:

- Follows the `ACTION` variable convention (provision/destroy)
- Uses standard AgnosticD variables (`guid`, `env_authorized_key_path`, etc.)
- Integrates with the `locate_env_authorized_key` role
- Works with the existing infrastructure deployment workflows

## Error Handling

The role includes strict error handling with no fallback modes:

- **SoftLayer Plugin Required**: The role will fail if the SoftLayer plugin is not installed or available. This ensures SSH key operations can be performed reliably.
- **Variable Validation**: Validates required variables are present before proceeding
- **SSH Key File Validation**: Checks SSH key file existence and readability
- **IBM Cloud Authentication**: Verifies IBM Cloud CLI installation and API key authentication
- **Detailed Error Messages**: Provides comprehensive troubleshooting information on failures
- **Existing Key Detection**: Handles cases where SSH keys already exist or don't exist during create/destroy operations

## Security Considerations

- API key is marked with `no_log: true` to prevent logging
- SSH key information is saved with restricted permissions
- Role validates authentication before proceeding
- Cleanup removes temporary files on destruction 