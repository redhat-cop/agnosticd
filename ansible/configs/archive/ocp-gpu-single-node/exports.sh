export REGION=us-east-1
export KEYNAME=roadshow
export ENVTYPE="ocp-gpu-single-node"
export CLOUDPROVIDER=ec2
export HOSTZONEID='ZNQ5TMIG603EU'
export BASESUFFIX='.openshiftdemos.com'
export DEPLOYER_REPO_PATH=`pwd`

ansible-playbook main.yml  -e "guid=${GUID}" -e "env_type=${ENVTYPE}" \
-e "repo_version=${REPO_VERSION}" \
  -e "cloud_provider=${CLOUDPROVIDER}" -e "aws_region=${REGION}" \
  -e "HostedZoneId=${HOSTZONEID}" -e "key_name=${KEYNAME}" \
  -e "subdomain_base_suffix=${BASESUFFIX}" \
  -e "software_to_deploy=openshift" \
  -e "ANSIBLE_REPO_PATH=${DEPLOYER_REPO_PATH}" --skip-tags=remove_self_provisioners \
  -t step000,step001
