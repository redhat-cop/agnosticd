# Redfish User Management Role (infra-redfish-user-management)

This role provides comprehensive user management capabilities for servers using the Redfish API standard. It supports creating, updating, deleting, and managing user accounts on BMCs with full password validation and role assignment.

## Features

- **User Lifecycle Management**: Create, update, delete, and check status of user accounts
- **Password Validation**: Comprehensive password requirements enforcement
- **Role Assignment**: Support for Administrator, Operator, ReadOnly, and PowerUser roles
- **PowerUser Role**: Custom OEM role with specific privileges for console and power management
- **Flexible Create Behavior**: Option to force password update when user already exists during create action
- **Redfish API Integration**: Uses standard Redfish API for broad server compatibility
- **Connection Validation**: Tests BMC connectivity before operations
- **Account Service Discovery**: Automatic discovery of account service capabilities

## Supported User Actions

- `create`: Create a new user account (or update existing user if `force_password_update_on_existing` is true)
- `update_password`: Update an existing user's password
- `delete`: Delete a user account
- `status`: Check user account status and information

## Supported User Roles

- `Administrator`: Full administrative privileges
- `Operator`: Operational privileges without configuration changes
- `ReadOnly`: Read-only access to system information
- `PowerUser`: Custom OEM role with console and power management access

## Required Variables

- `bmc_hostname`: BMC IP address or hostname
- `bmc_username`: BMC username for authentication
- `bmc_password`: BMC password for authentication
- `target_username`: Username to manage (default: "console")
- `target_password`: Password for create/update operations (auto-generated if not provided)
- `user_action`: Action to perform (create, update_password, delete, status)

## Optional Variables

- `user_role`: User role to assign (default: "ReadOnly")
- `enable_user`: Enable the user account (default: true)
- `force_password_update_on_existing`: Force password update if user exists during create action (default: true)
- `validate_certs`: Validate SSL certificates (default: false)
- `force_basic_auth`: Use basic authentication (default: true)
- `connection_timeout`: Connection timeout in seconds (default: 30)

## Password Requirements

The role enforces comprehensive password validation:

- **Length**: 10-32 characters
- **Character Types**: At least 2 of uppercase, lowercase, special characters
- **Required**: At least one letter and one number
- **Restrictions**: No more than 2 consecutive identical characters
- **Security**: Cannot be username or reverse of username
- **Character Set**: A-Z, a-z, 0-9, and ~`!@#$%^&*()-+={}[]|:;"'<>,?/._

## Usage

### Create a New User

```yaml
- include_role:
    name: infra-redfish-user-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "admin123"
    target_username: "console"
    target_password: "SecurePass123!"
    user_action: "create"
    user_role: "PowerUser"
    enable_user: true
```

### Update User Password

```yaml
- include_role:
    name: infra-redfish-user-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "admin123"
    target_username: "console"
    target_password: "NewSecurePass123!"
    user_action: "update_password"
```

### Check User Status

```yaml
- include_role:
    name: infra-redfish-user-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "admin123"
    target_username: "console"
    user_action: "status"
```

### Delete User Account

```yaml
- include_role:
    name: infra-redfish-user-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "admin123"
    target_username: "console"
    user_action: "delete"
```

### Auto-Generated Password

```yaml
- include_role:
    name: infra-redfish-user-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "admin123"
    target_username: "console"
    user_action: "create"
    user_role: "PowerUser"
    # target_password will be auto-generated
```

### Force Password Update on Existing User

```yaml
- include_role:
    name: infra-redfish-user-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "admin123"
    target_username: "console"
    target_password: "NewSecurePass123!"
    user_action: "create"
    user_role: "PowerUser"
    force_password_update_on_existing: true  # Force update if user exists
```

## Task Flow

1. **Validation**: Validates user action, role, and password requirements
2. **Password Validation**: Enforces comprehensive password requirements
3. **Connectivity**: Tests BMC connectivity using Redfish API
4. **Account Service**: Discovers account service capabilities
5. **User Operations**: Performs the requested user management operation
6. **PowerUser Role**: Assigns custom OEM role if PowerUser is selected
7. **Summary**: Displays operation completion summary

## PowerUser Role Details

The PowerUser role provides custom OEM privileges:

- **RemoteConsoleAndVirtualMediaAccess**: Console and virtual media management
- **RemoteServerPowerRestartAccess**: Power control capabilities

This role is ideal for automated deployment scenarios where console access and power management are required.

## Integration with AgnosticD

This role integrates with AgnosticD infrastructure workflows:

```yaml
# Used in XClarity baremetal infrastructure deployment
- include_role:
    name: infra-redfish-user-management
  vars:
    bmc_hostname: "{{ bm_server_info.remote_mgmt_ip }}"
    bmc_username: "{{ bm_server_info.remote_mgmt_user }}"
    bmc_password: "{{ bm_server_info.remote_mgmt_password }}"
    target_username: "console"
    target_password: "{{ generated_password }}"
    user_action: "create"
    user_role: "PowerUser"
```

## Return Values

The role sets the following facts:

- `user_operation_result`: Result of the user management operation
- `user_account_info`: User account information (for status operations)
- `poweruser_role_result`: Result of PowerUser role assignment
- `password_validation_result`: Result of password validation

## Error Handling

The role includes comprehensive error handling:

- **Parameter Validation**: Checks for required parameters and valid values
- **Password Validation**: Enforces password complexity requirements
- **Connectivity Testing**: Verifies BMC is reachable before operations
- **Account Service Discovery**: Handles different BMC capabilities
- **Operation Validation**: Validates operations completed successfully

## Compatibility

This role works with servers that support the Redfish API standard, including:

- Lenovo ThinkSystem servers
- Dell PowerEdge servers
- HP/HPE ProLiant servers
- IBM System servers
- Other Redfish-compliant servers

## Examples

### Complete User Lifecycle

```yaml
# Create user
- include_role:
    name: infra-redfish-user-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "admin123"
    target_username: "deployuser"
    target_password: "Deploy123!"
    user_action: "create"
    user_role: "Administrator"

# Update password
- include_role:
    name: infra-redfish-user-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "admin123"
    target_username: "deployuser"
    target_password: "NewDeploy123!"
    user_action: "update_password"

# Check status
- include_role:
    name: infra-redfish-user-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "admin123"
    target_username: "deployuser"
    user_action: "status"

# Delete user
- include_role:
    name: infra-redfish-user-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "admin123"
    target_username: "deployuser"
    user_action: "delete"
```

### PowerUser for Deployment

```yaml
- include_role:
    name: infra-redfish-user-management
  vars:
    bmc_hostname: "192.168.1.100"
    bmc_username: "admin"
    bmc_password: "admin123"
    target_username: "console"
    target_password: "{{ generated_password }}"
    user_action: "create"
    user_role: "PowerUser"
    enable_user: true
```

## Security Considerations

- Store BMC credentials securely using Ansible Vault
- Use strong passwords that meet complexity requirements
- Use SSL/TLS when possible (set `validate_certs: true`)
- Limit network access to BMC interfaces
- Regularly rotate user passwords
- Delete temporary accounts after use

## Dependencies

- Ansible `uri` module for HTTP/HTTPS requests
- Network connectivity to BMC interface
- Redfish API support on target servers
- BMC administrative privileges for user management

## Troubleshooting

Common issues and solutions:

1. **Password Validation Failures**: Ensure passwords meet complexity requirements
2. **Connection Timeout**: Increase `connection_timeout` value
3. **SSL Certificate Errors**: Set `validate_certs: false` for self-signed certificates
4. **User Creation Failures**: Check available user slots and existing users
5. **PowerUser Role Issues**: Verify BMC supports OEM role extensions
6. **Permission Errors**: Ensure BMC admin account has user management privileges 