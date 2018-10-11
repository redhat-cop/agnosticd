# Quay Builder

Ansible Role to help configure [Quay Builder](https://coreos.com/quay-enterprise/docs/latest/build-support.html) on a standalone instance.

## Requirements

A Linux Distribution which supports `systemd` and `package` modules along with docker install and configured.

## Role Variables

This role contains a number of variables to customize the deployment of Clair. The following are some of the most important that may need to be configured

| Name | Description | Default|
|---|---|---|
|quay_builder_image|Quay builder image|`quay.io/coreos/quay-builder:v2.9.3`|
|quay_builder_config_dir|Directory for Quay builder configurations| `/var/lib/quay-builder/config`| 
|quay_enterprise_hostname|Hostname of the Quay Enterprise instance| |
|quay_builder_ssl_trust_configure|Configure SSL trust|`False`|
|quay_builder_ssl_trust_src_file|Location of the SSL certificates to populate use for TLS trust when enabled|`/tmp/quay-builder-ssl-trust.crt`|


## Dependencies

* [container-storage-setup](../container-storage-setup)
* [config-docker](../config-docker)


## Example Playbook

```
- name: Install Quay Builder
  hosts: quay_builder
  roles:
    - role: config-quay-builder
```

## License

Apache License 2.0

## Author Information

Red Hat Community of Practice & staff of the Red Hat Open Innovation Labs.