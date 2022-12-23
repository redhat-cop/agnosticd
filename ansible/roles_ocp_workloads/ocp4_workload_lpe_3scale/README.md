
= 3scale Latest Product Environment

:numbered:

== Overview

This workload provisions all the required resources for 3scale API Manager & a default tenant On OpenShift 4. The following are provisioned:

. 3scale Operator
. 3scale Multitenant API Manager (default channel) (S3 compatible provider)
. 3scale single tenant
. 3scale Gateway Projects for each user:
.. Gateway Operator (latest channel)
.. Portal Endpoint secret for connecting to corresponding 3scale tenant admin
.. Staging & Production API Gateways


=== Prerequisites and assumptions

An OCP 4 cluster is provisioned and this role is run using a cluster admin.


. The version of 3scale provisioned in this lab (v2.11) is known to run on OpenShift Container Platform v4.*.
+
This version of OpenShift should already be pre-installed before executing this ansible role.

. Using a version of oc utility that corresponds to your target OCP cluster, ensure oc utility is already authenticated as the cluster-admin.


==== SMTP Providers
You'll want to have registered with an smtp provider to enable the 3scale API Manager with the ability to send emails.

In 3scale, smtp settings are configured globally and is leveraged by all API _tenants_.
When provisioning 3scale, you can specify the following ansible variables:

* smtp_host
* smtp_userid
* smtp_passwd
* smtp_authentication


A few SMTP providers with _Free Plans_ that this ansible role has been tested with are listed below:

. *SocketLabs:* Currently offering a free plan that allows for link:https://www.socketlabs.com/signup/[2000 emails per month]
. *SendGrid:* Currently offering a free plan that allows for link:https://sendgrid.com/pricing/[100 emails per day]

You can choose to provision your 3scale API Manager such that it is not configured to send emails.
To do so, ensure that the value of _smtp_userid_ = "changeme"

=== Project Layout

. Notice the directory layout and files included in this project:
+
-----
$ tree

├── defaults
│   └── main.yml
├── files
│   ├── 3scale_remove_tenants.yml
│   ├── 3scale_single_tenant_user.yml
│   ├── 3scale_single_tenant.yml
│   └── mino_s3_config.yml
├── meta
│   └── main.yml
├── README.adoc
├── tasks
│   ├── main.yml
│   ├── post_workload.yml
│   ├── pre_workload.yml
│   ├── remove_workload.yml
│   └── workload.yml
└── templates
    └── << all the k8s object J2 files >>
-----

. Highlights of the most important files are as follows:

.. *defaults/main.yml* : ansible variables and their defaults
.. *tasks/workload.yml* : ansible tasks executed when provisioning 3scale API Manager




== Deployment

=== Environment Variables

-----
# Update the following:


$ ocp4_workload_lpe_3scale_namespace=3scale-management-project-{{ guid }}"     # OCP namespace where 3scale API Manager resides

# Execute the following:
$ source ~/.bashrc


# SMTP Configurations to enable API Manager to send emails
# If the SMTP values are not provided SMTP is not set up for 3scale & emails cannot be sent. This does not impact the usability in demos or workshops that do not use this feature.
$ ocp4_workload_lpe_3scale_smtp_host=smtp.socketlabs.com
$ ocp4_workload_lpe_3scale_smtp_port=587
$ ocp4_workload_lpe_3scale_smtp_authentication=login
$ ocp4_workload_lpe_3scale_smtp_userid=<change me>
$ ocp4_workload_lpe_3scale_smtp_passwd=<change me>
$ ocp4_workload_lpe_3scale_smtp_domain=redhat.com

# Admin Email user and domain:
    
$ ocp4_workload_lpe_3scale_admin_email_user=<change me>            # e.g 3scaleadmin
$ ocp4_workload_lpe_3scale_admin_email_domain=<change me>          # e.g redhat.com

$ create_tenants: True                  #   If tenant accounts need to be created as part of the provisioning. Default is `True`
ocp4_workload_lpe_3scale_tenant_admin_name_base: tenant-admin             #   Name of the Admin user in each tenant.
ocp4_workload_lpe_3scale_tenant_user_name_base: user                #   Name of the OCP users in the cluster. Default is `user`.
ocp4_workload_lpe_3scale_tenant_admin_password: admin            #   Default password for each tenant admin.
ocp4_workload_lpe_3scale_create_gws_with_each_tenant: True       #   To create a Gateway Project & deploy APIcast staging & production as self-managed gateways for each tenant.
-----

=== Provision  API CICD Lab

The OCP namespace for 3scale multi-tenant app will be owned by the admin user.


. Execute:
+
-----

# 3scale Multitenant API Manager & Tenants Provisoning
$  ansible-playbook ${VERBOSITY} -i ${TARGET_HOST}, ./ansible/configs/ocp-workloads/ocp-workload.yml \
    -e"ansible_ssh_private_key_file=${ANSIBLE_USER_KEY_FILE}" \
    -e"ansible_user=${ANSIBLE_USER}" \
    -e"ocp_username=${OCP_USERNAME}" \
    -e"ocp_workload=ocp4_workload_lpe_3scale" \
    -e"subdomain_base_suffix=${BASE_DOMAIN}" \
    -e"silent=False" \
    -e"guid=${GUID}" \
    -e"ACTION=create \
    -e"become_override=False" \
    -e"output_dir=$HOME/Development/agnosticd-output/${WORKLOAD}" \
    -e"cloud_provider=${CLOUD_PROVIDER}" \
    -e"target_host=bastion.${GUID}.${BASE_DOMAIN}"
-----

. After about 5 minutes, provisioning of the  API Manager should complete.


=== Remove Provisioned Artifacts

Run the remove workload with *ACTION=remove* in order to remove all of the projects created as part of this workload. 

. Execute:
+
----

$ ansible-playbook ${VERBOSITY} -i ${TARGET_HOST}, ./ansible/configs/ocp-workloads/ocp-workload.yml \
    -e"ansible_ssh_private_key_file=${ANSIBLE_USER_KEY_FILE}" \
    -e"ansible_user=${ANSIBLE_USER}" \
    -e"ocp_username=${OCP_USERNAME}" \
    -e"ocp_workload=ocp4_workload_lpe_3scale" \
    -e"subdomain_base_suffix=${BASE_DOMAIN}" \
    -e"silent=False" \
    -e"guid=${GUID}" \
    -e"ACTION=remove \
    -e"become_override=False" \
    -e"output_dir=$HOME/Development/agnosticd-output/${WORKLOAD}" \
    -e"cloud_provider=${CLOUD_PROVIDER}" \
    -e"target_host=bastion.${GUID}.${BASE_DOMAIN}"

----

All the projects created as part of this workload will be removed.



