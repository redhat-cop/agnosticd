# Redis

Ansible Role to help configure [Redis](https://redis.io/) on a standalone instance.

## Requirements

A Linux Distribution which supports `systemd` along with docker install and configured

## Role Variables

This role contains a number of variables to customize the deployment of Redis. The following are some of the most important that may need to be configured

| Name | Description | Default|
|---|---|---|
|redis_image|Redis image|`quay.io/quay/redis:latest`|
|redis_storage_dir|Directory to persistently storage data from the Redis container|`/var/lib/redis`|
|redis_host_port|Port to expose on the host |`6379`|

## Dependencies

None

## Example Playbook

```
- name: Install Redis
  hosts: redis
  roles:
    - role: config-redis
```

## License

Apache License 2.0

## Author Information

Red Hat Community of Practice & staff of the Red Hat Open Innovation Labs.