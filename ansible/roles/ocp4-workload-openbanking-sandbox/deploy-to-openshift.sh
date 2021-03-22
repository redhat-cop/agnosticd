#/bin/sh

###
# Usage:
#   ./deploy-on-openshift.sh <ACTION> [options]
#
#       ACTION  - either "create" or "remove"
#       options - extended arguments to ansible-playbook
#
# Execute create with verbose example:
#   ./deploy-on-openshift.sh create -vvvv

RHT_SVC_ACCT_TOKEN="<CHANGE ME!!!>"

### uncomment below to login CRC cluster using 'kubeadmin'
#crc console --credentials | tail -n 1 | cut -d "'" -f 2 | sh

OCP_USERNAME="$( oc whoami )"
TARGET_HOST="localhost"
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
    -e"ACTION=${ACTION}" $@
