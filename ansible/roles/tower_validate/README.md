Role Name
=========

A role to validate the setup of a Tower installation. It validates that it can ping and get
the configuration pages with the given credentials, and, if wished, validates that the
number of instances and instance groups is correct, as well as if the licenses has enough
nodes and days left.

Requirements
------------

Access

Role Variables
--------------

All the relevant variables are listed and available in [the defaults variables](defaults/main.yml).

Dependencies
------------

none.

Example Playbook
----------------

Assuming that the credentials are present in your inventory, you could check the number of
remaining license days like this:

    - hosts: towers
      roles:
         - { role: tower_validate, tower_expected_licensed_min_days: 42 }

License
-------

BSD

Author Information
------------------

Eric Lavarde <elavarde@redhat.com>
