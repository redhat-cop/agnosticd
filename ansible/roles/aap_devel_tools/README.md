aap\_devel\_tools
===============

Install AAP development tools

Requirements
------------

Availability of the AAP RPM repository

Role Variables
--------------

see [defaults/main.yml](defaults/main.yml)

Dependencies
------------

n/a

Example Playbook
----------------

    - hosts: workstations
      roles:
         - { role: aap_devel_tools, aap_devel_tools_repos_enable: true }

License
-------

MIT

Author Information
------------------

Eric Lavarde as part of the AgnosticD framework
