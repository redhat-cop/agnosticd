aap\_pah\_cert\_issue
==================

Issue and install Let's Encrypt certificates to PAH

Requirements
------------

n/a

Role Variables
--------------

See [defaults/main.yml](defaults/main.yml).

Dependencies
------------

The Let's Encrypt CA isn't added to the CA trust, use the role `letsencrypt_ca_trust` for this.

Example Playbook
----------------

    - hosts: pah
      roles:
         - { role: aap_pah_cert_issue }

License
-------

MIT

Author Information
------------------

Eric Lavarde, as part of the AgnosticD framework, hosted by Red Hat CoP
