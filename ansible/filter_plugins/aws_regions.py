#!/usr/bin/env python
"""
AWS Region Validation Filters for AgnosticD
Provides intelligent region selection and validation based on workload requirements
"""

from ansible.errors import AnsibleFilterError
from ansible.module_utils.six import string_types


def aws_validate_region_compatibility(aws_region, workload_vars):
    """
    Validate if the selected AWS region is compatible with the workload requirements.
    
    Args:
        aws_region: The selected AWS region
        workload_vars: Dictionary containing workload variables
        
    Returns:
        Dict with validation results and recommendations
    """
    
    function_name = "aws_validate_region_compatibility"
    
    if not isinstance(aws_region, string_types):
        raise AnsibleFilterError(
            'Invalid type used with {} filter, '
            'expect a string, got {}'.format(function_name, type(aws_region))
        )
    
    if not isinstance(workload_vars, dict):
        raise AnsibleFilterError(
            'Invalid type used with {} filter, '
            'expect a dict, got {}'.format(function_name, type(workload_vars))
        )
    
    # AWS Region Registry - Central source of truth
    aws_ami_registry = {
        'RHELAI10': ['us-east-2', 'us-east-1'],
        'RHELAI12': ['us-east-2', 'us-east-1'],
        'RHELAI13': ['us-east-2', 'us-east-1', 'us-west-1', 'us-west-2'],
        'aap-2.5-10.1-x86_64-20250304': [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-central-1', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1',
            'ap-southeast-2', 'ca-central-1'
        ],
        'RHEL95GOLD-latest': [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-central-1', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1',
            'ap-southeast-2', 'ca-central-1'
        ]
    }
    
    # Instance Type Availability
    aws_instance_type_regions = {
        'g6.xlarge': ['us-east-1', 'us-east-2', 'us-west-2', 'eu-central-1', 'ap-northeast-1'],
        'g6.2xlarge': ['us-east-1', 'us-east-2', 'us-west-2', 'eu-central-1', 'ap-northeast-1'],
        'g6.4xlarge': ['us-east-1', 'us-east-2', 'us-west-2', 'eu-central-1', 'ap-northeast-1'],
        'g6.12xlarge': ['us-east-1', 'us-east-2', 'us-west-2', 'eu-central-1', 'ap-northeast-1'],
        'g6.24xlarge': ['us-east-1', 'us-east-2', 'us-west-2'],
        'g6e.2xlarge': ['us-east-1', 'us-east-2', 'us-west-2'],
        'g5.xlarge': ['us-east-1', 'us-east-2', 'us-west-2', 'eu-central-1', 'ap-northeast-1', 'ap-southeast-2'],
        'g5.4xlarge': ['us-east-1', 'us-east-2', 'us-west-2', 'eu-central-1', 'ap-northeast-1', 'ap-southeast-2'],
        'g4dn.xlarge': ['us-east-1', 'us-east-2', 'us-west-2', 'eu-central-1', 'ap-northeast-1', 'ap-southeast-2', 'eu-west-1'],
        # Standard instances available everywhere
        't3a.large': ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'eu-central-1', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1', 'ap-southeast-2', 'ca-central-1'],
        't3a.xlarge': ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'eu-central-1', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1', 'ap-southeast-2', 'ca-central-1'],
        'm5a.4xlarge': ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'eu-central-1', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1', 'ap-southeast-2', 'ca-central-1'],
        'm5ad.2xlarge': ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'eu-central-1', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1', 'ap-southeast-2', 'ca-central-1'],
        'm5.xlarge': ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'eu-central-1', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1', 'ap-southeast-2', 'ca-central-1'],
        'm5.2xlarge': ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'eu-central-1', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1', 'ap-southeast-2', 'ca-central-1'],
        'm5.4xlarge': ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'eu-central-1', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1', 'ap-southeast-2', 'ca-central-1'],
    }
    
    # Collect all instance types from workload
    instance_types = []
    ami_images = []
    
    # Check various instance type variables
    for var_name in ['bastion_instance_type', 'default_instance_type', 'controller_instance_type',
                     'rhelai_instance_type', 'gpu_instance_type', 'worker_instance_type',
                     'master_instance_type', 'single_gpu_instance_type', 'multi_gpu_instance_type']:
        if var_name in workload_vars:
            instance_types.append(workload_vars[var_name])
    
    # Check various AMI image variables
    for var_name in ['bastion_instance_image', 'default_instance_image', 'controller_instance_image',
                     'rhelai_instance_image', 'worker_instance_image']:
        if var_name in workload_vars:
            ami_images.append(workload_vars[var_name])
    
    # Default fallbacks
    if not instance_types:
        instance_types = ['t3a.large']
    if not ami_images:
        ami_images = ['RHEL95GOLD-latest']
    
    # Validate region compatibility
    compatible = True
    issues = []
    warnings = []
    
    # Check instance type availability
    for instance_type in instance_types:
        if instance_type in aws_instance_type_regions:
            if aws_region not in aws_instance_type_regions[instance_type]:
                compatible = False
                issues.append('Instance type {} not available in {}'.format(instance_type, aws_region))
                # Suggest compatible regions
                compatible_regions = aws_instance_type_regions[instance_type][:3]  # Top 3
                issues.append('  -> Available in: {}'.format(', '.join(compatible_regions)))
    
    # Check AMI availability
    for ami_image in ami_images:
        if ami_image in aws_ami_registry:
            if aws_region not in aws_ami_registry[ami_image]:
                compatible = False
                issues.append('AMI {} not available in {}'.format(ami_image, aws_region))
                # Suggest compatible regions
                compatible_regions = aws_ami_registry[ami_image][:3]  # Top 3
                issues.append('  -> Available in: {}'.format(', '.join(compatible_regions)))
    
    # Detect workload type and provide recommendations
    workload_type = "standard"
    if any("RHELAI" in ami for ami in ami_images) or any("rhelai" in var for var in workload_vars.keys()):
        workload_type = "rhelai"
    elif any(inst_type.startswith(('g4', 'g5', 'g6')) for inst_type in instance_types):
        workload_type = "gpu"
    
    # Provide optimal region recommendations
    optimal_regions = {
        'rhelai': ['us-east-2', 'us-east-1', 'us-west-2'],
        'gpu': ['us-east-2', 'us-east-1', 'us-west-2', 'eu-central-1', 'ap-northeast-1'],
        'standard': ['us-east-2', 'us-east-1', 'us-west-2', 'eu-central-1', 'ap-southeast-1', 'eu-west-1']
    }
    
    if aws_region not in optimal_regions[workload_type][:3]:  # Top 3 optimal
        warnings.append('Region {} is not optimal for {} workloads'.format(aws_region, workload_type))
        warnings.append('  -> Recommended: {}'.format(', '.join(optimal_regions[workload_type][:3])))
    
    return {
        'compatible': compatible,
        'workload_type': workload_type,
        'issues': issues,
        'warnings': warnings,
        'optimal_regions': optimal_regions[workload_type],
        'selected_region': aws_region
    }


def aws_get_optimal_regions(workload_vars):
    """
    Get optimal AWS regions for a workload based on its requirements.
    
    Args:
        workload_vars: Dictionary containing workload variables
        
    Returns:
        List of optimal regions for the workload
    """
    
    function_name = "aws_get_optimal_regions"
    
    if not isinstance(workload_vars, dict):
        raise AnsibleFilterError(
            'Invalid type used with {} filter, '
            'expect a dict, got {}'.format(function_name, type(workload_vars))
        )
    
    # Detect workload type
    workload_type = "standard"
    
    # Check for RHEL AI workloads
    rhelai_indicators = [
        'rhelai_instance_type', 'rhelai_instance_image',
        'bastion_instance_image'
    ]
    
    for indicator in rhelai_indicators:
        if indicator in workload_vars:
            value = workload_vars[indicator]
            if isinstance(value, string_types) and "RHELAI" in value:
                workload_type = "rhelai"
                break
    
    # Check for GPU workloads
    gpu_indicators = [
        'gpu_instance_type', 'single_gpu_instance_type', 'multi_gpu_instance_type',
        'bastion_instance_type', 'worker_instance_type', 'default_instance_type'
    ]
    
    for indicator in gpu_indicators:
        if indicator in workload_vars:
            value = workload_vars[indicator]
            if isinstance(value, string_types) and any(value.startswith(gpu) for gpu in ['g4', 'g5', 'g6']):
                workload_type = "gpu"
                break
    
    # Return optimal regions based on workload type
    optimal_regions = {
        'rhelai': ['us-east-2', 'us-east-1', 'us-west-2'],
        'gpu': ['us-east-2', 'us-east-1', 'us-west-2', 'eu-central-1', 'ap-northeast-1'],
        'standard': ['us-east-2', 'us-east-1', 'us-west-2', 'eu-central-1', 'ap-southeast-1', 'eu-west-1']
    }
    
    return optimal_regions[workload_type]


def aws_auto_select_region(workload_vars, preferred_region=None):
    """
    Automatically select the best AWS region for a workload.
    
    Args:
        workload_vars: Dictionary containing workload variables
        preferred_region: Optional preferred region to validate first
        
    Returns:
        Best region for the workload
    """
    
    function_name = "aws_auto_select_region"
    
    if not isinstance(workload_vars, dict):
        raise AnsibleFilterError(
            'Invalid type used with {} filter, '
            'expect a dict, got {}'.format(function_name, type(workload_vars))
        )
    
    optimal_regions = aws_get_optimal_regions(workload_vars)
    
    # If preferred region is provided and valid, use it
    if preferred_region and isinstance(preferred_region, string_types):
        validation = aws_validate_region_compatibility(preferred_region, workload_vars)
        if validation['compatible']:
            return preferred_region
    
    # Otherwise, return the first optimal region
    return optimal_regions[0]


class FilterModule(object):
    """AWS Region Validation Filters"""

    def filters(self):
        return {
            'aws_validate_region_compatibility': aws_validate_region_compatibility,
            'aws_get_optimal_regions': aws_get_optimal_regions,
            'aws_auto_select_region': aws_auto_select_region,
        }
