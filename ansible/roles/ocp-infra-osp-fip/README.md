AWS-Broker
=========

This role installs the AWS Broker on a 3.7 or higher OCP Cluster.

Refer to the Readme on how to create proper AWS Credentials to be passed to the services:
https://github.com/awslabs/aws-servicebroker-documentation/blob/master/getting-started.md

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
  roles:
    - { role: "aws-broker" }

License
-------

BSD

Author Information
------------------

Wolfgang Kulhanek (wkulhane@redhat.com)
