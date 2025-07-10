# IBM Cloud Classic Bare Metal Resources Role (infra-ibm-cloud-classic-bm-resources)

This role provides lifecycle management for IBM Cloud Classic bare metal servers using XClarity power management capabilities.

## Features

- **Power Management**: Start, stop, and check status of bare metal servers
- **BMC Integration**: Connects to server BMC for remote management
- **Lifecycle Operations**: Supports start, stop, and status actions
- **AgnosticD Integration**: Designed for AgnosticD infrastructure workflows

## Required Variables

- `ibm_cloud_server_id`: IBM Cloud server ID for the bare metal server
- `ACTION`: The action to perform (`start`, `stop`, or `status`)

## Optional Variables

- `ibm_cloud_api_key`: IBM Cloud API key (if not already authenticated)

## Usage

### Starting Servers

```yaml
- include_role:
    name: infra-ibm-cloud-classic-bm-resources
  vars:
    ibm_cloud_server_id: "12345678"
    ACTION: "start"
```

### Stopping Servers

```yaml
- include_role:
    name: infra-ibm-cloud-classic-bm-resources
  vars:
    ibm_cloud_server_id: "12345678"
    ACTION: "stop"
```

### Checking Status

```yaml
- include_role:
    name: infra-ibm-cloud-classic-bm-resources
  vars:
    ibm_cloud_server_id: "12345678"
    ACTION: "status"
```

## How It Works

1. **Initialize**: Uses `infra-ibm-cloud-classic-bm-info` to retrieve server information
2. **Extract BMC Details**: Gets BMC hostname, username, and password from server info
3. **Power Management**: Uses `infra-redfish-power-management` to perform the requested action
4. **Report Status**: Provides feedback on the operation results

## Task Flow

- `initialize.yml`: Validates input and retrieves server BMC information
- `start.yml`: Powers on the server
- `stop.yml`: Powers off the server
- `status.yml`: Checks current power state and reports status

## Integration with AgnosticD

This role integrates with AgnosticD lifecycle management:

```yaml
# In lifecycle_redfish_baremetal.yml
- when: >-
    ACTION == 'stop'
    or ACTION == 'start'
    or ACTION == 'status'
  include_role:
    name: infra-ibm-cloud-classic-bm-resources
```

## Dependencies

- `infra-ibm-cloud-classic-bm-info`: For retrieving server information
- `infra-redfish-power-management`: For actual power operations
- IBM Cloud CLI (automatically installed by dependent roles)

## Output

When running status checks, the role provides:
- BMC connection details
- Current power state
- User-friendly status messages through `agnosticd_user_info`

## Error Handling

The role includes comprehensive validation:
- Checks for required `ibm_cloud_server_id`
- Validates BMC connection parameters
- Handles missing or invalid server information gracefully

## Example Output

```
XClarity Baremetal Server Status:

BMC Host: 192.168.1.200
Console User: console
Power Status: on

Server is currently: POWERED ON
``` 