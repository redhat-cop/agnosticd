### Authorino Operator Deployment Role ###

Role name: ocp4_workload_authorino

This role install Authorino Operator on OpenShift Cluster.

. Set up Environment Variables for the bastion you want to run this role on.
+
[source,bash]
----
TARGET_HOST="bastion.dev.openshift.opentlc.com"
OCP_USERNAME="rshah-redhat.com"
ANSIBLE_USER="ec2-user" # Will become OpenTLC username
WORKLOAD="ocp4_workload_authorino"
GUID="1001"
----

. Finally run the workload passing the input files as parameters:
+
[source,sh]
----
# a TARGET_HOST is specified in the command line, without using an inventory file
ansible-playbook -i ${TARGET_HOST}, ./configs/ocp-workloads/ocp-workload.yml \
    -e"ansible_ssh_private_key_file=~/.ssh/keytoyourhost.pem" \
    -e"ansible_user=${ANSIBLE_USER}" \
    -e"ocp_username=${OCP_USERNAME}" \
    -e"ocp_workload=${WORKLOAD}" \
    -e"guid=${GUID}" \
    -e"ACTION=create" \
    -e @./ocp4_workload_example_dedicated_cluster_vars.yaml \
    -e @./ocp4_workload_example_dedicated_cluster_secrets.yaml
----
+

=== To Delete a Workload from the CLI

----
TARGET_HOST="bastion.dev.openshift.opentlc.com"
OCP_USERNAME="rshah-redhat.com"
ANSIBLE_USER="ec2-user" # Will become OpenTLC username
WORKLOAD="ocp4_workload_authorino"
GUID="1001"

# a TARGET_HOST is specified in the command line, without using an inventory file
ansible-playbook -i ${TARGET_HOST}, ./configs/ocp-workloads/ocp-workload.yml \
    -e"ansible_ssh_private_key_file=~/.ssh/keytoyourhost.pem" \
    -e"ansible_user=ec2-user" \
    -e"ocp_username=${OCP_USERNAME}" \
    -e"ocp_workload=${WORKLOAD}" \
    -e"guid=${GUID}" \
    -e"ACTION=remove" \
    -e @./ocp_workload_example_dedicated_cluster_vars.yaml \
    -e @./ocp_workload_example_dedicated_cluster_secrets.yaml
----

== Deploying a Workload with AgnosticV from the Command Line

When creating a configuration in AgnosticV that includes the deployment of the workload you can specify the variables straight in the AgnosticV config.
AgnosticV configs are usually created by combining a `common.yaml` file with either `dev.yaml`, `test.yaml` or `prod.yaml`.
You can specify different variables in each of these files.
For example you could have common values defined in the `common.yaml` file and then specific values overriding the common ones for development or production environments in `dev.yaml` or `prod.yaml`.

AgnosticV merges the definition files starting with `common.yaml` and then adding/overwriting what comes from either `dev.yaml` or `prod.yaml`.
