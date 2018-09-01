# Ansible Role: Gogs

[![Build Status](https://travis-ci.org/geerlingguy/ansible-role-gogs.svg?branch=master)](https://travis-ci.org/geerlingguy/ansible-role-gogs)

Installs [Gogs](https://github.com/gogits/gogs), a Go-based front-end to Git, on RedHat or Debian-based linux systems.

After the playbook is finished, visit the gogs server (on port 3000 by default), and you will be redirected to the /install page, where you can configure an administrator account and other default options.

## Requirements

Requires git (via `geerlingguy.git`), and at least the Gogs HTTP port (3000 by default) open on your system's firewall. Install MySQL (e.g. via `geerlingguy.mysql`) prior to installing Gogs if you would like to use MySQL instead of built-in SQLite support.

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

    gogs_user: git
    gogs_user_home: /home/git

The user and home under which Gogs will run and be installed.

    gogs_binary_url: https://github.com/gogits/gogs/releases/download/v0.3.1/linux_amd64.zip

Download URL for the Gogs binary.

    gogs_http_port: "3000"

HTTP port over which Gogs will be accessed.

    gogs_use_mysql: false
    gogs_db_name: gogs
    gogs_db_username: gogs
    gogs_db_password: root

MySQL database support. Set `gogs_use_mysql` to `true` to configure MySQL for gogs, using the database name, username, and password defined by the respective variables.

## Dependencies

  - geerlingguy.git

## Example Playbook

    - hosts: servers
      vars_files:
        - vars/main.yml
      roles:
        - geerlingguy.gogs

*Inside `vars/main.yml`*:

    gogs_http_port: "8080"

## License

MIT / BSD

## Author Information

This role was created in 2014 by [Jeff Geerling](https://www.jeffgeerling.com/), author of [Ansible for DevOps](https://www.ansiblefordevops.com/).
