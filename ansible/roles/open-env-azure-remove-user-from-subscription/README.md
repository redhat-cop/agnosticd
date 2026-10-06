Role Name
=========

open-env-azure-remove-user-from-subscription

Role Description
================

This role does the following:
- Revokes user access and applies a temporary deny-creation policy
- Pre-cleans Recovery Services / Azure DevOps blockers
- Runs hardened Azure cleanup via ``azure_openenv_cleanup_subscription``
  (ARO + NAT teardown, AIServices/Resource Mover blockers, topo-sorted RGs)
- Clears subscription tags
- Unallocates the pool ID from the pool manager database (when used outside
  Sandbox API). Sandbox API–owned sandboxes normally release the pool themselves.

Requirements
------------

Collection         Version
------------------ -------
azure.azcollection 1.12.0
azure.rm           0.0.6

Python packages (execution environment): azure-identity, azure-mgmt-resource,
azure-mgmt-network, requests. Optional but recommended:
``azure-mgmt-redhatopenshift`` (otherwise ARO delete uses ``az aro``).

Role Variables
--------------

guid - the guid to use for the deployment
requester_email - an email address to invite
az_pool_id / azure_pool_api_secret / az_function_* - pool manager API

License
-------

BSD

Author Information
------------------
prutledg@redhat.com
hmourad@redhat.com
