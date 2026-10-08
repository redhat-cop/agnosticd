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

Pool ``/release`` is **not** called here — Sandbox API owns that (standalone
``clean_sub`` is the only ops exception).

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
az_pool_id / azure_pool_api_secret / az_function_show - pool lookup (show only; no release)

License
-------

BSD

Author Information
------------------
prutledg@redhat.com
hmourad@redhat.com
