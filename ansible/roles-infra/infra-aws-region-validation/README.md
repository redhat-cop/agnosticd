# AWS Region Validation Role

This role provides intelligent AWS region validation and selection based on workload requirements.

## Features

- **Smart Region Validation**: Validates if the selected AWS region is compatible with workload requirements
- **Workload Detection**: Automatically detects workload type (RHEL AI, GPU, Standard)
- **Auto-Selection**: Automatically selects optimal region when none is specified
- **Comprehensive Validation**: Checks AMI availability, instance type availability, and optimal regions
- **Detailed Reporting**: Provides clear validation results and recommendations

## Usage

### Basic Usage

```yaml
- name: Validate AWS region
  include_role:
    name: infra-aws-region-validation
```

### With Custom Variables

```yaml
- name: Validate AWS region with custom settings
  include_role:
    name: infra-aws-region-validation
  vars:
    aws_region_validation_strict: false  # Warnings only
    aws_region_validation_verbose: true  # Detailed output
```

## Variables

### Input Variables

- `aws_region`: The AWS region to validate (optional, will auto-select if not provided)
- `aws_region_validation_enabled`: Enable/disable validation (default: true)
- `aws_region_validation_strict`: Fail on incompatible regions (default: true)
- `aws_region_default`: Default region fallback (default: us-east-2)

### Output Variables

- `aws_region_final`: The final validated/selected region
- `aws_region_validated`: The validated region
- `aws_region_validation`: Detailed validation results
- `aws_region_metadata`: Metadata about the validation process

## Workload Detection

The role automatically detects workload types based on variables:

### RHEL AI Workloads
- Variables containing `rhelai_instance_type` or `rhelai_instance_image`
- AMI images containing "RHELAI"
- Optimal regions: us-east-2, us-east-1, us-west-2

### GPU Workloads
- Instance types starting with g4, g5, or g6
- Variables like `gpu_instance_type`, `single_gpu_instance_type`
- Optimal regions: us-east-2, us-east-1, us-west-2, eu-central-1, ap-northeast-1

### Standard Workloads
- All other workloads
- Optimal regions: us-east-2, us-east-1, us-west-2, eu-central-1, ap-southeast-1, eu-west-1

## Integration

This role should be included early in the deployment process, before infrastructure provisioning:

```yaml
- name: Step 001.0 Validate AWS Region
  hosts: localhost
  connection: local
  gather_facts: false
  become: false
  tasks:
    - name: Validate AWS region for workload
      include_role:
        name: infra-aws-region-validation
```

## Examples

### Example 1: RHEL AI Workload

```yaml
vars:
  rhelai_instance_type: g6.2xlarge
  rhelai_instance_image: RHELAI13
  aws_region: eu-west-1  # Will fail validation

# Result: Validation fails, recommends us-east-2, us-east-1, us-west-2
```

### Example 2: Auto-Selection

```yaml
vars:
  gpu_instance_type: g5.4xlarge
  # No aws_region specified

# Result: Auto-selects us-east-2 (optimal for GPU workloads)
```

### Example 3: Standard Workload

```yaml
vars:
  default_instance_type: m5.xlarge
  aws_region: us-east-1

# Result: Validates successfully
```
