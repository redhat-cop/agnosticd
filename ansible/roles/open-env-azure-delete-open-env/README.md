Role Name
=========

open-env-azure-delete-open-env

Role Description
================

Legacy / shared-subscription cleanup for ARO catalog items that still call this
role. Deletes openenv AD users, guid-scoped Azure resources via
``azure_openenv_cleanup_subscription`` (ARO + blockers + RG), and app
registrations.

For pooled subscription sandboxes prefer Sandbox API cleanup, or
``open-env-azure-remove-user-from-subscription`` for AgnosticD-owned pool
teardown. This role never deletes the entire subscription — only
``openenv-{{ guid }}``.

Requirements
------------

Collection         Version
------------------ -------
azure.azcollection 1.9.0
azure.rm           0.0.6

Also requires ``azure-mgmt-redhatopenshift`` in the execution environment
(see config ``requirements_azure.txt``).

Role Variables
--------------

guid - the guid to use for the deployment
azure_subscription_id - subscription containing openenv-{{ guid }}
azure_user / azure_user_password / azure_tenant / azure_user_domain

License
-------

BSD

Author Information
------------------

prutledg@redhat.com
