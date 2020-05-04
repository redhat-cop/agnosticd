# set-repositories

Configure YUM/DNF repositories.

## Requirements

FIXME

## Role Variables

`repo_method` - Repository configuration method. May be set to `file`, `rhn`, or `satellite`.

`use_content_view` - FIXME

### Repo Method satellite Variables

`set_repositories_satellite_hostname` -
Hostname of satellite server.
Required, but may be set as `set_repositories_satellite_url` or `satellite_url` for compatibility with previous versions.

`set_repositories_satellite_ca_cert` -
CA certificate used to validate satellite server TLS.
Required unless `set_repositories_satellite_hostname` is `labsat.opentlc.com`.

`set_repositories_satellite_ca_rpm_url` -
URL used to download the Katello/Satellite CA certificate configuration RPM.
Default `https://{{ set_repositories_satellite_hostname }}/pub/katello-ca-consumer-latest.noarch.rpm`

`set_repositories_satellite_activationkey` -
Activation key to register to satellite. Optional, but may be set with `satellite_activationkey` for compatibility with previous versions.

## Dependencies

FIXME

## Example Playbook

FIXME

License
-------

BSD

Author Information
------------------

Red Hat, GPTE
