Azure-Create-Service-Principal
=========

This role deletes a service principal in Azure that is based on the resource group name

az service principal documentation: https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest

Requirements
------------

Will most likely be run as part of destroying an environment, it is a useful clean up task.

Role Variables
--------------

Needs some details about the Azure instance, there are no default values. The current
values are names are from GPTE's naming standard.
    project_tag: 'ResourceGroupName'

Dependencies
------------

Requires the Azure to be the cloud provider

Example Playbook
----------------

  hosts: masters
  gather_facts: False
  become: yes
  run_once: true
  roles:
    - { role: "infra-azure-delete-service-principal" }

License
-------

BSD

Author Information
------------------

Vince Power (vpower@redhat.com)

