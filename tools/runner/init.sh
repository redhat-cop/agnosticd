#!/bin/bash

export AGD_GUID=$(uuidgen | cut -d - -f 2 | tr '[:upper:]' '[:lower:]')
export AGD_AWS_ACCESS_KEY_ID=$1
export AGD_AWS_SECRET_ACCESS_KEY=$2
export AGD_SANDBOX=$3
export AGD_AWS_REGION=us-east-2
export AGD_HOME=${AGNOSTICD_HOME:-$(pwd)}
export AGD_EXECUTION_DIR=ansible/workdir/.agnosticd/${AGD_GUID}
export AGD_SECRETS_YAML=ansible/workdir/.agnosticd/secrets.yml

mkdir -p ${AGD_HOME}/${AGD_EXECUTION_DIR}

cat << EOF >${AGD_HOME}/${AGD_EXECUTION_DIR}/rosa.yml
---
# -------------------------------------------------------------------
# User specific
# -------------------------------------------------------------------
guid: "${AGD_GUID}"
subdomain_base_suffix: .${AGD_SANDBOX}.opentlc.com
output_dir: /runner/agnosticd/${AGD_EXECUTION_DIR}

# -------------------------------------------------------------------
# Top level vars
# -------------------------------------------------------------------
cloud_provider: ec2
env_type: rosa-consolidated

# -------------------------------------------------------------------
# Other vars
# -------------------------------------------------------------------
aws_region: ${AGD_AWS_REGION}
agnosticd_aws_capacity_reservation_enable: false

rosa_version: latest
rosa_version_base: "openshift-v4.17"
rosa_deploy_hcp: true
rosa_compute_machine_type: m6a.2xlarge
rosa_compute_replicas: 2
rosa_setup_cluster_admin_login: true

bastion_instance_type: t2.small
bastion_instance_image: RHEL95GOLD-latest

install_student_user: false

agnosticd_preserve_user_data: true

# -------------------------------------------------------------------
# Workloads
# -------------------------------------------------------------------
infra_workloads:
- ocp4_workload_authentication_rosa

# -------------------------------------------------------------------
# ocp4_workload_authentication_rosa
# -------------------------------------------------------------------
ocp4_workload_authentication_rosa_user_count: 10
ocp4_workload_authentication_rosa_user_base: user
ocp4_workload_authentication_rosa_user_password: openshift
ocp4_workload_authentication_rosa_admin: false

ocp4_workload_authentication_rosa_token: "{{ rosa_token }}"

ocp4_workload_authentication_rosa_aws_access_key_id: "{{ aws_access_key_id | mandatory }}"
ocp4_workload_authentication_rosa_aws_secret_access_key: "{{ aws_secret_access_key | mandatory }}"
ocp4_workload_authentication_rosa_aws_region: "{{ aws_region | mandatory }}"

EOF

cat << EOF >${AGD_HOME}/${AGD_EXECUTION_DIR}/ocp4-cluster.yml
---
# -------------------------------------------------------------------
# User specific
# -------------------------------------------------------------------
guid: "${AGD_GUID}"
subdomain_base_suffix: .${AGD_SANDBOX}.opentlc.com
output_dir: /runner/agnosticd/${AGD_EXECUTION_DIR}

# -------------------------------------------------------------------
# Top level vars
# -------------------------------------------------------------------
cloud_provider: ec2
env_type: ocp4-cluster
software_to_deploy: openshift4
agnosticd_preserve_user_data: true

# -------------------------------------------------------------------
# VM configuration
# -------------------------------------------------------------------
master_instance_type: m6a.4xlarge
master_instance_count: 1
worker_instance_type: m6a.2xlarge
worker_instance_count: 0
bastion_instance_type: t2.small
bastion_instance_image: RHEL95GOLD-latest
aws_region: ${AGD_AWS_REGION}
agnosticd_aws_capacity_reservation_enable: false

# -------------------------------------------------------------------
# OpenShift installer
# -------------------------------------------------------------------
ocp4_installer_version: "4.19"
ocp4_installer_root_url: https://mirror.openshift.com/pub/openshift-v4/clients

# -------------------------------------------------------------------
# Bastion
# -------------------------------------------------------------------
install_student_user: false

# -------------------------------------------------------------------
# Workloads
# -------------------------------------------------------------------
infra_workloads:
  - ocp4_workload_rhsso_authentication
  - ocp4_workload_cert_manager

# -------------------------------------------------------------------
# Workload: ocp4_workload_cert_manager
# -------------------------------------------------------------------
ocp4_workload_cert_manager_channel: stable-v1
ocp4_workload_cert_manager_install_ingress_certificates: true
ocp4_workload_cert_manager_install_api_certificates: false

# -------------------------------------------------------------------
# ocp4_workload_rhsso_authentication
# -------------------------------------------------------------------
ocp4_workload_rhsso_authentication_channel: stable
ocp4_workload_rhsso_authentication_admin_username: admin
ocp4_workload_rhsso_authentication_admin_password: r3dh4t1!
ocp4_workload_rhsso_authentication_user_count: 5
ocp4_workload_rhsso_authentication_user_name_base: user
ocp4_workload_rhsso_authentication_user_password: openshift
EOF

cat << EOF >${AGD_HOME}/${AGD_EXECUTION_DIR}/ocp-workloads-base.yml
---
# -------------------------------------------------------------------
# User specific
# -------------------------------------------------------------------
target_host: bastion.${AGD_GUID}.${AGD_SANDBOX}.opentlc.com
ansible_user: ec2-user
ansible_ssh_private_key_file: /runner/agnosticd/${AGD_EXECUTION_DIR}/ssh_provision_${AGD_GUID}
output_dir: /runner/agnosticd/${AGD_EXECUTION_DIR}

# -------------------------------------------------------------------
# Top level vars
# -------------------------------------------------------------------
cloud_provider: none
env_type: ocp-workloads

agnosticd_preserve_user_data: true

EOF

if [ -f "${AGD_HOME}/$AGD_SECRETS_YAML" ]; then
    echo "INFO: Secret file found at ${AGD_HOME}/${AGD_SECRETS_YAML}"
else
    echo "WARNING: Secret file not found at ${AGD_HOME}/${AGD_SECRETS_YAML}"
    echo "WARNING: New secret file will be created at ${AGD_HOME}/${AGD_SECRETS_YAML}"
    echo "WARNING: Add your secrets in that file before proceeding"
    cat << EOF >${AGD_HOME}/${AGD_SECRETS_YAML}
# -------------------------------------------------------------------
# Satellite
# -------------------------------------------------------------------
repo_method: satellite
update_packages: true
set_repositories_satellite_ha: true
set_repositories_force_register: true
set_repositories_satellite_url: demosat-ha.infra.demo.redhat.com
set_repositories_satellite_hostname: demosat-ha.infra.demo.redhat.com
set_repositories_satellite_org: Red_Hat_RHDP_Labs
# set_repositories_satellite_activationkey: [redacted]
# ansible localhost -m debug -a "var=satellite_activationkey" --extra-vars="@${AGV_HOME}/includes/secrets/demosat-rhel-8-and-9-latest.yaml" --ask-vault-pass

# Employee subscription (needs testing)
# rhel_subscription_user: user@example.com
# rhel_subscription_pass: [redacted]

# -------------------------------------------------------------------
# OCP pull secret
# -------------------------------------------------------------------
# Get yours from https://console.redhat.com/openshift/install/pull-secret
# ocp4_pull_secret:
#   {
#     "auths":
#       {
#         "cloud.openshift.com": {"auth":"xyz","email":"me@acme.com"},
#         "quay.io": {"auth":"xyz","email":"me@acme.com"},
#         "registry.connect.redhat.com":{"auth":"xyz","email":"me@acme.com"},
#         "registry.redhat.io":{"auth":"xyz","email":"me@acme.com"}
#       }
#   }

# -------------------------------------------------------------------
# ROSA
# -------------------------------------------------------------------
gpte_rosa_token: [redacted]
aws_billing_account_id: [redacted]

EOF
fi

echo "INFO: Remember to 'source' it"
echo "INFO: source init.sh aws-access-key-id aws-secret-access-key sandbox"
