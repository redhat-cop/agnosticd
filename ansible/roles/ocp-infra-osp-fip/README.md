OCP-Infra-OSP-FIP
=========

This role configured an OCP cluster running on OpenStack to use a Floating IP.

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
  gather_facts: False
  become: yes
  run_once: true
  when: cloud_provider == "osp"
  roles:
    - { role: "ocp-infra-osp-fip" }

License
-------

BSD

Author Information
------------------

Wolfgang Kulhanek (wkulhane@redhat.com)
