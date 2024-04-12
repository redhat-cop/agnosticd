Role Name
=========

This role corresponds with the 2024 Red Hat Summit Lab LB1401.

It's purpose is to create fake domains inside the /etc/hosts file for all instances in the environment, assign these hosts new internal hostnames after deployment, and configure the lab-user to be ansible ready with collections, python libraries, and an updated /etc/ansible/hosts file.

Requirements
------------
Collections:
- community.general
- ansible.windows

python3 libraries:
- pywinrm

Role Variables
--------------

Most of the variables are internal for this role. To update which custom collections are uploaded into /home/lab-user/.ansible/collections/ansible-collections/ modify the custom_collections dict.

custom_collections:
- name: "rhel_system_roles-1.23.0.tar.gz"
  collection_path: "rhel_system_roles"
  url: "https://example.com:/rhel_system_roles-1.23.0.tar.gz"
- name: "redhat-rhel_idm-1.12.1.tar.gz"
  collection_path: "rhel_idm"
  url: "https://example.com/redhat-rhel_idm-1.12.1.tar.gz"

Dependencies
------------
Variables from deployer:
- guid
- common_password


License
-------

BSD

Author Information
------------------

Wilson Harris
Red Hat
