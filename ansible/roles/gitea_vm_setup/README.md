gitea\_vm\_setup
==============

Setup Gitea as VM workload, i.e. not as container

Requirements
------------

* an nginx server must have been setup and configured
* certificates must already have been installed at the expected places, by default:
    * `ssl_certificate_key /etc/pki/nginx/private/server.key;`
    * `ssl_certificate /etc/pki/nginx/server.crt;`

Role Variables
--------------

All the variables from [l3d.git.gitea](https://galaxy.ansible.com/ui/repo/published/l3d/git/content/role/gitea/) are applicable, plus the ones described in `defaults/main.yml`.

Dependencies
------------

* the collection `l3d.git` must be installed

Example Playbook
----------------

    - name: Install and configure Gitea on VM
      include_role:
        name: gitea_vm_setup
      vars:
        gitea_db_pasword: "{{ student_password }}"  # shouldn't matter for sqlite3

License
-------

BSD

Author Information
------------------

Eric Lavarde <elavarde@redhat.com> for the Ansible Labs Crew
