= ocp4_workload_lpe_fuse - Deploy Fuse Products on Openshift

== Role overview

* This role installs Camel K, Fuse, Fuse Online and supporting applications into an OpenShift Cluster. +
The role is primarily meant to provide an environment where users can deploy Camel K integrations, design API's and deploy Fuse integrations on both Openshift directly or through Fuse Online as well as monitor them with the Fuse Console.. +
It consists of the following tasks files:
** Tasks: link:./tasks/pre_workload.yml[pre_workload.yml] - Sets up an
 environment for the workload deployment.
*** Debug task will print out: `pre_workload Tasks completed successfully.`

** Tasks: link:./tasks/workload.yml[workload.yml] - Deploys:
*** Camel K with an integration platform and a test integration.  All Camel K integrations should be deployed into Namespace `lpe-fuse-camelk-{{ guid }}`
*** Fuse on Openshift with the latest Fuse Image Streams and Templates. Installed into Namespace `lpe-fuse-{{ guid }}`
*** Fuse API Designer for creating new or editing existing API designs. Installed into Namespace `lpe-fuse-{{ guid }}`
*** Fuse Console for the discovery and management of Fuse applications deployed on OpenShift. Installed into Namespace `lpe-fuse-{{ guid }}`
*** Fuse Online for providing core integration capabilities as a service. Installed into Namespace `lpe-fuse-{{ guid }}`
*** Debug task will print out: `workload Tasks completed successfully.`

** Tasks: link:./tasks/post_workload.yml[post_workload.yml] - Used to
 configure the workload after deployment
*** This role doesn't do anything here
*** Debug task will print out: `post_workload Tasks completed successfully.`

** Tasks: link:./tasks/remove_workload.yml[remove_workload.yml] - Used to
 delete the workload
*** Removes namespaces associated with the role
*** Debug task will print out: `remove_workload Tasks completed successfully.`


== Review the defaults variable file

* This file link:./defaults/main.yml[./defaults/main.yml] contains all the variables you need to define to control the deployment of your workload.
* The variable *ocp_username* is mandatory to assign the workload to the correct OpenShift user.

=== Deploy a Workload with the `ocp-workload` playbook [Mostly for testing]

----
TARGET_HOST="bastion.dev4.openshift.opentlc.com"
OCP_USERNAME="treddy-redhat.com"
WORKLOAD="ocp4_workload_lpe_fuse"
OCP4_TOKEN='TOKEN FOR PULLING IMAGES FROM registry.redhat.io'
GUID=1001

# a TARGET_HOST is specified in the command line, without using an inventory file
ansible-playbook -i ${TARGET_HOST}, ./configs/ocp-workloads/ocp-workload.yml \
    -e"ansible_ssh_private_key_file=~/.ssh/keytoyourhost.pem" \
    -e"ansible_user=ec2-user" \
    -e"ocp_username=${OCP_USERNAME}" \
    -e"ocp_workload=${WORKLOAD}" \
    -e"ocp4_token=${OCP4_TOKEN}" \
    -e"guid=${GUID}" \
    -e"ACTION=create"
----

=== To Delete an environment

----
TARGET_HOST="bastion.dev4.openshift.opentlc.com"
OCP_USERNAME="treddy-redhat.com"
WORKLOAD="ocp4_workload_lpe_fuse"
GUID=1001

# a TARGET_HOST is specified in the command line, without using an inventory file
ansible-playbook -i ${TARGET_HOST}, ./configs/ocp-workloads/ocp-workload.yml \
    -e"ansible_ssh_private_key_file=~/.ssh/keytoyourhost.pem" \
    -e"ansible_user=opentlc-mgr" \
    -e"ocp_username=${OCP_USERNAME}" \
    -e"ocp_workload=${WORKLOAD}" \
    -e"guid=${GUID}" \
    -e"ACTION=remove"
----

