#!/bin/bash

# wapper script to agnostic_ansible_deployer playbooks

if [ $# -lt 2 ]; then
    echo "2 args needed" >&2
    echo
    echo 'wapper script to agnostic_ansible_deployer playbooks'
    echo "./$0 RCFILE ACTION"
    echo 'args'
    echo '- RCFILE: to be sourced, containing needed env variables (especially envtype_args array)'
    echo '- ACTION: provision|destroy|stop|start|scaleup'
    exit 2
fi

set -xe -o pipefail
ORIG=$(cd $(dirname $0); cd ..; pwd)
DEPLOYER_REPO_PATH="${ORIG}/ansible"

export ANSIBLE_CONFIG=${DEPLOYER_REPO_PATH}/ansible.cfg

. "$1"

if [ -z "${GUID}" ]; then
    echo "GUID is mandatory"
    exit 2
fi


REGION=${REGION:-us-east-1}
KEYNAME=${KEYNAME:-ocpkey}
ENVTYPE=${ENVTYPE:-generic-example}
PROFILE=${PROFILE:-default}
CLOUDPROVIDER=${CLOUDPROVIDER:-ec2}
if [ "$CLOUDPROVIDER" = "ec2" ]; then
    if [ -z "${HOSTZONEID}" ]; then
        echo "HOSTZONEID vars are mandatory"
        exit 2
    fi
    INVENTORY=${DEPLOYER_REPO_PATH}/inventory/ec2.sh
else
    INVENTORY=${DEPLOYER_REPO_PATH}/inventory/${CLOUDPROVIDER}.py
fi

INSTALL_IPA_CLIENT=${INSTALL_IPA_CLIENT:-false}
REPO_METHOD=${REPO_METHOD:-file}
SOFTWARE_TO_DEPLOY=${SOFTWARE_TO_DEPLOY:-none}

STACK_NAME=${ENVTYPE}-${GUID}

case $2 in
    provision)
        shift; shift
        ansible-playbook \
            ${DEPLOYER_REPO_PATH}/main.yml  \
            -i ${INVENTORY} \
            -e "ANSIBLE_REPO_PATH=${DEPLOYER_REPO_PATH}" \
            -e "guid=${GUID}" \
            -e "env_type=${ENVTYPE}" \
            -e "key_name=${KEYNAME}" \
            -e "cloud_provider=${CLOUDPROVIDER}" \
            -e "aws_region=${REGION}" \
            -e "azure_region=${REGION}" \
            -e "HostedZoneId=${HOSTZONEID}" \
            -e "install_ipa_client=${INSTALL_IPA_CLIENT}" \
            -e "software_to_deploy=${SOFTWARE_TO_DEPLOY}" \
            -e "repo_method=${REPO_METHOD}" \
            ${ENVTYPE_ARGS[@]} \
            "$@"
        ;;

    destroy)
        shift; shift
        ansible-playbook \
            ${DEPLOYER_REPO_PATH}/configs/${ENVTYPE}/destroy_env.yml \
            -i ${INVENTORY} \
            -e "ANSIBLE_REPO_PATH=${DEPLOYER_REPO_PATH}" \
            -e "guid=${GUID}" \
            -e "env_type=${ENVTYPE}"  \
            -e "cloud_provider=${CLOUDPROVIDER}" \
            -e "aws_region=${REGION}"  \
            -e "azure_region=${REGION}"  \
            -e "HostedZoneId=${HOSTZONEID}"  \
            -e "key_name=${KEYNAME}"  \
            ${ENVTYPE_ARGS[@]} \
            "$@"
        ;;

    scaleup)
        shift; shift
        ansible-playbook \
            ${DEPLOYER_REPO_PATH}/configs/${ENVTYPE}/scaleup.yml \
            -i ${INVENTORY} \
            -e "ANSIBLE_REPO_PATH=${DEPLOYER_REPO_PATH}" \
            -e "guid=${GUID}" \
            -e "env_type=${ENVTYPE}" \
            -e "key_name=${KEYNAME}" \
            -e "cloud_provider=${CLOUDPROVIDER}" \
            -e "aws_region=${REGION}" \
            -e "azure_region=${REGION}"  \
            -e "HostedZoneId=${HOSTZONEID}" \
            -e "install_ipa_client=${INSTALL_IPA_CLIENT}" \
            -e "software_to_deploy=${SOFTWARE_TO_DEPLOY}" \
            -e "repo_method=${REPO_METHOD}" \
            ${ENVTYPE_ARGS[@]} \
            "$@"
        ;;

    stop)
        aws ec2 stop-instances --profile $PROFILE --region $REGION --instance-ids $(aws ec2 describe-instances --filters "Name=tag:aws:cloudformation:stack-name,Values=${STACK_NAME}" --query Reservations[*].Instances[*].InstanceId --profile $PROFILE --region $REGION --output text)
        ;;
    start)
        aws ec2 start-instances --profile $PROFILE --region $REGION --instance-ids `aws ec2 describe-instances --filters "Name=tag:aws:cloudformation:stack-name,Values=${STACK_NAME}" --query Reservations[*].Instances[*].InstanceId --profile $PROFILE --region $REGION --output text`
        ;;
esac
