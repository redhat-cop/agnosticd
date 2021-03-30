OSB-Azure
=========

This role installs the Open Service Broker for Azure on a 3.10 or higher OCP Cluster.

Main URL: https://osba.sh/

Documentation: https://github.com/Azure/open-service-broker-azure/blob/master/README.md

Requirements
------------

Needs to be run after OCP has been set up

Role Variables
--------------

Needs some details about the Azure instance, there are no default values. The current
values are names are from GPTE's naming standard.

azure_tenant: 00000000-1111-2222-3333-444444444444
azure_subscription_id: 55555555-6666-7777-8888-999999999999
azure_service_principal: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
bindPassword: 'SetMeToSomething'


Dependencies
------------

Requires the Service Catalog to be installed in OCP

Example Playbook
----------------

  hosts: masters
  gather_facts: False
  become: yes
  run_once: true
  roles:
    - { role: "ocp-infra-azure-service-broker" }

License
-------

BSD

Author Information
------------------

Vince Power (vpower@redhat.com)
