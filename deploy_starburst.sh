TARGET_HOST="bastion.f941.sandbox1327.opentlc.com"
OCP_USERNAME="gejames-redhat.com"
WORKLOAD="ocp4_workload_starburst"
GUID=$(date +%s|sha256sum|base64|head -c 4)
ANSIBLE_USER="gejames-redhat.com"

cd /home/geojams/agnosticd-git/ansible

# a TARGET_HOST is specified in the command line, without using an inventory file
ansible-playbook -k -i ${TARGET_HOST}, ./configs/ocp-workloads/ocp-workload.yml \
    -e"ansible_user=${ANSIBLE_USER}" \
    -e"ocp_username=${OCP_USERNAME}" \
    -e"ocp_workload=${WORKLOAD}" \
    -e"silent=False" \
    -e"guid=${GUID}" \
    -e"ACTION=create" \
    -e @/home/geojams/secrets/starburst_license.yml

