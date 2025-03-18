zero_touch_lockdown
=========

This role removes ssh information including:
* authorized_keys for lab-user and root
* *.pem , *.pub , and the ssh config files from lab-user and root

Requirements
------------

ansible.builtin

Role Variables
--------------

## student_name from role "common" to remove ssh credentials

zt_lockdown_users:
  - "{{ student_name }}"

zt_lockdown_ssh_dirs:
  - "/home/{{ student_name }}/.ssh"
  - "/root/.ssh"

zt_lockdown_auth_keys:
  - "/root/.ssh/authorized_keys"
  - "/home/{{ student_name }}/.ssh/authorized_keys"

## expressions for finding files to remove
zt_lockdown_sensitive_files:
  - "*.pem"
  - "*.pub"
  - "config"

Dependencies
------------

N/A

License
-------

BSD

Author Information
------------------

Wilson Harris
