### Run this role post KMM, NFD and Habana Gaudi Accelerators / GPU Setup Role completion and RHODS operator installation role completion ###

# Once the role installation is comleted, update the respective notebook by adding       "habana.ai/gaudi: '1'" as shown below in limits and requests for the main container.
# With the release of RHODS 1.34, below procedure is not required.

# From UI - API Epxlorer, search for notebook. Select v1 with Group kubeflow.org & instances(Be sure to be in rhods-notebooks project or respective project where you are running the notebook). Go to instances , select your instance and edit the yaml file to add habana.ai/gaudi hpu's as shown below.

spec:
 template:
 spec:
 affinity:
 nodeAffinity:
 preferredDuringSchedulingIgnoredDuringExecution:
- preference:
 matchExpressions:
- key: nvidia.com/gpu.present
 operator: NotIn
 values:
- 'true'
 weight: 1
 containers:
- resources:
 limits:
 cpu: '2'
** habana.ai/gaudi: '1'
 memory: 8Gi
 requests:
 cpu: '1'
** habana.ai/gaudi: '1'
 memory: 8Gi

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
WORKLOAD="ocp4_workload_habana_post_rhods_setup"
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
