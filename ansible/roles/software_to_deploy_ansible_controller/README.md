software_to_deploy_ansible_controller
=========

Installs, and opotionally licenses via manifest, Ansible controller

Requirements
------------

None.

Role Variables
--------------


Dependencies
------------


Example Playbook
----------------

```yaml
- name: Install Ansible controller
  hosts: controllers
  become: true
  gather_facts: false

  roles:
     - software_to_deploy_ansible_controller
```

License
-------

BSD

Author Information
------------------

Original author: Tony Kay (tok) tok@redhat.com
