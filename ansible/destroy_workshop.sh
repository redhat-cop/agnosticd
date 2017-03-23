#!/bin/bash
GUID=${2};
REGION=${1}
KEYNAME=ocpkey
ENVTYPE="opentlc-shared"
CLOUDPROVIDER=ec2
HOSTZONEID='Z3IHLWJZOU9SRT'

echo "Deleting GUID '${2}' in region '${1}'."

time ansible-playbook -i inventory/ ./configs/${ENVTYPE}/destroy_env.yml \
 -e "guid=${GUID}" -e "env_type=${ENVTYPE}" -e "cloud_provider=${CLOUDPROVIDER}" -e "aws_region=${REGION}"  \
 -e "HostedZoneId=${HOSTZONEID}" -e "key_name=${KEYNAME}" -e "subdomain_base_suffix=.openshift.opentlc.com" 
