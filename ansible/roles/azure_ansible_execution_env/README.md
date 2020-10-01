Role Name
=========

`azure_ansible_execution_env` creates the necessary environment for ansible to run locally and execute azure based playbooks.
It assumes, in its current, incarnation that it will used either with a system wide installation of ansible or via a virtualenv.

It does not itself use a virtualenv for the az cli (Azure CLI) but installs system wide via an rpm.
This is due to reported issues with the cli and Azure python dependencies co-existing in a virtualenv.

Role draws on the flow outline here: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-yum


Requirements
------------

None

Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
