### Run this role to setup Rocket Chat and related configurations ###

This blog is useful to understand the implementation aspects of rocket chat.
https://medium.com/@ritz.shah/rocket-chat-setup-configuration-and-working-in-an-openshift-k8s-environment-3b418a3e48c7

=== Deploy a Workload with the `ocp-workload` playbook [Mostly for testing]

----
TARGET_HOST="bastion.na411.openshift.opentlc.com"
OCP_USERNAME="user1-redhat.com"
WORKLOAD="ocp4_workload_rocket_chat"
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
OCP_USERNAME="user1-redhat.com"
WORKLOAD="ocp4_workload_rocket_chat"
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
