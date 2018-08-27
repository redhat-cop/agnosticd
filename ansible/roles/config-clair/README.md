# Clair

Ansible Role to help configure [Clair](https://coreos.com/clair) on a standalone instance.

## Requirements

A Linux Distribution which supports `systemd` and `package` modules along with docker install and configured.

## Role Variables

This role contains a number of variables to customize the deployment of Clair. The following are some of the most important that may need to be configured

| Name | Description | Default|
|---|---|---|
|clair_image|Clair image|`quay.io/coreos/clair-jwt:v2.0.4`|
|clair_config_dir|Directory for Clair configurations| `/var/lib/clair/config`| 
|clair_host_proxy_port|Port to the clair proxy on the host |`6060`|
|clair_host_api_port|Port to the clair API on the host |`6061`|
|quay_enterprise_address|Address of the Quay Enterprise instance| |
|clair_ssl_trust_configure|Configure SSL trust|`False`|
|clair_ssl_trust_src_file|Location of the SSL certificates to populate Clair TLS trust when enabled|`/tmp/clair-ssl-trust.crt`|


## Dependencies

* [container-storage-setup](../container-storage-setup)
* [config-docker](../config-docker)


## Example Playbook

```
- name: Install Clair
  hosts: clair
  roles:
    - role: config-clair
```

## License

Apache License 2.0

## Author Information

Red Hat Community of Practice & staff of the Red Hat Open Innovation Labs.