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
  roles:
    - { role: "openwhisk" }

License
-------

BSD

Author Information
------------------

Wolfgang Kulhanek (wkulhane@redhat.com)
