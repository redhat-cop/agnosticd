# Quay Enterprise

Ansible Role to help configure [Quay Enterprise](https://coreos.com/quay-enterprise/) on a standalone instance.

## Requirements

A Linux Distribution which supports `systemd` and `package` modules along with docker install and configured.

## Role Variables

This role contains a number of variables to customize the deployment of Quay Enterprise. The following are some of the most important that may need to be configured

| Name | Description | Default|
|---|---|---|
|quay_registry_server|Image server containing Quay images|`quay.io`|
|quay_registry_auth|Authentication credentials to pull images from the Quay registry| |
|quay_database_type|Database to use (`postgresql` or `mysql`)|`postgresql`|
|postgresql_image|PostgreSQL image|`registry.access.redhat.com/rhscl/postgresql-96-rhel7:latest`|
|mysql_image|MySQL image|`registry.access.redhat.com/rhscl/mysql-57-rhel7:latest`|
|redis_image|Redis image|`quay.io/quay/redis:latest`|
|quay_image|Quay Enterprise image|`quay.io/coreos/quay:v2.9.2`|
|quay_server_hostname|Hostname configured within Quay| `inventory_hostname` Ansible variable|
|quay_superuser_username|Quay superuser user name| |
|quay_superuser_password|Quay superuser user password| |
|quay_registry_email|Quay superuser email address| |

If `quay_superuser_username`, `quay_superuser_password` and `quay_superuser_email` are provided, the initial setup and configuration of Quay will be completed automatically.

## Dependencies

* [container-storage-setup](../container-storage-setup)
* [config-docker](../config-docker)

## Example Inventory

```
quay_registry_auth: "<Base64 encoded value in Basic Authentication format (username:password)>"
```

## Example Playbook

```
- name: Install Quay Enterprise
  hosts: quay_enterprise
  roles:
    - role: config-quay-enterprise
```

## License

Apache License 2.0

## Author Information

Red Hat Community of Practice & staff of the Red Hat Open Innovation Labs.