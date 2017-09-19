==================
ansible-role-shade
==================

Ansible role to manage Shade

* License: Apache License, Version 2.0
* Documentation: https://ansible-role-shade.readthedocs.org
* Source: https://git.openstack.org/cgit/openstack/ansible-role-shade
* Bugs: https://bugs.launchpad.net/ansible-role-shade

Description
-----------

Shade is a simple client library for operating OpenStack clouds.

Requirements
------------

See `bindep.txt` for role dependencies.

Packages
~~~~~~~~

Package repository index files should be up to date before using this role, we
do not manage them.

Role Variables
--------------

Dependencies
------------

Example Playbook
----------------

.. code-block:: yaml

    - name: Install shade
      hosts: nodepool
      roles:
        - ansible-role-shade
