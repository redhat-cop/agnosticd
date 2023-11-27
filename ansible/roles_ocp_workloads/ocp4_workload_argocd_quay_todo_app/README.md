TODO Application with Quarkus HELM Chart repo
=========

This is a simple TODO application that allows users to create, read, update, and delete tasks from a database. The application is built using the Quarkus framework, which is a Kubernetes-native Java framework. The application is also packaged as a Helm chart, which makes it easy to deploy and manage on Kubernetes.

See The [TODO Application with Quarkus HELM Chart repo](https://github.com/tosin2013/todo-demo-app-helmrepo/blob/main/openshift-pipelines/README.md) for use of this demo.

[Deploy using Github Actions](https://github.com/tosin2013/todo-demo-app-helmrepo/blob/main/openshift-pipelines/github-actions.md)

Requirements
------------

* OpenShift 4.12 cluster installed
* Ansible 2.9 or higher
```
sudo pip3 install openshift pyyaml kubernetes jmespath 
ansible-galaxy collection install kubernetes.core community.general
```


Role Variables
--------------

Role Variables are found in defaults/main.yml

```
become_override: false
ocp_username: system:admin
silent: false

ocp4_workload_gitea_user: user1
ocp4_workload_gitea_operator_create_admin: true
ocp4_workload_gitea_operator_create_users: true
ocp4_workload_gitea_operator_migrate_repositories: true
ocp4_workload_gitea_operator_gitea_image_tag: 1.19.3
ocp4_workload_gitea_operator_repositories_list:
- repo: "https://github.com/tosin2013/todo-demo-app-helmrepo.git"
  name: "todo-demo-app-helmrepo"
  private: false

## OpenShift Pipelines

ocp4_workload_pipelines_defaults:
  tkn_version: 0.31.1
  channel: latest
  automatic_install_plan_approval: true
  starting_csv: ""

```

Dependencies
------------
* ocp4_workload_gitea_operator
* ocp4_workload_pipelines

Example Playbook
----------------

Deploy a Workload with the `ocp-workload` playbook

```
TARGET_HOST="bastion.wk.red.osp.opentlc.com"
OCP_USERNAME="lab-user"
WORKLOAD="ocp4_workload_argocd_quay_todo_app"
GUID=wk
```
**Generate extra vars**
```
cat >extra_vars.yaml<<EOF
ocp4_workload_gitea_operator_create_admin: true
ocp4_workload_gitea_operator_create_users: true
ocp4_workload_gitea_operator_migrate_repositories: true
ocp4_workload_gitea_operator_gitea_image_tag: 1.19.3
ocp4_workload_gitea_operator_repositories_list:
- repo: "https://github.com/tosin2013/todo-demo-app-helmrepo.git"
  name: "todo-demo-app-helmrepo"
  private: false
EOF
```


**a TARGET_HOST is specified in the command line, without using an inventory file**
```
ansible-playbook -i ${TARGET_HOST}, ./configs/ocp-workloads/ocp-workload.yml \
    -e"ansible_ssh_private_key_file=~/.ssh/keytoyourhost.pem" \
    -e"ansible_user=cloud-user" \
    -e"ocp_username=${OCP_USERNAME}" \
    -e"ocp_workload=${WORKLOAD}" \
    -e"silent=False" \
    -e"guid=${GUID}" \
    -e"@extra_vars.yaml" \
    -e"ACTION=create"
```

To Delete an environment
----
```
TARGET_HOST="bastion.wk.red.osp.opentlc.com"
OCP_USERNAME="lab-user"
WORKLOAD="ocp4_workload_argocd_quay_todo_app"
GUID=wk
```

**TARGET_HOST is specified in the command line, without using an inventory file**
```
ansible-playbook -i ${TARGET_HOST}, ./configs/ocp-workloads/ocp-workload.yml \
    -e"ansible_ssh_private_key_file=~/.ssh/keytoyourhost.pem" \
    -e"ansible_user=ec2-user" \
    -e"ocp_username=${OCP_USERNAME}" \
    -e"ocp_workload=${WORKLOAD}" \
    -e"guid=${GUID}" \
    -e"@extra_vars.yaml" \
    -e"ACTION=remove"
```

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).

