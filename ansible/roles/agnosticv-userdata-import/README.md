# agnosticv-userdata-import

Import custom defined user_data with a yaml dictionary named agnosticv_importdata.

## Requirements
agnosticd_user_info

## Role Variables

agnosticv_importdata:
  bastion_ssh_command: "{{ bastion_ssh_command }}"
  bastion_public_hostname: "{{ bastion_public_hostname }}"
  bastion_ssh_user_name: "{{ bastion_ssh_user_name }}"
  bastion_ssh_password: "{{ bastion_ssh_password }}"
  node1_petname: "{{ node1_instance_name }}"
  node2_petname: "{{ node2_instance_name }}"
  node3_petname: "{{ node3_instance_name }}"
  node4_petname: "{{ node4_instance_name }}"
  automationcontroller_url: "https://ansible-1.{{ guid }}.example.opentlc.com"
  automationcontroller_user_password: "{{ common_password }}"
  automationcontroller_user_name: "admin"
  cockpit_user_name: "student"
  ssh_password: "{{ common_password }}"
  cockpit_user_password: "{{ common_password }}"
  vscode_server_password: "{{ common_password }}"
  vscode_server_url: "https://ansible-1.{{ guid }}.sandbox2418.opentlc.com/login/"
  page-links:
  - url: "{{ automationcontroller_url }}"
    text: "AAP Web UI"
  - url: "{{ cockpit_url }}"
    text: "RHEL Web Console"
  - url: "{{ vscode_server_url }}"
    text: "VS Code"
  - url: "https://github.com/redhat-cop/infra.leapp"
    text: "GitHub: infra.leapp"
  - url: "https://github.com/redhat-cop/infra.lvm_snapshots"
    text: "GitHub: infra.lvm_snapshots"
  - url: "https://github.com/oamg/leapp-supplements"
    text: "GitHub: leapp-supplements"
  - url: "https://www.martinfowler.com/ieeeSoftware/failFast.pdf"
    text: "Fail Fast"

License
-------

BSD

Author Information
------------------
Wilson Harris
Red Hat, GPTE
