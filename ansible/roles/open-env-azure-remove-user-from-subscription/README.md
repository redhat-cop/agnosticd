Role Name
=========

open-env-azure-remove-user-from-subscription

Role Description
================

This role does the following:
- Removes all resource groups attached to the Azure subscription
- Removes all tags from the Azure subscription
- Removes a Red Hat user's access from an Azure subscription
- Unallocates the pool ID from the database

Requirements
------------

Collection         Version
------------------ -------
azure.azcollection 1.12.0
azure.rm           0.0.6

Role Variables
--------------

guid - the guid to use for the deployment
requester_email - an email address to invite

Dependencies
------------

License
-------

BSD

Author Information
------------------
prutledg@redhat.com
hmourad@redhat.com
