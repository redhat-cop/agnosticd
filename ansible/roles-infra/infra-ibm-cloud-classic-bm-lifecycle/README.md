# IBM Cloud Classic Bare Metal Lifecycle Role (infra-ibm-cloud-classic-bm-lifecycle)

This role provides lifecycle management for IBM Cloud Classic bare metal servers using BMC (Baseboard Management Controller) operations through a bastion host proxy.

## Features

- **BMC-Based Power Management**: Reliable start, stop, and status operations via IPMI
- **VM Dependency Management**: Automatically manages bastion VM dependencies for BMC access
- **HAProxy Tunnel Integration**: Uses bastion host as secure proxy for BMC communication
- **Intelligent Sequencing**: Proper VM→BM start order and BM→VM stop order
- **AgnosticD Integration**: Designed for AgnosticD infrastructure workflows
- **Enhanced Reliability**: More dependable than IBM Cloud CLI power commands

## Required Variables

- `ibm_cloud_server_id`: IBM Cloud server ID for the bare metal server
- `ibm_cloud_api_key`: IBM Cloud API key with hardware management permissions
- `ACTION`: The action to perform (`start`, `stop`, or `status`)

## Usage

### Starting Servers

```yaml
- include_role:
    name: infra-ibm-cloud-classic-bm-lifecycle
  vars:
    ibm_cloud_server_id: "12345678"
    ibm_cloud_api_key: "{{ ibm_cloud_api_key }}"
    ACTION: "start"
```

### Stopping Servers

```yaml
- include_role:
    name: infra-ibm-cloud-classic-bm-lifecycle
  vars:
    ibm_cloud_server_id: "12345678"
    ibm_cloud_api_key: "{{ ibm_cloud_api_key }}"
    ACTION: "stop"
```

### Checking Status

```yaml
- include_role:
    name: infra-ibm-cloud-classic-bm-lifecycle
  vars:
    ibm_cloud_server_id: "12345678"
    ibm_cloud_api_key: "{{ ibm_cloud_api_key }}"
    ACTION: "status"
```

## How It Works

### Start Sequence (VM → BM)
1. **VM Dependency**: Ensures bastion VM is running using `infra-ibm-cloud-classic-vm-lifecycle`
2. **SSH Connectivity**: Waits for bastion SSH accessibility for BMC proxy operations
3. **BMC Power On**: Uses Redfish API calls through bastion proxy to power on bare metal server

### Stop Sequence (BM → VM)
1. **BMC Power Off**: Uses Redfish API calls through bastion proxy to power off bare metal server
2. **VM Dependency**: Stops bastion VM after BM operations complete

### Status Check
1. **VM Status**: Uses IBM Cloud CLI to check bastion VM status and exact power state
2. **BM Status**: Uses IBM Cloud CLI to check bare metal server status and infer power state from hardware status

**Note**: IBM Cloud Classic bare metal servers do not expose direct power state via CLI API. Power status is inferred from hardware status (ACTIVE = likely powered on).

### Technical Implementation
- **BMC Communication**: Redfish API calls executed via bastion host proxy
- **Proxy Tunnel**: Bastion provides secure proxy access to BMC network
- **Dependency Management**: Automatic VM lifecycle management for BM operations
- **Error Handling**: Comprehensive validation and fallback procedures

## Task Flow

### Start Operation
- `initialize.yml`: Validates input and retrieves server information
- `discover_vm_inventory.yml`: Discovers existing IBM Cloud Classic VMs and adds bastion hosts to inventory
- `start_vm_dependency.yml`: Ensures bastion VM is running for BMC access
- `wait_for_bastion_ssh.yml`: Waits for SSH connectivity to bastion
- `start_bm_via_bmc.yml`: Powers on server via Redfish API through bastion proxy

### Stop Operation  
- `initialize.yml`: Validates input and retrieves server information
- `discover_vm_inventory.yml`: Discovers existing IBM Cloud Classic VMs and adds bastion hosts to inventory
- `start_vm_dependency.yml`: Ensures bastion VM is running for BMC access
- `wait_for_bastion_ssh.yml`: Waits for SSH connectivity to bastion
- `stop_bm_via_bmc.yml`: Powers off server via Redfish API through bastion proxy
- `stop_vm_dependency.yml`: Stops bastion VM after BM operations complete

### Status Operation
- `initialize.yml`: Validates input and retrieves server information
- `discover_vm_inventory.yml`: Discovers existing IBM Cloud Classic VMs and adds bastion hosts to inventory
- `status_bm_via_cli.yml`: Checks both VM and bare metal server status via IBM Cloud CLI

## Integration with AgnosticD

This role integrates with AgnosticD lifecycle management:

```yaml
# In lifecycle_redfish_baremetal.yml
- when: >-
    ACTION == 'stop'
    or ACTION == 'start'
    or ACTION == 'status'
  include_role:
    name: infra-ibm-cloud-classic-bm-lifecycle
```

## Dependencies

- `infra-ibm-cloud-classic-bm-info`: For retrieving server information including BMC credentials
- `infra-ibm-cloud-classic-vm-lifecycle`: For managing bastion VM dependencies (start/stop operations only)
- **Bastion Host**: Running VM with proxy configured for BMC access (start/stop operations only)
- **SSH Access**: Port 22 connectivity to bastion host for Redfish API calls (start/stop operations only)
- **BMC Network**: Bastion proxy must route to BMC management network (start/stop operations only)

**Note**: Status operations use IBM Cloud CLI directly and have no bastion or VM dependencies.

## Output

When running status checks, the role provides:
- **VM (Bastion) Status**: ID, hostname, IPs, CPU/memory, power state
- **BM Server Status**: ID, hostname, datacenter, IPs, hardware specs
- Current power state and hardware status for both systems
- Operating system information
- Comprehensive infrastructure overview
- User-friendly status messages through `agnosticd_user_info`

## Power Management Considerations

### Power State Detection Limitations

**IBM Cloud Classic API Limitations**: 
- **VM Power State**: Exposed directly via `powerState.keyName` field (RUNNING/HALTED)
- **BM Power State**: NOT exposed via IBM Cloud CLI API - must be inferred from hardware status

**BM Power State Inference**:
- `ACTIVE` hardware status → Likely powered on 🟢
- `PROVISIONING` hardware status → Boot/provisioning in progress ⏳ 
- `MAINTENANCE` hardware status → Under maintenance 🔧
- Other statuses → Power state unknown ⚠️

**For Exact BM Power Status**: Use BMC/Redfish API operations (start/stop actions) which provide real power state through bastion proxy.

### Known Issues with Stop Operations

Some IBM Cloud Classic bare metal servers may not respond to remote power-off commands even when the command appears to succeed. This can happen due to:

- **Server Configuration**: Power management disabled or restricted in server settings
- **Running Workloads**: Critical services preventing graceful shutdown
- **BMC/IPMI Issues**: Baseboard management controller not responding properly
- **Policy Restrictions**: IBM Cloud policies preventing remote power control

### Troubleshooting BMC Operations

When BMC operations fail, check these common issues:

#### 1. **Bastion VM Dependency Issues**
- **Bastion not running**: Ensure bastion VM is powered on
- **SSH connectivity**: Verify SSH access to bastion host (port 22)
- **Proxy service**: Check proxy service is running on bastion for BMC routing

#### 2. **BMC Communication Problems**
- **Network routing**: Verify bastion proxy routes to BMC management network
- **BMC credentials**: Check management username/password are correct
- **BMC responsiveness**: BMC may need time to respond to Redfish API calls
- **HTTPS connectivity**: Ensure bastion can reach BMC via HTTPS

#### 3. **Power Operation Failures**
- **Manual verification**: Check status via Redfish API calls on bastion
- **Alternative methods**: Use server console via IBM Cloud web interface
- **Support escalation**: Submit IBM Cloud support ticket with BMC details
- **Direct server access**: SSH to server and run `sudo shutdown -h now`

#### 4. **Dependency Sequence Issues**
- **Start problems**: VM must be running before BM operations (VM→BM)
- **Stop problems**: BM should be stopped before VM (BM→VM)
- **Status checks**: VM status affects BMC proxy availability

### Manual BMC Commands

If the role fails, you can manually execute Redfish API calls on the bastion:

```bash
# Check power status
curl -k -u <bmc_user>:<bmc_pass> -X GET https://<bmc_ip>/redfish/v1/Systems/1

# Power on
curl -k -u <bmc_user>:<bmc_pass> -X POST https://<bmc_ip>/redfish/v1/Systems/1/Actions/ComputerSystem.Reset \
  -H "Content-Type: application/json" \
  -d '{"ResetType": "On"}'

# Power off (graceful shutdown)
curl -k -u <bmc_user>:<bmc_pass> -X POST https://<bmc_ip>/redfish/v1/Systems/1/Actions/ComputerSystem.Reset \
  -H "Content-Type: application/json" \
  -d '{"ResetType": "GracefulShutdown"}'

# Force power off (if needed)
curl -k -u <bmc_user>:<bmc_pass> -X POST https://<bmc_ip>/redfish/v1/Systems/1/Actions/ComputerSystem.Reset \
  -H "Content-Type: application/json" \
  -d '{"ResetType": "ForceOff"}'
```

### Start Operation Considerations

Power-on operations may take time to complete due to:

- **Boot Process**: Servers may take 5-15 minutes to fully boot and show ACTIVE status
- **Hardware Initialization**: BIOS/UEFI and hardware component initialization
- **Operating System Load**: OS boot process and service startup
- **Network Configuration**: Network interfaces and routing setup

### Smart Operation Features

Both start and stop operations include intelligent behavior:

- **Pre-operation Status Check**: Verifies current state before executing commands
- **Skip Unnecessary Operations**: Won't start already ACTIVE servers or stop already INACTIVE servers
- **Wait Periods**: Appropriate wait times for operations to take effect (15s for start, 10s for stop)
- **Verification**: Post-operation status checks to confirm success
- **Manual Guidance**: Provides clear instructions for manual intervention when needed

### Power Commands Used

- **Status Check**: `GET https://<bmc_ip>/redfish/v1/Systems/1`
- **Start**: `POST https://<bmc_ip>/redfish/v1/Systems/1/Actions/ComputerSystem.Reset` with `{"ResetType": "On"}`
- **Stop**: `POST https://<bmc_ip>/redfish/v1/Systems/1/Actions/ComputerSystem.Reset` with `{"ResetType": "GracefulShutdown"}`
- **Manual Force-off**: `POST https://<bmc_ip>/redfish/v1/Systems/1/Actions/ComputerSystem.Reset` with `{"ResetType": "ForceOff"}` (user-initiated when needed)

All commands executed on bastion host through SSH delegation for secure proxy access.

## Error Handling

The role includes comprehensive validation:
- Checks for required `ibm_cloud_server_id`
- Validates `ibm_cloud_api_key` presence
- Handles IBM Cloud CLI command failures gracefully
- Verifies power state changes after operations
- Provides detailed error messages for troubleshooting
- Offers manual alternatives when power commands don't take effect

## Example Output

```
🏗️ IBM Cloud Classic Infrastructure Status:

🖥️ Virtual Machine (Bastion):
VM ID: 151802381
Hostname: bastion-aaaa
FQDN: bastion-aaaa.example.com
Public IP: 169.62.251.23
Private IP: 10.73.77.235
CPU: 1 cores
Memory: 2048 MB
Power State: HALTED
VM Status: 🔴 STOPPED

⚙️ Bare Metal Server:
Server ID: 3389586
Hostname: dal13-bm02
FQDN: dal13-bm02.example.com
Datacenter: dal13
Public IP: 169.62.251.20
Private IP: 10.73.77.224

🔧 Hardware Details:
CPU: 20 cores
Memory: 192 GB
OS: Ubuntu 20.04 LTS

⚡ Power Status:
Current State: Inferred from hardware status
Status: 🟢 LIKELY POWERED ON (Hardware Status: ACTIVE)
Method: IBM Cloud CLI (direct API access)

📊 Hardware Status:
Overall Status: ACTIVE
System Health: ✅ Active and operational

🔗 Infrastructure Overview:
- VM provides BMC proxy access for BM power operations
- Status operations use direct IBM Cloud CLI (no dependencies)
- Both VM and BM can be managed independently via their respective APIs
``` 