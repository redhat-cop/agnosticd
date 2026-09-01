# Redfish Power Management Role (infra-redfish-power-management)

This role provides power management capabilities for servers using the Redfish API standard. It supports power operations, PXE boot configuration, and server monitoring through BMC connections.

## Features

- **Power Management**: Start, stop, reset, and force power off servers
- **Power Status Monitoring**: Check current power state and monitor state changes
- **PXE Boot Support**: Configure PXE boot settings and initiate network boot
- **Boot Order Management**: Check and optimize boot order to prioritize hard disk first
- **Redfish API Integration**: Uses standard Redfish API for broad server compatibility
- **Connection Validation**: Tests BMC connectivity before operations
- **Graceful Handling**: Intelligent handling of already-powered servers

## Supported Power Actions

- `status`: Check current power state
- `on`: Power on the server
- `off`: Gracefully power off the server
- `force_off`: Force immediate power off
- `reset`: Reset/restart the server

## Required Variables

- `bmc_hostname`: BMC IP address or hostname
- `bmc_username`: BMC username for authentication
- `bmc_password`: BMC password for authentication
- `power_action`: Power action to perform (status, on, off, force_off, reset)

## Optional Variables

- `enable_pxe_boot_and_reset`: Enable PXE boot and reset server (default: false)
- `check_boot_order`: Check and fix boot order to prioritize hard disk first (default: true)
- `set_boot_order_on_provision`: Set boot order during provision operations (default: true)
- `validate_certs`: Validate SSL certificates (default: false)
- `force_basic_auth`: Use basic authentication (default: true)
- `connection_timeout`: Connection timeout in seconds (default: 30)
- `power_monitor_retries`: Number of retries for power monitoring (default: 30)
- `power_monitor_delay`: Delay between power state checks in seconds (default: 5)

## Usage

### Basic Power Operations

```yaml
- include_role:
    name: infra-redfish-power-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "password123"
    power_action: "on"
```

### Check Power Status

```yaml
- include_role:
    name: infra-redfish-power-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "password123"
    power_action: "status"
```

### PXE Boot Configuration

```yaml
- include_role:
    name: infra-redfish-power-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "password123"
    enable_pxe_boot_and_reset: true
```

### Boot Order Management

```yaml
- include_role:
    name: infra-redfish-power-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "password123"
    power_action: "status"
    check_boot_order: true
```

### Skip Boot Order Check

```yaml
- include_role:
    name: infra-redfish-power-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "password123"
    power_action: "on"
    check_boot_order: false
```

### Force Power Off

```yaml
- include_role:
    name: infra-redfish-power-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "password123"
    power_action: "force_off"
```

## Task Flow

1. **Validation**: Validates required parameters and power action
2. **Connectivity**: Tests BMC connectivity using Redfish API
3. **Boot Order**: Checks and optimizes boot order to prioritize hard disk first
4. **Power Status**: Retrieves current power state
5. **Graceful Exits**: Checks for conditions requiring early exit
6. **Power Actions**: Executes requested power operations
7. **PXE Boot**: Configures PXE boot settings if enabled
8. **Monitoring**: Monitors power state changes
9. **Final Status**: Reports final power state

## Integration with AgnosticD

This role integrates with AgnosticD infrastructure workflows:

```yaml
# Used by infra-ibm-cloud-classic-bm-resources for lifecycle management
- include_role:
    name: infra-redfish-power-management
  vars:
    bmc_hostname: "{{ bmc_hostname }}"
    bmc_username: "{{ bmc_username }}"
    bmc_password: "{{ bmc_password }}"
    power_action: "{{ power_action }}"
```

## Return Values

The role sets the following facts:

- `power_status`: Current power state information
- `power_action_result`: Result of the power action performed
- `connectivity_status`: BMC connectivity test results

## Error Handling

The role includes comprehensive error handling:

- **Parameter Validation**: Checks for required BMC connection parameters
- **Power Action Validation**: Validates power action is supported
- **Connectivity Testing**: Verifies BMC is reachable before operations
- **Graceful Exits**: Handles already-powered servers appropriately
- **Timeout Handling**: Configurable timeouts for operations

## Compatibility

This role works with servers that support the Redfish API standard, including:

- Lenovo ThinkSystem servers
- Dell PowerEdge servers
- HP/HPE ProLiant servers
- IBM System servers
- Other Redfish-compliant servers

## Examples

### Complete Power-On Sequence

```yaml
- name: Power on server with monitoring
  include_role:
    name: infra-redfish-power-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "password123"
    power_action: "on"
    power_monitor_retries: 60
    power_monitor_delay: 10
```

### PXE Boot for OS Installation

```yaml
- name: Configure PXE boot and reset
  include_role:
    name: infra-redfish-power-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "password123"
    enable_pxe_boot_and_reset: true
    power_monitor_retries: 30
```

### Boot Order Management for Production Systems

```yaml
- name: Ensure hard disk boots first for production system
  include_role:
    name: infra-redfish-power-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "password123"
    power_action: "status"
    check_boot_order: true
```

## Security Considerations

- Store BMC credentials securely using Ansible Vault
- Use SSL/TLS when possible (set `validate_certs: true`)
- Limit network access to BMC interfaces
- Use strong authentication credentials

## Dependencies

- Ansible `uri` module for HTTP/HTTPS requests
- Network connectivity to BMC interface
- Redfish API support on target servers

## Troubleshooting

Common issues and solutions:

1. **Connection Timeout**: Increase `connection_timeout` value
2. **SSL Certificate Errors**: Set `validate_certs: false` for self-signed certificates
3. **Authentication Failures**: Verify BMC credentials and user permissions
4. **Power State Changes**: Adjust `power_monitor_retries` and `power_monitor_delay` 