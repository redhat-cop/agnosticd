# Redis

Ansible Role to help configure [PostgreSQL](https://www.postgresql.org/) on a standalone instance.

## Requirements

A Linux Distribution which supports `systemd` along with docker install and configured

## Role Variables

This role contains a number of variables to customize the deployment of PostgreSQL. The following are some of the most important that may need to be configured

| Name | Description | Default|
|---|---|---|
|postgresql_image|PostgreSQL image|`registry.access.redhat.com/rhscl/postgresql-96-rhel7:latest`|
|postgresql_storage_dir|Directory to persistently storage data from the PostgreSQL container|`/var/lib/postgresql`|
|postgresql_host_port|Port to expose on the host |`5432`|
|postgresql_username|Name of the standard user to create| |
|postgresql_password|Password of the standard user| |
|postgresql_root_username|Name of the admin user to create |`root`|
|postgresql_root_password|Password of the admin user | |

## Dependencies

None

## Example Playbook

```
- name: Install PostgreSQL
  hosts: postgresql
  roles:
    - role: config-postgresql
```

## License

Apache License 2.0

## Author Information

Red Hat Community of Practice & staff of the Red Hat Open Innovation Labs.