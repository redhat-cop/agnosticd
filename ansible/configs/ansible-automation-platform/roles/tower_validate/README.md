Role Name
=========

A role to validate the setup of a Tower installation.
It validates that it can, with the given credentials:

1. ping
2. get the configuration pages
3. validates that the number of instances and instance groups is correct,
4. as well as if the licenses has enough nodes and days left.

Requirements
------------

Access to an Ansible Tower or Ansible Controller instance

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
