# IBM Cloud Classic VM Infrastructure Role

This AgnosticD infrastructure role manages multiple Virtual Machines (VMs) in IBM Cloud Classic infrastructure using Terraform templates.

## Features

- **Multi-VM Deployment**: Deploy multiple VMs in a single operation
- **VM Deployment**: Creates VMs using Terraform templates from `~/create-vm-ibm-cloud`
- **VM Destruction**: Cleanly destroys VMs and associated resources
- **Inventory Creation**: Generates comprehensive Ansible inventory for deployed VMs
- **Security Groups**: Configures firewall rules for VM access
- **SSH Testing**: Validates SSH connectivity to deployed VMs
- **Automatic Setup**: Installs Terraform if not present (configurable version)
- **Flexible Configuration**: Each VM can have individual specifications and settings

## Prerequisites

- IBM Cloud account with Classic Infrastructure access
- IBM Cloud API key
- SSH key pair for VM access
- Terraform templates in `~/create-vm-ibm-cloud`

## Required Variables

```yaml
ibm_cloud_api_key: "YOUR_IBM_CLOUD_API_KEY"
output_dir: "/tmp"
security_groups:
  - name: "web"
    rules:
      - name: "http"
        description: "Allow HTTP traffic"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 80
        to_port: 80
        protocol: "tcp"
        cidr: "0.0.0.0/0"
      - name: "https"
        description: "Allow HTTPS traffic"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 443
        to_port: 443
        protocol: "tcp"
        cidr: "0.0.0.0/0"
  - name: "db"
    rules:
      - name: "mysql"
        description: "Allow MySQL traffic from internal network"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 3306
        to_port: 3306
        protocol: "tcp"
        cidr: "10.0.0.0/8"
  - name: "ssh"
    rules:
      - name: "ssh"
        description: "Allow SSH access"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 22
        to_port: 22
        protocol: "tcp"
        cidr: "0.0.0.0/0"
  - name: "egress"
    rules:
      - name: "tcp_out"
        description: "Allow outbound TCP traffic"
        rule_type: "egress"
        ether_type: "IPv4"
        protocol: "tcp"
        cidr: "0.0.0.0/0"
instances:
  - name: "web"
    datacenter: "dal13"
    count: 3  # Creates web-01, web-02, web-03
    security_groups: ["web", "ssh", "egress"]  # Multiple security groups
  - name: "db"
    datacenter: "wdc07"
    count: 2  # Creates db-01, db-02
    cores: 4
    memory: 8192
    security_groups: ["db", "ssh", "egress"]   # Multiple security groups
```

## VM Count Configuration

Each instance can specify a `count` parameter to create multiple VMs of the same type:

```yaml
instances:
  - name: "web"
    datacenter: "dal13"
    count: 3  # Creates web-01, web-02, web-03
  - name: "db"
    datacenter: "wdc07"
    count: 2  # Creates db-01, db-02
```

**Key Points:**
- If `count` is not specified, defaults to 1 VM
- VM names are automatically suffixed with `-01`, `-02`, etc.
- Each VM in the count shares the same configuration
- `count` must be a positive integer

## Security Group Configuration

Security groups use a structured format with named groups and descriptive rules:

### Security Group Structure

```yaml
security_groups:
  - name: "group_name"
    rules:
      - name: "rule_name"
        description: "Rule description"
        rule_type: "ingress" or "egress"
        ether_type: "IPv4"
        from_port: 80        # Optional for TCP/UDP
        to_port: 80          # Optional for TCP/UDP
        protocol: "tcp"      # tcp, udp, icmp
        cidr: "0.0.0.0/0"    # CIDR block
```

**Field Reference:**
- `name`: Security group name (referenced by instances)
- `rules`: List of security rules for this group
  - `name`: Descriptive name for the rule
  - `description`: Human-readable description
  - `rule_type`: "ingress" (inbound) or "egress" (outbound)
  - `ether_type`: "IPv4" (IPv6 not currently supported)
  - `from_port`: Starting port number (TCP/UDP only)
  - `to_port`: Ending port number (TCP/UDP only)
  - `protocol`: "tcp", "udp", or "icmp"
  - `cidr`: CIDR notation for allowed IP ranges

You can configure security groups in two ways:

### 1. Global Security Group Definitions

Define reusable security groups that can be referenced by name:

```yaml
security_groups:
  - name: "web"
    rules:
      - name: "http"
        description: "Allow HTTP traffic"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 80
        to_port: 80
        protocol: "tcp"
        cidr: "0.0.0.0/0"
      - name: "https"
        description: "Allow HTTPS traffic"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 443
        to_port: 443
        protocol: "tcp"
        cidr: "0.0.0.0/0"
  - name: "db"
    rules:
      - name: "mysql"
        description: "Allow MySQL traffic from internal network"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 3306
        to_port: 3306
        protocol: "tcp"
        cidr: "10.0.0.0/8"
  - name: "ssh"
    rules:
      - name: "ssh"
        description: "Allow SSH access"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 22
        to_port: 22
        protocol: "tcp"
        cidr: "0.0.0.0/0"
  - name: "egress"
    rules:
      - name: "tcp_out"
        description: "Allow outbound TCP traffic"
        rule_type: "egress"
        ether_type: "IPv4"
        protocol: "tcp"
        cidr: "0.0.0.0/0"
      - name: "udp_out"
        description: "Allow outbound UDP traffic"
        rule_type: "egress"
        ether_type: "IPv4"
        protocol: "udp"
        cidr: "0.0.0.0/0"

instances:
  - name: "web"
    datacenter: "dal13"
    security_group: "web"  # Single security group reference
  - name: "db"
    datacenter: "dal13"
    security_groups: ["db", "ssh", "egress"]  # Multiple security groups
  - name: "app"
    datacenter: "dal13"
    security_groups: ["web", "db", "ssh", "egress"]  # Combine multiple groups
```

### 2. Multiple Global Security Groups

Combine multiple global security groups for flexible configurations:

```yaml
security_groups:
  - name: "web"
    rules:
      - name: "http"
        description: "Allow HTTP traffic"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 80
        to_port: 80
        protocol: "tcp"
        cidr: "0.0.0.0/0"
  - name: "db"
    rules:
      - name: "mysql"
        description: "Allow MySQL traffic from internal network"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 3306
        to_port: 3306
        protocol: "tcp"
        cidr: "10.0.0.0/8"
  - name: "ssh"
    rules:
      - name: "ssh"
        description: "Allow SSH access"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 22
        to_port: 22
        protocol: "tcp"
        cidr: "0.0.0.0/0"
  - name: "egress"
    rules:
      - name: "tcp_out"
        description: "Allow outbound TCP traffic"
        rule_type: "egress"
        ether_type: "IPv4"
        protocol: "tcp"
        cidr: "0.0.0.0/0"

instances:
  - name: "web"
    datacenter: "dal13"
    security_groups: ["web", "ssh", "egress"]  # Web server with SSH and egress
  - name: "db"
    datacenter: "dal13"
    security_groups: ["db", "ssh", "egress"]   # Database with SSH and egress
  - name: "app"
    datacenter: "dal13"
    security_groups: ["web", "db", "ssh", "egress"]  # App server with web + db access
```

### 3. Inline Security Group Rules

Define security group rules directly in the instance:

```yaml
instances:
  - name: "web"
    datacenter: "dal13"
    security_group_rules:
      - name: "http"
        description: "Allow HTTP traffic"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 80
        to_port: 80
        protocol: "tcp"
        cidr: "0.0.0.0/0"
      - name: "https"
        description: "Allow HTTPS traffic"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 443
        to_port: 443
        protocol: "tcp"
        cidr: "0.0.0.0/0"
  - name: "db"
    datacenter: "dal13"
    security_group_rules:
      - name: "mysql"
        description: "Allow MySQL traffic from internal network"
        rule_type: "ingress"
        ether_type: "IPv4"
        from_port: 3306
        to_port: 3306
        protocol: "tcp"
        cidr: "10.0.0.0/8"
```

**Key Points:**
- Use `security_group: "name"` to reference a single global security group
- Use `security_groups: ["name1", "name2"]` to reference multiple global security groups
- Use `security_group_rules: [...]` for inline rules
- If none are specified, defaults to global security group rules
- Multiple security groups are merged - rules from all groups are combined
- Global security groups are more maintainable for reused configurations
- Inline rules are better for unique, one-off security requirements
- Use `create_security_group: false` to disable security group creation for an instance

**Priority Order:**
1. `security_groups: [...]` (multiple global groups - highest priority)
2. `security_group: "name"` (single global group)
3. `security_group_rules: [...]` (inline rules)
4. Default security group rules (fallback)

## VLAN Configuration

By default, IBM Cloud will automatically assign public and private VLANs if not specified. You can optionally provide specific VLAN IDs:

```yaml
private_vlan_id: 12345  # Optional
public_vlan_id: 54321   # Optional
```

If you need to use existing VLANs or have specific networking requirements, provide the VLAN IDs as extra variables.

## Output Directory Configuration

By default, Terraform files and outputs are stored in `/tmp`. You can specify a custom output directory:

```yaml
output_dir: "/path/to/custom/directory"
```

This affects:
- Terraform working directory location
- VM information output files
- Terraform state files

## Usage

### Deploy VMs

```bash
# Deploy VMs with extra vars file
ansible-playbook playbook.yml -e ACTION=provision \
  -e @vm_vars.yml

# Where vm_vars.yml contains:
# ibm_cloud_api_key: "YOUR_API_KEY"
# output_dir: "/tmp"
# security_groups:
#   web:
#     - direction: "ingress"
#       ether_type: "IPv4"
#       port_range_min: 80
#       port_range_max: 80
#       protocol: "tcp"
#       remote_ip: "0.0.0.0/0"
#   db:
#     - direction: "ingress"
#       ether_type: "IPv4"
#       port_range_min: 3306
#       port_range_max: 3306
#       protocol: "tcp"
#       remote_ip: "10.0.0.0/8"
#   ssh:
#     - direction: "ingress"
#       ether_type: "IPv4"
#       port_range_min: 22
#       port_range_max: 22
#       protocol: "tcp"
#       remote_ip: "0.0.0.0/0"
#   egress:
#     - direction: "egress"
#       ether_type: "IPv4"
#       protocol: "tcp"
#       remote_ip: "0.0.0.0/0"
# instances:
#   - name: "web"
#     datacenter: "dal13"
#     count: 3
#     security_groups: ["web", "ssh", "egress"]
#   - name: "db"
#     datacenter: "wdc07"
#     count: 2
#     cores: 4
#     memory: 8192
#     security_groups: ["db", "ssh", "egress"]
```

### Destroy VM

```bash
ansible-playbook playbook.yml -e ACTION=destroy \
  -e terraform_working_dir=/tmp/terraform-ibm-vm-guid
# Or use custom output directory
ansible-playbook playbook.yml -e ACTION=destroy \
  -e output_dir=/custom/path \
  -e terraform_working_dir=/custom/path/terraform-ibm-vm-guid
```

## Default Configuration

### VM Specifications
- **Operating System**: RHEL 9 (64-bit)
- **CPU Cores**: 2
- **Memory**: 4096 MB
- **Disk**: 25 GB local disk
- **Network**: 1 Gbps, public and private
- **Billing**: Hourly

### Security Groups
Default firewall rules (used when not specified per instance) allow:
- SSH inbound (port 22)
- All outbound traffic (TCP, UDP, ICMP)

Each instance can override these defaults with its own security group rules.

## Customization

### VM Configuration

```yaml
# VM specifications
cores: 4
memory: 8192
disks: [25, 100]  # Multiple disks
image: "UBUNTU_22_64"

# Network settings
network_speed: 10000  # 10 Gbps
private_network_only: false
```

### Security Groups

Security groups are now configured per-instance. See the "Security Group Configuration" section above for details.

### SSH Configuration

```yaml
ssh_user: "ubuntu"
ssh_private_key_path: "/path/to/private/key"
```

### VM Tagging

VM tags are configured per-instance to provide better resource organization and management:

```yaml
instances:
  - name: "web-server"
    datacenter: "dal13"
    tags:
      - "agnosticd"
      - "web-server"
      - "production"
      - "team-alpha"
  - name: "db-server"
    datacenter: "dal13"
    tags:
      - "agnosticd"
      - "database"
      - "mysql"
      - "production"
```

**Key Points:**
- Tags are specified per-instance using the `tags` field
- Each instance can have its own unique set of tags
- Tags are useful for resource organization, billing, and management
- Tags are passed directly to IBM Cloud Classic infrastructure

### Root Filesystem Sizing and Additional Disks

The root filesystem size for VMs can be configured using the `rootfs_size` parameter, which specifies the size in GB. Additional disks beyond the root filesystem can be specified using the `additional_disks` array.

```yaml
instances:
  - name: "web-server"
    datacenter: "dal13"
    rootfs_size: 50  # 50GB root filesystem
    tags:
      - "agnosticd"
      - "web-server"
  - name: "db-server"
    datacenter: "dal13"
    rootfs_size: 100  # 100GB root filesystem for database
    additional_disks: [200, 500]  # Additional 200GB and 500GB disks
    tags:
      - "agnosticd"
      - "database"
  - name: "storage-server"
    datacenter: "dal13"
    rootfs_size: 50  # 50GB root filesystem
    additional_disks: [500, 1000]  # 500GB + 1TB additional disks
    tags:
      - "agnosticd"
      - "storage"
```

**Key Points:**
- Root filesystem size is specified per-instance using the `rootfs_size` field
- Default value is 25GB if not specified
- Additional disks are specified using the `additional_disks` array
- The `additional_disks` array contains disk sizes in GB beyond the root filesystem
- Internally converted to a single `disks` array for IBM Cloud Classic (rootfs_size as first disk + additional_disks)
- Can be set to any size (in GB) supported by IBM Cloud
- Useful for applications with different storage requirements

### Terraform Version

By default, the role downloads and installs Terraform 1.5.7 for Linux AMD64. You can specify a different version by setting the `terraform_download_url` variable:

```yaml
terraform_download_url: "https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip"
```

## Inventory Groups

Deployed VMs are automatically added to these inventory groups:
- `all` (default group)
- `tag_<operating_system>` (e.g., `tag_rhel-9-64`)
- `datacenter_<datacenter>` (e.g., `datacenter_dal13`)

## File Structure

```
ansible/roles-infra/infra-ibm-cloud-classic-vm/
├── tasks/
│   ├── main.yml                 # Main entry point
│   ├── pre_checks.yml           # Validation and setup
│   ├── terraform_deploy.yml     # VM deployment
│   ├── terraform_destroy.yml    # VM destruction
│   └── create_inventory.yml     # Inventory creation
├── templates/
│   ├── terraform.tfvars.j2      # Terraform variables
│   └── inventory.j2             # Ansible inventory
├── defaults/
│   └── main.yml                 # Default variables
└── README.md                    # This documentation
```

## Variables Reference

### Required Variables

- `ibm_cloud_api_key`: IBM Cloud API key
- `output_dir`: Directory for terraform files and outputs
- `domain`: VM domain name (no default - must be provided)
- `instances`: List of VM configurations (each VM must have `name` and `datacenter`)

### Instance Configuration

Each instance in the `instances` list supports:
- `name`: VM name prefix (required)
- `datacenter`: IBM Cloud datacenter (required)
- `count`: Number of VMs to create (optional, default: 1)
- `security_group`: Reference to single global security group by name (optional)
- `security_groups`: List of global security group names to combine (optional)
- `security_group_rules`: Security group rules for this instance (optional)
- `create_security_group`: Whether to create security group (optional, default: true)
- `tags`: List of tags to apply to this instance (optional)
- `rootfs_size`: Root filesystem size in GB (optional, default: 25)
- `additional_disks`: Additional disk sizes in GB beyond root filesystem (optional, default: [])
- All other VM configuration options (cores, memory, etc.)

### Optional Variables
- `ACTION`: provision or destroy (default: provision)
- `region`: IBM Cloud region (default: us-south)
- `private_vlan_id`: Private VLAN ID (default: auto-assigned by IBM Cloud)
- `public_vlan_id`: Public VLAN ID (default: auto-assigned by IBM Cloud)
- `image`: Operating system (default: REDHAT_9_64)
- `cores`: CPU cores (default: 2)
- `memory`: Memory in MB (default: 4096)
- `rootfs_size`: Root filesystem size in GB (default: 25)
- `additional_disks`: Additional disk sizes in GB beyond root filesystem (default: [])
- `network_speed`: Network speed in Mbps (default: 1000)
- `hourly_billing`: Use hourly billing (default: true)
- `ssh_user`: SSH username (default: root)
- `ssh_private_key_path`: SSH private key path (default: ~/.ssh/id_rsa)
- `inventory_group`: Inventory group name (default: all)
- `wait_for_ssh`: Wait for SSH availability (default: true)
- `test_ssh_connection`: Test SSH connection (default: true)
- `terraform_download_url`: URL for Terraform download (default: https://releases.hashicorp.com/terraform/1.5.7/terraform_1.5.7_linux_amd64.zip)
- `security_groups`: Dictionary of named security group definitions that can be referenced by instances
- `create_security_group`: Global default for creating security groups (default: true)
- `security_group_rules`: Global default security group rules (used when not specified per instance)

### DNS Configuration Variables

- `create_dns_records`: Whether to create Route53 DNS records (default: false)
- `route53_aws_access_key_id`: AWS access key ID for Route53 (required if create_dns_records is true)
- `route53_aws_secret_access_key`: AWS secret access key for Route53 (required if create_dns_records is true)
- `aws_region`: AWS region for Route53 (default: us-east-1)
- `route53_aws_zone_id`: Route53 hosted zone ID (auto-discovered from cluster_dns_zone if not provided)
- `cluster_dns_zone`: DNS domain for Route53 records (required if create_dns_records is true)
- `dns_ttl`: TTL for DNS records in seconds (default: 300)

**Auto-Discovery Feature**: The role automatically discovers the Route53 hosted zone ID for your `cluster_dns_zone` domain. The discovery process supports pagination and will retrieve all hosted zones in your account, making it suitable for accounts with many zones. If a hosted zone exists for your domain, `route53_aws_zone_id` will be set automatically. You only need to manually provide `route53_aws_zone_id` if auto-discovery fails or you want to use a different zone.

### Terraform Logging Configuration Variables

- `terraform_enable_logging`: Enable comprehensive Terraform logging (default: true)
- `terraform_log_level`: Terraform log level (default: "INFO", options: TRACE, DEBUG, INFO, WARN, ERROR)

**Terraform Logging Features**:
- **Comprehensive Logging**: Captures all Terraform operations (init, plan, apply, destroy) with timestamps
- **Structured Logs**: Individual log files for each operation plus master log combining all operations
- **Configurable Verbosity**: Adjust log level from ERROR (minimal) to TRACE (maximum detail)
- **Centralized Storage**: All logs stored in `{{ output_dir }}/terraform-logs/` directory
- **Easy Monitoring**: Use `tail -f {{ output_dir }}/terraform-logs/terraform-master-*.log` to monitor progress

**Log Files Created**:
- `terraform-master-TIMESTAMP.log`: Combined log with all operations
- `terraform-init-TIMESTAMP.log`: Terraform initialization
- `terraform-plan-TIMESTAMP.log`: Terraform planning
- `terraform-apply-TIMESTAMP.log`: Terraform application
- `terraform-state-TIMESTAMP.log`: State checking
- `terraform-verify-TIMESTAMP.log`: Deployment verification
- `terraform-destroy-*-TIMESTAMP.log`: Destroy operations (when applicable)

## Outputs

After successful deployment, the role provides:
- VM metadata in `vm_info` variable
- Ansible inventory groups
- SSH connection details
- VM information saved to `vm_info.json`
- DNS records (if DNS is enabled)

## Error Handling

The role includes comprehensive error handling:
- Validates required variables
- Installs Terraform if missing
- Checks Terraform state before operations
- Provides clear error messages

## Examples

### Basic VM Deployment (Auto-assigned VLANs)
```yaml
- name: Deploy IBM Cloud Classic VMs
  include_role:
    name: infra-ibm-cloud-classic-vm
  vars:
    ACTION: provision
    ibm_cloud_api_key: "{{ vault_ibm_cloud_api_key }}"
    output_dir: "/tmp"
    instances:
      - name: "web-server"
        datacenter: "dal13"
        tags:
          - "agnosticd"
          - "web-server"
```

### VM Deployment with DNS Records (Auto-Discovery)
```yaml
- name: Deploy IBM Cloud Classic VMs with Route53 DNS
  include_role:
    name: infra-ibm-cloud-classic-vm
  vars:
    ACTION: provision
    ibm_cloud_api_key: "{{ vault_ibm_cloud_api_key }}"
    output_dir: "/tmp"
    create_dns_records: true
    route53_aws_access_key_id: "{{ vault_aws_access_key_id }}"
    route53_aws_secret_access_key: "{{ vault_aws_secret_access_key }}"
    cluster_dns_zone: "example.com"  # Zone ID auto-discovered
    dns_ttl: 300
    instances:
      - name: "web-server"
        datacenter: "dal13"
        tags:
          - "agnosticd"
          - "web-server"
```

### VM Deployment with Enhanced Terraform Logging
```yaml
- name: Deploy IBM Cloud Classic VMs with detailed logging
  include_role:
    name: infra-ibm-cloud-classic-vm
  vars:
    ACTION: provision
    ibm_cloud_api_key: "{{ vault_ibm_cloud_api_key }}"
    output_dir: "/tmp"
    # Enhanced logging configuration
    terraform_enable_logging: true
    terraform_log_level: "DEBUG"  # More verbose logging
    instances:
      - name: "debug-server"
        datacenter: "dal13"
        tags:
          - "agnosticd"
          - "debug-server"
```

### VM Deployment with Minimal Logging
```yaml
- name: Deploy IBM Cloud Classic VMs with minimal logging
  include_role:
    name: infra-ibm-cloud-classic-vm
  vars:
    ACTION: provision
    ibm_cloud_api_key: "{{ vault_ibm_cloud_api_key }}"
    output_dir: "/tmp"
    # Minimal logging configuration
    terraform_enable_logging: true
    terraform_log_level: "ERROR"  # Only log errors
    instances:
      - name: "prod-server"
        datacenter: "dal13"
        tags:
          - "agnosticd"
          - "production"
```

### Monitoring Terraform Progress
```bash
# Monitor live progress during deployment
tail -f /tmp/terraform-logs/terraform-master-*.log

# Check specific operation logs
tail -f /tmp/terraform-logs/terraform-apply-*.log

# View all terraform logs
ls -la /tmp/terraform-logs/

# Search for errors in logs
grep -i "error" /tmp/terraform-logs/terraform-master-*.log
```

### Multi-VM Deployment with Multiple Security Groups
```yaml
- name: Deploy multiple VMs with multiple security groups
  include_role:
    name: infra-ibm-cloud-classic-vm
  vars:
    ACTION: provision
    ibm_cloud_api_key: "{{ vault_ibm_cloud_api_key }}"
    output_dir: "/tmp"
    security_groups:
      - name: "web"
        rules:
          - name: "http"
            description: "Allow HTTP traffic"
            rule_type: "ingress"
            ether_type: "IPv4"
            from_port: 80
            to_port: 80
            protocol: "tcp"
            cidr: "0.0.0.0/0"
          - name: "https"
            description: "Allow HTTPS traffic"
            rule_type: "ingress"
            ether_type: "IPv4"
            from_port: 443
            to_port: 443
            protocol: "tcp"
            cidr: "0.0.0.0/0"
      - name: "db"
        rules:
          - name: "mysql"
            description: "Allow MySQL traffic from internal network"
            rule_type: "ingress"
            ether_type: "IPv4"
            from_port: 3306
            to_port: 3306
            protocol: "tcp"
            cidr: "10.0.0.0/8"
      - name: "ssh"
        rules:
          - name: "ssh"
            description: "Allow SSH access"
            rule_type: "ingress"
            ether_type: "IPv4"
            from_port: 22
            to_port: 22
            protocol: "tcp"
            cidr: "0.0.0.0/0"
      - name: "egress"
        rules:
          - name: "tcp_out"
            description: "Allow outbound TCP traffic"
            rule_type: "egress"
            ether_type: "IPv4"
            protocol: "tcp"
            cidr: "0.0.0.0/0"
    instances:
      - name: "web"
        datacenter: "dal13"
        count: 3  # Creates web-01, web-02, web-03
        security_groups: ["web", "ssh", "egress"]
        tags:
          - "agnosticd"
          - "web-server"
          - "production"
      - name: "db"
        datacenter: "wdc07"
        count: 2  # Creates db-01, db-02
        cores: 4
        memory: 8192
        rootfs_size: 50  # 50GB root filesystem for database storage
        additional_disks: [200]  # Additional 200GB disk for database storage
        security_groups: ["db", "ssh", "egress"]
        tags:
          - "agnosticd"
          - "database"
          - "mysql"
      - name: "app"
        datacenter: "dal13"
        count: 1
        rootfs_size: 100  # 100GB root filesystem for application with more storage needs
        additional_disks: [500]  # Additional 500GB disk for application data
        security_groups: ["web", "db", "ssh", "egress"]  # Combines web + db access
        tags:
          - "agnosticd"
          - "application"
          - "backend"
```

### VM Deployment with Specific VLANs
```yaml
- name: Deploy IBM Cloud Classic VMs with specific VLANs
  include_role:
    name: infra-ibm-cloud-classic-vm
  vars:
    ACTION: provision
    ibm_cloud_api_key: "{{ vault_ibm_cloud_api_key }}"
    output_dir: "/tmp"
    private_vlan_id: 12345
    public_vlan_id: 54321
    instances:
      - name: "web-server"
        datacenter: "dal13"
        tags:
          - "agnosticd"
          - "web-server"
          - "vlan-specific"
```

### High-Performance VMs with Count
```yaml
- name: Deploy High-Performance VMs
  include_role:
    name: infra-ibm-cloud-classic-vm
  vars:
    ACTION: provision
    ibm_cloud_api_key: "{{ vault_ibm_cloud_api_key }}"
    output_dir: "/tmp"
    private_vlan_id: 12345
    public_vlan_id: 54321
    instances:
      - name: "compute-node"
        datacenter: "dal13"
        count: 4  # Creates compute-node-01, compute-node-02, compute-node-03, compute-node-04
        cores: 8
        memory: 16384
        network_speed: 10000
        disks: [50, 200]
        tags:
          - "agnosticd"
          - "high-performance"
          - "compute"
```

### Custom Terraform Version
```yaml
- name: Deploy VMs with custom Terraform version
  include_role:
    name: infra-ibm-cloud-classic-vm
  vars:
    ACTION: provision
    ibm_cloud_api_key: "{{ vault_ibm_cloud_api_key }}"
    output_dir: "/tmp"
    terraform_download_url: "https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip"
    instances:
      - name: "test-vm"
        datacenter: "dal13"
        tags:
          - "agnosticd"
          - "test"
```

### Mixed Security Group Usage
```yaml
- name: Deploy VMs with Mixed Security Group Usage
  include_role:
    name: infra-ibm-cloud-classic-vm
  vars:
    ACTION: provision
    ibm_cloud_api_key: "{{ vault_ibm_cloud_api_key }}"
    output_dir: "/tmp"
    private_vlan_id: 12345
    public_vlan_id: 54321
    security_groups:
      - name: "web"
        rules:
          - name: "http"
            description: "Allow HTTP traffic"
            rule_type: "ingress"
            ether_type: "IPv4"
            from_port: 80
            to_port: 80
            protocol: "tcp"
            cidr: "0.0.0.0/0"
          - name: "https"
            description: "Allow HTTPS traffic"
            rule_type: "ingress"
            ether_type: "IPv4"
            from_port: 443
            to_port: 443
            protocol: "tcp"
            cidr: "0.0.0.0/0"
      - name: "db"
        rules:
          - name: "mysql"
            description: "Allow MySQL traffic from internal network"
            rule_type: "ingress"
            ether_type: "IPv4"
            from_port: 3306
            to_port: 3306
            protocol: "tcp"
            cidr: "10.0.0.0/8"
      - name: "ssh"
        rules:
          - name: "ssh"
            description: "Allow SSH access"
            rule_type: "ingress"
            ether_type: "IPv4"
            from_port: 22
            to_port: 22
            protocol: "tcp"
            cidr: "0.0.0.0/0"
      - name: "egress"
        rules:
          - name: "tcp_out"
            description: "Allow outbound TCP traffic"
            rule_type: "egress"
            ether_type: "IPv4"
            protocol: "tcp"
            cidr: "0.0.0.0/0"
    instances:
      - name: "web-server"
        datacenter: "dal13"
        security_groups: ["web", "ssh", "egress"]  # Multiple global groups
        tags:
          - "agnosticd"
          - "web-server"
          - "mixed-sg"
      - name: "db-server"
        datacenter: "dal13"
        security_group: "db"  # Single global group (plus defaults)
        tags:
          - "agnosticd"
          - "database"
          - "single-sg"
      - name: "app-server"
        datacenter: "dal13"
        security_groups: ["web", "db", "ssh", "egress"]  # Combined access
        tags:
          - "agnosticd"
          - "application"
          - "combined-sg"
      - name: "custom-app"
        datacenter: "dal13"
        security_group_rules:  # Inline rules for unique requirements
          - name: "custom_api"
            description: "Allow custom API access from specific subnet"
            rule_type: "ingress"
            ether_type: "IPv4"
            from_port: 9000
            to_port: 9000
            protocol: "tcp"
            cidr: "192.168.1.0/24"
          - name: "ssh"
            description: "Allow SSH access"
            rule_type: "ingress"
            ether_type: "IPv4"
            from_port: 22
            to_port: 22
            protocol: "tcp"
            cidr: "0.0.0.0/0"
        tags:
          - "agnosticd"
          - "custom-app"
          - "inline-sg"
```

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Ensure API key has Classic Infrastructure permissions
   - Check API key is not expired

2. **VLAN Issues**
   - Verify VLAN IDs exist in the specified datacenter
   - Ensure VLANs are in the correct region

3. **SSH Connection Issues**
   - Verify SSH key is properly configured
   - Check security group rules allow SSH access
   - Ensure VM is fully provisioned

4. **Terraform Issues**
   - Check Terraform templates are present in `~/create-vm-ibm-cloud`
   - Verify Terraform state is not corrupted
   - Review Terraform logs for detailed errors

### Debug Mode

Enable debug output:
```yaml
debug: true
```

## License

This role is part of the AgnosticD project and follows the same licensing terms. 