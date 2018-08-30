Openwhisk
=========

This role installs the Openwhisk on a 3.9 or higher OCP Cluster.

Requirements
------------

Needs to be run after OCP has been set up

Role Variables
--------------

None

Dependencies
------------

None

Example Playbook
----------------

  hosts: masters
  run_once: true
  gather_facts: False
  become: yes
  vars_files:
    - "{{ ANSIBLE_REPO_PATH }}/configs/{{ env_type }}/env_vars.yml"
  roles:
    - { role: "{{ ANSIBLE_REPO_PATH }}/roles/openwhisk" }

License
-------

BSD

Author Information
------------------

Wolfgang Kulhanek (wkulhane@redhat.com)
