#/bin/sh

###
# Usage:
#   ./deploy-using-rhpds-bastion.sh <ACTION> [options]
#
#       ACTION  - either "create" or "remove"
#       options - extended arguments to ansible-playbook
#
# Execute create with verbose example:
#   ./deploy-using-rhpds-bastion.sh create -vvvv

RHT_SVC_ACCT_TOKEN="<CHANGE ME!!!>"

### change placeholders with RHPDS values
TARGET_HOST="<CHANGE ME!!!>"

ANSIBLE_SSH_USER="<CHANGE ME!!!>"
ANSIBLE_SSH_PWD="<CHANGE ME!!!>"

OCP_USERNAME="opentlc-mgr"
WORKLOAD="ocp4-workload-openbanking-sandbox"
ACTION="create"

BASEDIR=$(dirname "$0")
cd ${BASEDIR}/../../

if [ "$1" == "remove" ]; then
    ACTION="$1"
    shift
fi

ansible-playbook -i ${TARGET_HOST}, ./configs/ocp-workloads/ocp-workload.yml \
    -e @./roles/${WORKLOAD}/defaults/main.yml \
    -e"ocp_username=${OCP_USERNAME}" \
    -e"ocp_workload=${WORKLOAD}" \
    -e"obsandbox_3scale_registry_token=${RHT_SVC_ACCT_TOKEN}" \
    -e"silent=False" \
    -e"ACTION=${ACTION}" \
    -e"ansible_user=${ANSIBLE_SSH_USER}" \
    -e"ansible_password=${ANSIBLE_SSH_PWD}" $@