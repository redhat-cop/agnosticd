# IBM InstructLab Service Role

This Ansible role automates the deployment and management of IBM InstructLab service instances on IBM Cloud. It provides complete lifecycle management including provisioning, configuration, and destruction of InstructLab resources with enterprise-grade error handling and logging.

## Features

- **Complete Lifecycle Management**: Provision and destroy InstructLab service instances
- **Idempotent Operations**: Safe to run multiple times with consistent results
- **Enterprise Error Handling**: Comprehensive retry logic and descriptive error messages
- **Terraform Integration**: Uses Terraform for robust infrastructure management
- **Resource Naming**: Consistent `instructlab-{guid}-{type}` naming pattern
- **Comprehensive Logging**: Detailed terraform logs for troubleshooting
- **Clean State Management**: Automatic state refresh and cleanup

## Requirements

- **IBM Cloud Account**: Valid IBM Cloud account with sufficient permissions
- **IBM Cloud API Key**: Service account or user API key with required roles:
  - Resource Group Editor
  - Cloud Object Storage Editor
  - InstructLab Service Manager
- **Terraform**: Automatically installed if not present (v1.51.0)
- **Ansible Collections**:
  - `community.general` (for terraform module)

## Role Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ibmcloud_api_key` | IBM Cloud API key for authentication | `your-api-key-here` |
| `ibm_realm_name` | IBM realm name for the account | `your-realm` |
| `requester_email` | Email address for the requestor | `user@example.com` |
| `guid` | Unique identifier for deployment | `user01` |
| `output_dir` | Directory for terraform files and logs | `/tmp/instructlab-deploy` |

### Optional Variables (defaults/main.yml)

| Variable | Default | Description |
|----------|---------|-------------|
| `ibmcloud_region` | `us-east` | IBM Cloud region for deployment |
| `ibmcloud_terraform_version` | `1.51.0` | Terraform version to install |
| `ibmcloud_terraform_name_prefix` | `instructlab` | Prefix for resource names |
| `ibmcloud_storage_class` | `standard` | Storage class for COS resources |
| `ibmcloud_instructlab_instance_service` | `instructlab` | InstructLab service name |
| `ibmcloud_instructlab_instance_plan` | `instructlab-pricing-plan` | Service plan for InstructLab |

## Resource Naming

All resources follow the pattern: `instructlab-{guid}-{type}`

Examples:
- Resource Group: `instructlab-user01-rg`
- Trusted Profile: `instructlab-user01-tp`
- COS Instance: `instructlab-user01-cos`
- COS Bucket: `instructlab-user01-bucket`

## Usage

### Basic Deployment

```yaml
- name: Deploy IBM InstructLab Service
  hosts: localhost
  connection: local
  become: false
  vars:
    ACTION: provision
    ibmcloud_api_key: "{{ vault_ibmcloud_api_key }}"
    ibm_realm_name: "your-realm"
    requester_email: "user@example.com"
    guid: "user01"
    output_dir: "/tmp/instructlab-{{ guid }}"
  roles:
    - agnosticd.ibm.ibm_instructlab_service
```

### Complete Lifecycle Example

```yaml
---
- name: IBM InstructLab Service Management
  hosts: localhost
  connection: local
  become: false
  vars:
    ibmcloud_api_key: "{{ vault_ibmcloud_api_key }}"
    ibm_realm_name: "your-realm"
    requester_email: "admin@company.com"
    guid: "{{ student_name | default('demo01') }}"
    output_dir: "/tmp/instructlab-{{ guid }}"
    
    # Optional customizations
    ibmcloud_region: "us-south"
    ibmcloud_terraform_name_prefix: "instructlab"
    
  tasks:
    # Provision InstructLab Service
    - name: Deploy InstructLab Service
      include_role:
        name: agnosticd.ibm.ibm_instructlab_service
      vars:
        ACTION: provision
    
    # Later: Destroy InstructLab Service
    - name: Clean up InstructLab Service
      include_role:
        name: agnosticd.ibm.ibm_instructlab_service
      vars:
        ACTION: destroy
      when: cleanup_resources | default(false)
```

### Integration with AgnosticD

```yaml
# In your AgnosticD config vars
ibmcloud_api_key: "{{ vault_ibmcloud_api_key }}"
ibm_realm_name: "your-realm"
requester_email: "{{ email }}"
guid: "{{ guid }}"
output_dir: "{{ output_dir }}"
ACTION: "{{ env_type }}"  # 'provision' or 'destroy'

# In your software playbook
- name: Manage IBM InstructLab Service
  include_role:
    name: agnosticd.ibm.ibm_instructlab_service
```

## Actions

The role supports two primary actions controlled by the `ACTION` variable:

### `ACTION: provision`
- Creates IBM Cloud resources
- Deploys InstructLab service instance
- Configures access and storage
- Provides resource information for integration

### `ACTION: destroy`
- Safely destroys all created resources
- Cleans up terraform state files
- Handles missing state gracefully
- Provides cleanup verification

## Logging and Troubleshooting

### Log Files
All operations generate detailed logs in the `output_dir`:

- `terraform_deploy.log` - Deployment terraform logs
- `terraform_destroy.log` - Destruction terraform logs
- `terraform_refresh.log` - State refresh logs (if applicable)
- `terraform.tfstate` - Terraform state file

### Common Issues

1. **Resource Naming Conflicts**
   - Use a different `guid` value
   - Run with `ACTION: destroy` first to clean up

2. **API Key Issues**
   - Verify API key has required permissions
   - Check key hasn't expired

3. **Region Availability**
   - Verify InstructLab service is available in selected region
   - Check IBM Cloud service status

4. **Quota Limits**
   - Review IBM Cloud account quotas
   - Contact IBM support for quota increases

## Dependencies

This role has no external role dependencies but requires:

- IBM Cloud account with appropriate service quotas
- Network connectivity to IBM Cloud APIs
- Sufficient disk space for terraform state and logs

## Error Handling

The role includes comprehensive error handling:

- **Retry Logic**: Automatic retries for transient failures
- **State Validation**: Terraform state refresh before operations
- **Graceful Degradation**: Continues with warnings when appropriate
- **Detailed Logging**: All operations logged for troubleshooting
- **Resource Cleanup**: Automatic cleanup on failures when possible

## Security Considerations

- **API Key Protection**: Store API keys in Ansible Vault
- **Resource Isolation**: Each deployment uses unique GUID-based naming
- **Access Control**: Uses IBM trusted profiles for secure access
- **State Security**: Terraform state contains sensitive information

## License

Apache-2.0

## Author Information

- **Patrick Rutledge** - Red Hat
- **Tony Kay** - Red Hat

This role is part of the AgnosticD project for automated cloud infrastructure deployment.

## Support

For issues and questions:
- AgnosticD Documentation: [AgnosticD Docs](https://github.com/redhat-cop/agnosticd)
- IBM Cloud Documentation: [IBM Cloud InstructLab](https://cloud.ibm.com/docs/instructlab)
- File issues: [AgnosticD Issues](https://github.com/redhat-cop/agnosticd/issues)
