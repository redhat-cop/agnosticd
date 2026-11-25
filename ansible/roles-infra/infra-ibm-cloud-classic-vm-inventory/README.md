# IBM Cloud Classic VM Inventory Role

This role extracts VM information from Terraform outputs and manages in-memory inventory for IBM Cloud Classic VMs. It processes Terraform state, creates VM metadata, and adds VMs to Ansible's in-memory inventory without creating physical inventory files.

## Purpose

- **Terraform integration**: Extracts VM information from Terraform outputs after deployment
- **Separated from deployment**: Extracted from `infra-ibm-cloud-classic-deploy-vms` for cleaner separation of concerns
- **In-memory only**: Adds hosts to Ansible's in-memory inventory instead of creating files
- **Group management**: Automatically assigns VMs to inventory groups based on tags and metadata
- **SSH testing**: Verifies SSH connectivity to deployed VMs

## Features

### Automatic Group Assignment

VMs are automatically added to multiple inventory groups:
- **Main group**: `all` (configurable via `inventory_group`)
- **OS-based**: `tag_rhel_9`, `tag_ubuntu_22`, etc.
- **Datacenter-based**: `datacenter_dal13`, `datacenter_wdc07`, etc.
- **Custom groups**: Via `ansible_group:groupname` tags

### VM Metadata

Each host gets comprehensive VM metadata as host variables:
- `vm_id`, `vm_hostname`, `vm_fqdn`
- `vm_public_ip`, `vm_private_ip`
- `vm_cores`, `vm_memory`, `vm_datacenter`
- `vm_operating_system`, `vm_status`
- `vm_private_security_group_id`, `vm_public_security_group_id`
- `vm_tags`, `vm_creation_date`
- `vm_private_vlan_id`, `vm_public_vlan_id`

### SSH Configuration

Automatically configures SSH access:
- Sets `ansible_host` to public IP
- Sets `ansible_user` and `ansible_ssh_private_key_file`
- Tests SSH connectivity and reports results

## Usage

### Basic Usage

```yaml
- name: Create VM inventory
  include_role:
    name: "infra-ibm-cloud-classic-vm-inventory"
```

### With Custom SSH Configuration

```yaml
- name: Create VM inventory
  include_role:
    name: "infra-ibm-cloud-classic-vm-inventory"
  vars:
    ssh_user: "cloud-user"
    ssh_private_key_path: "/path/to/private/key"
    inventory_group: "vms"
```

### Disable SSH Testing

```yaml
- name: Create VM inventory
  include_role:
    name: "infra-ibm-cloud-classic-vm-inventory"
  vars:
    wait_for_ssh: false
    test_ssh_connection: false
```

## Required Variables

None - the role automatically extracts VM information from Terraform outputs in the configured working directory.

## Optional Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `terraform_working_dir` | String | `{{ output_dir }}/terraform-ibm-vm-{{ guid }}` | Terraform working directory |
| `save_vm_info` | Boolean | `true` | Save VM info to JSON file |
| `ssh_user` | String | `root` | SSH username for VMs |
| `ssh_private_key_path` | String | `{{ env_authorized_key_path }}` | Path to SSH private key |
| `inventory_group` | String | `all` | Main inventory group name |
| `wait_for_ssh` | Boolean | `true` | Wait for SSH to be available |
| `test_ssh_connection` | Boolean | `true` | Test SSH connections |
| `ssh_wait_delay` | Integer | `10` | Seconds to wait before SSH checks |
| `ssh_wait_timeout` | Integer | `300` | Total SSH availability timeout |
| `ssh_connect_timeout` | Integer | `5` | Individual connection timeout |
| `ssh_retry_interval` | Integer | `2` | Seconds between connection retries |

## VM Info Format

The role automatically creates the `vm_info` variable by extracting data from Terraform outputs:

```yaml
vm_info:
  - id: "12345678"
    hostname: "web-01"
    domain: "example.com"
    fqdn: "web-01.example.com"
    public_ip: "169.62.x.x"
    private_ip: "10.x.x.x"
    datacenter: "dal13"
    cores: 2
    memory: 4096
    operating_system: "REDHAT_9_64"
    network_speed: 1000
    status: "RUNNING"
    ssh_connection: "ssh -i /path/to/key root@169.62.x.x"
    private_security_group_id: ["sg-123"]
    public_security_group_id: ["sg-456"]
    tags: ["agnosticd", "ansible_group:webservers"]
    hourly_billing: true
    creation_date: "2024-01-01T00:00:00Z"
    private_vlan_id: "vlan-123"
    public_vlan_id: "vlan-456"
```

## Integration

This role is automatically called by `infra-ibm-cloud-classic-deploy-vms` when `ACTION == 'provision'`. It can also be used independently for any IBM Cloud Classic VMs.

## Example Output

```
TASK [infra-ibm-cloud-classic-vm-inventory : Display inventory information]
ok: [localhost] => {
    "msg": [
        "In-memory inventory created successfully",
        "Total VMs added: 3",
        "Main inventory group: all",
        "Custom ansible groups detected: 2",
        "  webservers: web-01, web-02",
        "  databases: db-01",
        "Access all VMs via: ansible all -m ping",
        "Access webservers group via: ansible webservers -m ping",
        "Access databases group via: ansible databases -m ping"
    ]
}
```

## Dependencies

- IBM Cloud Classic VMs must be deployed via Terraform
- Terraform working directory must exist with valid outputs
- SSH keys must be properly configured for deployed VMs 