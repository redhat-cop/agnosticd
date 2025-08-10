# Network SSH Config Role

This role configures SSH client settings for connecting to network devices (specifically Cisco routers) from the bastion host.

## Purpose

This role is designed to work with the `control-user` role to properly configure SSH connectivity to Cisco network devices using the SSH keys managed by AgnosticD.

## What it does

1. **SSH Client Configuration**: Creates SSH config entries optimized for network devices
2. **Collection Installation**: Installs required Ansible network collections
3. **Test Files**: Creates sample inventory and playbook files for testing connectivity
4. **Key Configuration**: Uses the same SSH keys managed by the control-user role

## Variables

- `student_name`: The user who will connect to network devices (default: lab-user)
- `env_authorized_key`: The SSH key name pattern (default: "{{ guid }}key")
- `guid`: The environment GUID used in hostnames

## Dependencies

- `control-user` role (for SSH key management)
- Network devices must be configured with proper UserData for SSH key acceptance

## Usage

This role is typically run as a post-software workload:

```yaml
post_software_workloads:
  bastions:
    - showroom
    - network_ssh_config
```

## Files Created

- `/home/{{ student_name }}/.ssh/config` - SSH client configuration
- `/home/{{ student_name }}/network_inventory.yml` - Sample inventory file
- `/home/{{ student_name }}/test_network_connectivity.yml` - Test playbook

## Testing

After the role runs, you can test network connectivity:

```bash
# Test with Ansible
ansible-playbook -i network_inventory.yml test_network_connectivity.yml

# Test direct SSH
ssh cisco-rtr-1.{{ guid }}.internal
```
