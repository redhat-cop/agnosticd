### KMM, NFD and Habana Gaudi Accelerators / GPU Setup Role ###
# Role to setup Habana Gaudi HPY's for RHODS requirements.

=== Deploy a Workload with the `ocp-workload` playbook [Mostly for testing]

----
TARGET_HOST="bastion.na311.openshift.opentlc.com"
OCP_USERNAME="mavazque-redhat.com"
WORKLOAD="ocp4_workload_rhacm"
GUID=1001

# a TARGET_HOST is specified in the command line, without using an inventory file
ansible-playbook -i ${TARGET_HOST}, ./configs/ocp-workloads/ocp-workload.yml \
    -e"ansible_ssh_private_key_file=~/.ssh/keytoyourhost.pem" \
    -e"ansible_user=ec2-user" \
    -e"ocp_username=${OCP_USERNAME}" \
    -e"ocp_workload=${WORKLOAD}" \
    -e"silent=False" \
    -e"guid=${GUID}" \
    -e"ACTION=create"
----

=== To Delete an environment

----
TARGET_HOST="bastion.na412.openshift.opentlc.com"
OCP_USERNAME="rshah-redhat.com"
WORKLOAD="ocp4_workload_habana_gaudi_gpu_setup"
GUID=1002

# a TARGET_HOST is specified in the command line, without using an inventory file
ansible-playbook -i ${TARGET_HOST}, ./configs/ocp-workloads/ocp-workload.yml \
    -e"ansible_ssh_private_key_file=~/.ssh/keytoyourhost.pem" \
    -e"ansible_user=ec2-user" \
    -e"ocp_username=${OCP_USERNAME}" \
    -e"ocp_workload=${WORKLOAD}" \
    -e"guid=${GUID}" \
    -e"ACTION=remove"
----
