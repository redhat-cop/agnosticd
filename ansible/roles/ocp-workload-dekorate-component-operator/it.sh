#!/bin/sh

HOST_GUID=$1
ACTION=${2:-create}

TARGET_HOST="bastion.$HOST_GUID.openshiftworkshop.com"

OCP_USERNAME="cmoulliard-redhat.com"
WORKLOAD="ocp-workload-dekorate-component-operator"
GUID=$HOST_GUID

SSH_USER=$OCP_USERNAME
SSH_PRIVATE_KEY="id_rsa"

ansible-playbook -i $TARGET_HOST, ./configs/ocp-workloads/ocp-workload.yml \
    -e "ansible_ssh_private_key_file=~/.ssh/${SSH_PRIVATE_KEY}" \
    -e "ansible_user=${SSH_USER}" \
    -e "ANSIBLE_REPO_PATH=`pwd`" \
    -e "ocp_username=${OCP_USERNAME}" \
    -e "ocp_workload=${WORKLOAD}" \
    -e "silent=False" \
    -e "guid=${GUID}" \
    -e "ACTION=$ACTION" \
    -v