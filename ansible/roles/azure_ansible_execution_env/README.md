azure_ansible_execution_env
=========

Installs the azure cli as an rpm instead of a pip package.
Avoids python dependency issues with system, user, or venv type deployments.

Can be extended to other azure related assets and resources.
Designed with Ansible Tower nodes and isolated nodes as the goal, but will work with standard control node.

Requirements
------------

None.

Role Variables
--------------


azure_ansible_execution_env_rpm_key - RPM Key

Dependencies
------------


ne

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - azure_ansible_execution_env

License
-------

BSD

Author Information
------------------

Original author: Tony Kay (tok) tok@redhat.com
