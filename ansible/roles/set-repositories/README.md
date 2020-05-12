# set-repositories

Configure YUM/DNF repositories.

## Requirements

FIXME

## Role Variables

`repo_method` - Repository configuration method. May be set to `file`, `rhn`, or `satellite`.

`use_content_view` - FIXME

### Repo Method 'rhn' Variables

**IMPORTANT:** When using `repo_method: rhn` only define the variables of one of the below options.

**Option 1:** Register with credentials
This option registers a system with Red Hat credentials and a pool id.
If using this method define these variables in a secrets file.

`rhel_subscription_user` (Required)
User name of the Red Hat account that will register the system.
This is the same user name used to log into access.redhat.com

`rhel_subscription_pass` (Required)
The password for the user name referenced in `rhel_subscription_user`.

`rhsm_pool_ids` (Required)
The pool id for the subscription to attach. By default `auto_attach` is false.

**Option 2:** Register with an activation key.
These variables will register a system with an activation key.

`rhel_subscription_activation_key` (Required)
The unique activation key created within an account at access.redhat.com

`rhel_subscription_org_id` (Required)
The organization ID of the the account which created the activation key.

`rhsm_pool_ids` (Required)
The pool id for the subscription to attach. By default `auto_attach` is false.

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
