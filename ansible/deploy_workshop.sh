#!/bin/bash
GUID=${2};
REGION=${1}
KEYNAME=ocpkey
ENVTYPE="opentlc-shared"
CLOUDPROVIDER=ec2

# Next two settings are related
HOSTZONEID='Z186MFNM7DX4NF'
SUBDOMAIN=".openshift.opentlc.com"

echo "Setting up '${2}${SUBDOMAIN}' in region '${1}'."

time ansible-playbook -i inventory/ ./main.yml \
 -e "guid=${GUID}" -e "env_type=${ENVTYPE}" -e "cloud_provider=${CLOUDPROVIDER}" -e "aws_region=${REGION}"  \
 -e "HostedZoneId=${HOSTZONEID}" -e "key_name=${KEYNAME}" -e "subdomain_base_suffix=${SUBDOMAIN}" \
 -e "bastion_instance_type=t2.large" -e "master_instance_type=c4.xlarge" \
 -e "infranode_instance_type=m4.4xlarge" -e "node_instance_type=m4.4xlarge" \
 -e "nfs_instance_type=m3.large" -e "node_instance_count=2" -e "install_idm=ldap" \
 -e "software_to_deploy=openshift"

