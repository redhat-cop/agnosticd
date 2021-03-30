ENVTYPE=ans-tower-lab
GUID=homework
BASESUFFIX='.example.opentlc.com'
CLOUDPROVIDER=ec2
REGION=us-east-1
HOSTZONEID='Z3IHLWJZOU9SRT'
KEYNAME=ocpkey
ENVTYPE=ans-tower-lab
CLOUDPROVIDER=ec2
HOSTZONEID='Z3IHLWJZOU9SRT'
BASESUFFIX='.example.opentlc.com'

ansible-playbook main.yml                       \
      -e "guid=${GUID}"                         \
      -e "env_type=${ENVTYPE}"                  \
      -e "key_name=${KEYNAME}"                  \
      -e "subdomain_base_suffix=${BASESUFFIX}"  \
      -e "cloud_provider=${CLOUDPROVIDER}"      \
      -e "aws_region=${REGION}"                 \
      -e "HostedZoneId=${HOSTZONEID}"           \
      -e "email=name@example.com"               \
      -e "output_dir=/tmp"              \
      -e@~/secret.yml                          \
      -e "deploy_tower_homework=true"
