Role Name
=========

open-env-azure-add-user-to-subscription

Role Description
================

This role does the following:
- Checks if the user is a Red Hat associate (member of Red Hat Active Directory)
- Gets and locks an Azure subscription from a pool from a function in Azure backed by a CosmosDB database
- Adds the 'Contributor' role for the Red Hat user to the subscription
- Tags the subscription with GUID and email

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

Authors Information
------------------
prutledg@redhat.com
hmourad@redhat.com
