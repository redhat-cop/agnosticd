#!/bin/bash
GUID=${2};
REGION=${1}
KEYNAME=ocpkey
ENVTYPE="ocp-ha-lab"
CLOUDPROVIDER=ec2
HOSTZONEID='Z3IHLWJZOU9SRT'

echo "Setting up GUID '${2}' in region '${1}'."

time ansible-playbook -i inventory/ ./main.yml \
  -e "guid=${GUID}" -e "env_type=${ENVTYPE}" \
  -e "cloud_provider=${CLOUDPROVIDER}" -e "aws_region=${REGION}" \
  -e "HostedZoneId=${HOSTZONEID}"  -e "key_name=${KEYNAME}"  -e "subdomain_base_suffix=.example.opentlc.com" \
  -e "install_idm=htpasswd" -e "node_instance_count=3" -e "infranode_instance_count=2" \
  -e "master_instance_count=3" -e "software_to_deploy=openshift" \
  -e "ipa_host_password=10b7386a-f63b-4254-8fa0-6b5c2723197a" --skip-tags=installing_openshift
