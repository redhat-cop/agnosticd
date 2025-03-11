

Role: gitlab
============

This role installs and configure gitlab. Also setup & configure firewalld and it's rules.

Requirements
------------

* Repository or subscription must be pre-configure to install dependencies packages 

Role Variables
--------------



Example Playbook
----------------

How to use the role in playbook 

```
[user@node ~]$ cat sample_vars.yml
firewall_services:
  - ssh
  - RH-Satellite-6
firewall_ports:
  - 22/tcp
  - 80/tcp
  - 443/tcp

[user@node ~]$ cat playbook.yml
- hosts: all
  roles:
    - gitlab

[user@node ~]$ ansible-playbook playbook.yml -e @./sample_vars.yml
```
License
-------
GPLv3

Author Information
------------------
Mitesh The Mouse <mitsharm@redhat.com>

