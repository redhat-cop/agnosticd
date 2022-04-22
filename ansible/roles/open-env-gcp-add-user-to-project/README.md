Role Name
=========

open-env-gcp-add-user-to-project

Role Description
================

This role does the following:
- Checks if the user is a Red Hat associate
- Creates a GCP project
- Adds the user to the project

Requirements
------------

Collection   Version
------------ -------
google.cloud 1.0.2

Role Variables
--------------

guid - the guid to use for the deployment
requester_email - the user's email address (must match GCP principal)
gcp_admin_group - group in GCP that has admin access to all projects, must start with group:

Dependencies
------------

License
-------

BSD

Authors Information
------------------
prutledg@redhat.com
