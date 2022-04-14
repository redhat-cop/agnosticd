# tower_agnosticd_virtualenvs

Configure AgnosticD Python virtual environments on Ansible Tower nodes.
Creates a shell script in `/etc/cron.hourly/` and executes it to manage virtual environments for running AgnosticD on tower.

Requirements
------------

Root access to tower nodes.

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
      - role: tower_agnosticd_virtualenvs

License
-------

BSD

Author Information
------------------

Johnathan Kupferer <jkupfere@redhat.com>
