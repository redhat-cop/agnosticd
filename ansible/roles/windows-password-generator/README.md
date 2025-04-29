windows-password-gen
====================

This role uses ansible.bultin.set_fact to produce a random password that is within the requirements for a windows server.

Passwords must meet at least three of the following four criteria:
- Include at least one uppercase letter (A-Z).
- Include at least one lowercase letter (a-z).
- Include at least one digit (0-9).
- Include at least one special character (e.g., !@#$%^&*()).

Requirements
------------
Ansible Core

ansible.cfg
-----------
- Configure ansible.cfg with local parameters for custom lookup plugin locations
- Point ansible to the vault password file

Variables
---------

```yaml
windows_ready_password: >-
  {{ (lookup('ansible.builtin.password', '/dev/null length=3 chars=ascii_uppercase') +
      lookup('ansible.builtin.password', '/dev/null length=4 chars=ascii_lowercase') +
      lookup('ansible.builtin.password', '/dev/null length=1 chars=digits')) | list | shuffle | join('') }}
```

Author Information
------------------

Wilson Harris
Red Hat
April 23 2024
