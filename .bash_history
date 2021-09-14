cd ansible
TARGET_HOST=localhost
GUID=7731
ocp_username=opentlc-mgr
# WORKLOAD SPECIFICS
WORKSHOP_PROJECT=lab
workloads=("ocp-workload-etherpad"            "ocp-workload-gogs"            "ocp4-workload-nexus-operator"            "ocp-workload-gogs-load-repository"            "ocp4-workload-homeroomlab-starter-guides")
for WORKLOAD in ${workloads[@]}; do   ansible-playbook -c local -i ${TARGET_HOST}, configs/ocp-workloads/ocp-workload.yml       -e ansible_python_interpreter=/opt/app-root/bin/python       -e ocp_workload=${WORKLOAD}       -e guid=${GUID}       -e project_name=${WORKSHOP_PROJECT}       -e etherpad_project=${WORKSHOP_PROJECT}       -e gogs_project=${WORKSHOP_PROJECT}       -e opsview_project=${WORKSHOP_PROJECT}       -e ocp4_workload_nexus_operator_project=${WORKSHOP_PROJECT}       -e project_name=${WORKSHOP_PROJECT}       -e ocp_username=${ocp_username}       --extra-vars '{"num_users": 5, "user_count": 5, "ACTION": "create"}'; done
ping 8.8.8.8
oc login --token=sha256~yKCe1m4fPTU7gIi0OcunYWl6I6UaiSA5p1El3j8gces --server=https://api.cluster-fd25.fd25.sandbox1851.opentlc.com:6443
oc delete project lab
oc login --token=sha256~yKCe1m4fPTU7gIi0OcunYWl6I6UaiSA5p1El3j8gces --server=https://api.cluster-fd25.fd25.sandbox1851.opentlc.com:6443
oc whoami
oc delete project lab
for WORKLOAD in ${workloads[@]}; do   ansible-playbook -c local -i ${TARGET_HOST}, configs/ocp-workloads/ocp-workload.yml       -e ansible_python_interpreter=/opt/app-root/bin/python       -e ocp_workload=${WORKLOAD}       -e guid=${GUID}       -e project_name=${WORKSHOP_PROJECT}       -e etherpad_project=${WORKSHOP_PROJECT}       -e gogs_project=${WORKSHOP_PROJECT}       -e opsview_project=${WORKSHOP_PROJECT}       -e ocp4_workload_nexus_operator_project=${WORKSHOP_PROJECT}       -e project_name=${WORKSHOP_PROJECT}       -e ocp_username=${ocp_username}       --extra-vars '{"num_users": 5, "user_count": 5, "ACTION": "create"}'; done
TARGET_HOST=localhost
GUID=7731
GUID=fd25
WORKSHOP_PROJECT=lab
workloads=("ocp-workload-etherpad"            "ocp-workload-gogs"            "ocp4-workload-nexus-operator"            "ocp-workload-gogs-load-repository"            "ocp4-workload-homeroomlab-starter-guides")
ocp_username=opentlc-mgr
for WORKLOAD in ${workloads[@]}; do   ansible-playbook -c local -i ${TARGET_HOST}, configs/ocp-workloads/ocp-workload.yml       -e ansible_python_interpreter=/opt/app-root/bin/python       -e ocp_workload=${WORKLOAD}       -e guid=${GUID}       -e project_name=${WORKSHOP_PROJECT}       -e etherpad_project=${WORKSHOP_PROJECT}       -e gogs_project=${WORKSHOP_PROJECT}       -e opsview_project=${WORKSHOP_PROJECT}       -e ocp4_workload_nexus_operator_project=${WORKSHOP_PROJECT}       -e project_name=${WORKSHOP_PROJECT}       -e ocp_username=${ocp_username}       --extra-vars '{"num_users": 5, "user_count": 5, "ACTION": "create"}'; done
cd ansible
for WORKLOAD in ${workloads[@]}; do   ansible-playbook -c local -i ${TARGET_HOST}, configs/ocp-workloads/ocp-workload.yml       -e ansible_python_interpreter=/opt/app-root/bin/python       -e ocp_workload=${WORKLOAD}       -e guid=${GUID}       -e project_name=${WORKSHOP_PROJECT}       -e etherpad_project=${WORKSHOP_PROJECT}       -e gogs_project=${WORKSHOP_PROJECT}       -e opsview_project=${WORKSHOP_PROJECT}       -e ocp4_workload_nexus_operator_project=${WORKSHOP_PROJECT}       -e project_name=${WORKSHOP_PROJECT}       -e ocp_username=${ocp_username}       --extra-vars '{"num_users": 5, "user_count": 5, "ACTION": "create"}'; done
oc delete project lab
---
- set_fact:
    user_count_end: "{{ (user_count_start | int) + (num_users | int) - 1 }}"
# Implement your Pre Workload deployment tasks here
- name: Ensure directory exists
  file:
    path: "{{ tmp_dir }}"
    state: directory
- name: Copy .kube/config and set env var
  copy:
    src: ~/.kube
    dest: "{{ tmp_dir }}"
    remote_src: true
## Figure out paths
- name: extract api_url
  shell: oc whoami --show-server
  register: api_url_r
- name: set the master
  set_fact:
    master_url: "{{ api_url_r.stdout | trim }}"
- name: extract console_url
  command: oc whoami --show-console
  register: console_url_r
- name: set the console
  set_fact:
    console_url: "{{ console_url_r.stdout | trim }}"
- name: extract route_subdomain
  k8s_info:
    api_version: config.openshift.io/v1
    kind: Ingress
    name: cluster
  register: r_ingress_config
  failed_when: r_ingress_config.resources | length < 1
- name: set the route
  set_fact:
    route_subdomain: "{{ r_ingress_config.resources[0].spec.domain }}"
- name: debug values
  debug:
    msg:
    - "master URL: {{ master_url }}"
    - "console URL: {{ console_url }}"
    - "route subdomain: {{ route_subdomain }}"
    - "ocp_username: {{ ocp_username }}"
# Leave these as the last tasks in the playbook
# For deployment onto a dedicated cluster (as part of the
# cluster deployment) set workload_shared_deployment to False
# This is the default so it does not have to be set explicitely
- name: pre_workload tasks complete
  debug:
    msg: "Pre-Workload tasks completed successfully."
  when:
  - not silent | bool
  - not workload_shared_deployment | default(false) | bool
# For RHPDS deployment (onto a shared cluster) set
# workload_shared_deployment to True
# (in the deploy script or AgnosticV configuration)
- name: pre_workload tasks complete
  debug:
    msg: "Pre-Software checks completed successfully"
  when:
  - not silent | bool
  - workload_shared_deployment | default(false) | bool
for WORKLOAD in ${workloads[@]}; do   ansible-playbook -c local -i ${TARGET_HOST}, configs/ocp-workloads/ocp-workload.yml       -e ansible_python_interpreter=/opt/app-root/bin/python       -e ocp_workload=${WORKLOAD}       -e guid=${GUID}       -e project_name=${WORKSHOP_PROJECT}       -e etherpad_project=${WORKSHOP_PROJECT}       -e gogs_project=${WORKSHOP_PROJECT}       -e opsview_project=${WORKSHOP_PROJECT}       -e ocp4_workload_nexus_operator_project=${WORKSHOP_PROJECT}       -e project_name=${WORKSHOP_PROJECT}       -e ocp_username=${ocp_username}       --extra-vars '{"num_users": 5, "user_count": 5, "ACTION": "create"}'; done
oc delete project lab
oc delete project lab
for WORKLOAD in ${workloads[@]}; do   ansible-playbook -c local -i ${TARGET_HOST}, configs/ocp-workloads/ocp-workload.yml       -e ansible_python_interpreter=/opt/app-root/bin/python       -e ocp_workload=${WORKLOAD}       -e guid=${GUID}       -e project_name=${WORKSHOP_PROJECT}       -e etherpad_project=${WORKSHOP_PROJECT}       -e gogs_project=${WORKSHOP_PROJECT}       -e opsview_project=${WORKSHOP_PROJECT}       -e ocp4_workload_nexus_operator_project=${WORKSHOP_PROJECT}       -e project_name=${WORKSHOP_PROJECT}       -e ocp_username=${ocp_username}       --extra-vars '{"num_users": 5, "user_count": 5, "ACTION": "create"}'; done
