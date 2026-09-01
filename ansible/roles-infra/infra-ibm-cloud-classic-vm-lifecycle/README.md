# IBM Cloud Classic VM Lifecycle Management Role

This AgnosticD infrastructure role manages the lifecycle of IBM Cloud Classic Virtual Machines (VMs) by reading VM information from Terraform state and using IBM Cloud CLI for power management operations.

## Features

- **VM Lifecycle Management**: Start, stop, and check status of IBM Cloud Classic VMs
- **Terraform State Integration**: Automatically discovers VMs from existing Terraform deployments
- **Action-based Operations**: Supports ACTION variable for different lifecycle operations
- **IBM Cloud CLI Integration**: Uses IBM Cloud CLI for direct VM power management
- **Intelligent Error Handling**: Detects "AlreadyHalted" conditions and treats them as success
- **Pre-operation Status Checking**: Checks VM state before operations to provide context
- **User Information**: Provides detailed status information via agnosticd_user_info

## Prerequisites

- IBM Cloud account with Classic Infrastructure access
- IBM Cloud API key with appropriate permissions
- IBM Cloud CLI installed and available in PATH
- Existing VM deployment with Terraform state in output directory
- VMs created with `infra-ibm-cloud-classic-manage-vms` role

## Required Variables

```yaml
ibm_cloud_api_key: "YOUR_IBM_CLOUD_API_KEY"
output_dir: "/path/to/output/directory"
ACTION: "start|stop|status"
```

## Usage

### Start VMs
```yaml
- name: Start IBM Cloud Classic VMs
  include_role:
    name: infra-ibm-cloud-classic-vm-lifecycle
  vars:
    ibm_cloud_api_key: "{{ ibm_cloud_api_key }}"
    output_dir: "{{ output_dir }}"
    ACTION: "start"
```

### Stop VMs
```yaml
- name: Stop IBM Cloud Classic VMs
  include_role:
    name: infra-ibm-cloud-classic-vm-lifecycle
  vars:
    ibm_cloud_api_key: "{{ ibm_cloud_api_key }}"
    output_dir: "{{ output_dir }}"
    ACTION: "stop"
```

### Check VM Status
```yaml
- name: Check IBM Cloud Classic VM Status
  include_role:
    name: infra-ibm-cloud-classic-vm-lifecycle
  vars:
    ibm_cloud_api_key: "{{ ibm_cloud_api_key }}"
    output_dir: "{{ output_dir }}"
    ACTION: "status"
```

## Command Line Usage

```bash
# Start VMs
ansible-playbook lifecycle.yml -e ACTION=start -e ibm_cloud_api_key=YOUR_API_KEY -e output_dir=/path/to/output

# Stop VMs
ansible-playbook lifecycle.yml -e ACTION=stop -e ibm_cloud_api_key=YOUR_API_KEY -e output_dir=/path/to/output

# Check status
ansible-playbook lifecycle.yml -e ACTION=status -e ibm_cloud_api_key=YOUR_API_KEY -e output_dir=/path/to/output
```

## Optional Variables

```yaml
# Verbosity level (default: 0)
verbosity: 1

# Default action if not specified
ACTION: "status"
```

## How It Works

1. **Initialize**: Validates output directory and Terraform working directory
2. **Read State**: Extracts VM information from Terraform outputs
3. **Action**: Performs the specified action using IBM Cloud CLI:
   - **Start**: Checks current state, then uses `ibmcloud sl vs power-on` for each VM
     - Handles "Already running" errors as success conditions
     - Provides detailed before/after state information
   - **Stop**: Checks current state, then uses `ibmcloud sl vs power-off` for each VM
     - Handles "AlreadyHalted" errors as success conditions
     - Provides detailed before/after state information
   - **Status**: Uses `ibmcloud sl vs detail` to get current state
4. **Report**: Provides detailed status information and completion messages

## Terraform Integration

The role reads VM information from:
- Terraform working directory: `{{ output_dir }}/terraform-ibm-vm-{{ guid }}`
- Terraform state file in the working directory
- Terraform outputs containing VM details:
  - `vm_ids`: VM instance IDs for CLI operations
  - `vm_hostnames`: VM hostnames for reporting
  - `vm_public_ips` and `vm_private_ips`: IP addresses
  - `vm_datacenters`: Datacenter locations
  - `deployment_summary`: Overall deployment information

## Dependencies

This role has no external role dependencies and works directly with:
- Terraform state files
- IBM Cloud CLI
- IBM Cloud Classic Infrastructure API

## Output

### Status Action
The status action provides detailed information about:
- VM instance IDs and hostnames
- IP addresses (public and private)
- Datacenter locations
- Current power states
- Deployment summary

### Start/Stop Actions
The start and stop actions provide:
- Per-VM operation results with initial state information
- Success/failure status for each VM (including "AlreadyHalted" and "Already running" as success)
- Detailed error analysis and recommended actions
- Total operation summary with final state confirmation

## Error Handling

The role includes validation for:
- Required API key presence
- Output directory existence
- Terraform working directory presence
- Terraform state file existence
- VM existence in Terraform state

## Security

- API keys are handled securely through environment variables
- No sensitive information is logged in debug output
- Uses IBM Cloud CLI authentication mechanisms

## Troubleshooting

### Common Issues

1. **No VMs Found**
   - Ensure `output_dir` points to a directory with Terraform state
   - Verify VMs were deployed using the `infra-ibm-cloud-classic-manage-vms` role
   - Check that Terraform deployment completed successfully

2. **API Authentication Errors**
   - Verify `ibm_cloud_api_key` has appropriate permissions
   - Check API key is not expired
   - Ensure IBM Cloud CLI is properly installed

3. **Terraform State Not Found**
   - Confirm the Terraform working directory `{{ output_dir }}/terraform-ibm-vm-{{ guid }}` exists
   - Verify `terraform.tfstate` file exists in the Terraform working directory
   - Check that the deployment was not cleaned up

4. **VM Operation Failures**
   - Verify IBM Cloud CLI is installed and accessible
   - Check that VMs still exist in IBM Cloud
   - Confirm API key has VM management permissions

5. **"AlreadyHalted" Errors on Stop Operations**
   - These are **expected and indicate success** - the VM was already stopped
   - The role automatically detects this condition and treats it as successful
   - Example error: `SoftLayer_Exception_Virtual_Guest_AlreadyHalted: Failed to halt guest as it has already been halted`
   - **No action required** - this means the target state was already achieved

6. **"Already Running" Errors on Start Operations**
   - These are **expected and indicate success** - the VM was already running
   - The role automatically detects this condition and treats it as successful
   - Example error: `SoftLayer_Exception_Virtual_Guest_AlreadyRunning: Failed to start guest as it is already running`
   - **No action required** - this means the target state was already achieved

## Integration

This role is designed to work with:
- AgnosticD lifecycle management system
- IBM Cloud Classic infrastructure
- Terraform-based VM deployments
- Existing output directory structure

## Version Compatibility

- Ansible 2.9+
- IBM Cloud Classic Infrastructure
- IBM Cloud CLI
- AgnosticD framework
- Terraform (any version that creates compatible state files) 