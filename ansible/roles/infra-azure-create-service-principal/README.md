Azure-Create-Service-Principal
=========

This role creates a service principal in Azure with access to a specific subscription.

az service principal documentation: https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest

Requirements
------------

Needs to be run before OCP is installed as it is used in the install

Role Variables
--------------

Needs some details about the Azure instance, there are no default values. The current
values are names are from GPTE's naming standard.
    azure_tenant: 00000000-1111-2222-3333-444444444444
    azure_subscription_id: 55555555-6666-7777-8888-999999999999
    project_tag: 'ResourceGroupName'

This role will create two new variables and make them available
    ocp_azure_sp: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
    ocp_azure_pwd: 'GeneratedPassword'

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
    - { role: "infra-azure-create-service-principal" }

License
-------

BSD

Author Information
------------------

Vince Power (vpower@redhat.com)

