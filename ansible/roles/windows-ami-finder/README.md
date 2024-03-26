# windows-ami-finder

Find the latest version of Windows Server image and save the AMI as a variable (windows_ami)

## Requirements
Collections:
  - amazon.aws

## Role Variables

`windows_ami_finder_windows_ami_owner`  - AWS Account to poll for images
`windows_ami_finder_windows_ami_filter` - Filter Values to search for specific images
`windows_ami_finder_aws_region` - Defaults to "aws_region" usually found in config default_vars_ec2.yml
`ocp_access_key` - Internal AWS access key
`ocp_secret_key` - Internal AWS secret Key

License
-------

BSD

Author Information
------------------
Wilson Harris
Red Hat, GPTE
