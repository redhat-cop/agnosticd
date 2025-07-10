# infra-ibm-cloud-classic-bm-info

This role retrieves information about IBM Cloud Classic bare metal servers including IP addresses, VLAN information, MAC addresses, and remote management details.

## Requirements

- IBM Cloud CLI installed (role will install it if not present)
- Valid IBM Cloud API key with Classic Infrastructure permissions
- Server ID for the bare metal server to query

## Role Variables

### Required Variables (must be passed as extra vars)
- `ibm_cloud_api_key`: IBM Cloud API key with Classic Infrastructure permissions
- `ibm_cloud_server_id`: ID of the bare metal server to query

### Optional Variables
- `display_results`: Whether to display results in debug output (default: true)
- `save_to_file`: Whether to save results to file (default: false) 
- `output_file`: Output file path if save_to_file is true (default: "bm_server_info.json")
- `output_dir`: Output directory for temporary files (default: "/tmp/{{ guid | default('agnosticd') }}")

## Dependencies

None

## Example Playbook

```yaml
- name: Get bare metal server information
  hosts: localhost
  vars:
    ibm_cloud_api_key: "{{ vault_ibm_cloud_api_key }}"
    ibm_cloud_server_id: "1234567"
  roles:
    - role: infra-ibm-cloud-classic-bm-info
```

## Output

The role creates a `bm_server_info` fact containing:
- `server_id`: The server ID
- `hostname`: Server hostname (falls back to server_id if not available)
- `datacenter`: Datacenter name
- `public_ip`: Public IP address
- `private_ip`: Private IP address  
- `public_vlan_id`: Public VLAN ID
- `private_vlan_id`: Private VLAN ID
- `public_mac_address`: Public interface MAC address
- `private_mac_address`: Private interface MAC address
- `remote_mgmt_ip`: Remote management IP address
- `remote_mgmt_user`: Remote management username
- `remote_mgmt_password`: Remote management password

## License

GPL-3.0+

## Author Information

Created for AgnosticD project 