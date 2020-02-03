HOST_GUID=username-mac
TARGET_HOST="username-mac.attlocal.net"
OCP_USERNAME="opentlc-mgr"
SSH_USER="sadhananandakumar"
SSH_PRIVATE_KEY="id_rsa"
GUID="sadhananandakumar"

WORKLOAD="ocp-workload-pam7-offer-management-dmn-pmml"

ansible-playbook -v -i ${TARGET_HOST}, ./configs/ocp-workloads/ocp-workload.yml \
                 -e"ansible_ssh_private_key_file=/Users/sadhananandakumar/.ssh/id_rsa" \
                 -e"ansible_ssh_user=${SSH_USER}" \
                 -e"ANSIBLE_REPO_PATH=pwd" \
                 -e"ocp_username=${OCP_USERNAME}" \
                 -e"ocp_workload=${WORKLOAD}" \
                 -e"guid=${GUID}" \
                 -e"ocp_user_needs_quota=true" \
                 -e"ocp_master=master.${HOST_GUID}.openshift.opentlc.com" \
                 -e"ocp_apps_domain=apps.${HOST_GUID}.openshift.opentlc.com" \
                 -e"ACTION=create" \
