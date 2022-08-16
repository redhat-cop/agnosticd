aap\_pah\_cert\_issue
==================

Issue and install Let's Encrypt certificates to PAH

Requirements
------------

Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.

Role Variables
--------------

See [defaults/main.yml](defaults/main.yml).

Dependencies
------------

n/a

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
