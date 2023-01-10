letsencrypt\_ca\_trust
====================

A very simple role to deploy the CA trust from Let's Encrypt

Requirements
------------

update-ca-trust needs to have been installed, e.g. through the ca-certificates package.

Role Variables
--------------

None.

Dependencies
------------

None.

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: letsencrypt_ca_trust }

License
-------

BSD

Author Information
------------------

Eric Lavarde, Red Hat, for AgnosticD
