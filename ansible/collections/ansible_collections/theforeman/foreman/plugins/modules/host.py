#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Bernhard Hopfenmüller (ATIX AG)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: host
version_added: 1.0.0
short_description: Manage Hosts
description:
  - Create, update, and delete Hosts
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
options:
  name:
    description:
      - Fully Qualified Domain Name of host
    required: true
    type: str
  hostgroup:
    description:
      - Name of related hostgroup.
    required: false
    type: str
  location:
    description:
      - Name of related location
    required: false
    type: str
  organization:
    description:
      - Name of related organization
    required: false
    type: str
  build:
    description:
      - Whether or not to setup build context for the host
    type: bool
    required: false
  enabled:
    description:
      - Include this host within reporting
    type: bool
    required: false
  managed:
    description:
      - Whether a host is managed or unmanaged.
      - Forced to true when I(build=true)
    type: bool
    required: false
  ip:
    description:
      - IP address of the primary interface of the host.
    type: str
    required: false
  mac:
    description:
      - MAC address of the primary interface of the host.
      - Please include leading zeros and separate nibbles by colons, otherwise the execution will not be idempotent.
      - Example EE:BB:01:02:03:04
    type: str
    required: false
  comment:
    description:
      - Comment about the host.
    type: str
    required: false
  owner:
    description:
      - Owner (user) of the host.
      - Mutually exclusive with I(owner_group).
    type: str
    required: false
  owner_group:
    description:
      - Owner (user group) of the host.
      - Mutually excluside with I(owner).
    type: str
    required: false
  provision_method:
    description:
      - The method used to provision the host.
      - I(provision_method=bootdisk) is only available if the bootdisk plugin is installed.
    choices:
      - 'build'
      - 'image'
      - 'bootdisk'
    type: str
    required: false
  image:
    description:
      - The image to use when I(provision_method=image).
    type: str
    required: false
  compute_attributes:
    description:
      - Additional compute resource specific attributes.
      - When this parameter is set, the module will not be idempotent.
    type: dict
    required: false
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.host_options
  - theforeman.foreman.foreman.nested_parameters
'''

EXAMPLES = '''
- name: "Create a host"
  theforeman.foreman.host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    hostgroup: my_hostgroup
    state: present

- name: "Create a host with build context"
  theforeman.foreman.host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    hostgroup: my_hostgroup
    build: true
    state: present

- name: "Create an unmanaged host"
  theforeman.foreman.host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    managed: false
    state: present

- name: "Create a VM with 2 CPUs and 4GB RAM"
  theforeman.foreman.host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    compute_attributes:
       cpus: 2
       memory_mb: 4096
    state: present

- name: "Create a VM and start it after creation"
  theforeman.foreman.host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    compute_attributes:
       start: "1"
    state: present

- name: "Delete a host"
  theforeman.foreman.host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    state: absent
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    hosts:
      description: List of hosts.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ensure_puppetclasses,
    ForemanEntityAnsibleModule,
    HostMixin,
)


class ForemanHostModule(HostMixin, ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanHostModule(
        foreman_spec=dict(
            name=dict(required=True),
            hostgroup=dict(type='entity'),
            location=dict(type='entity'),
            organization=dict(type='entity'),
            enabled=dict(type='bool'),
            managed=dict(type='bool'),
            build=dict(type='bool'),
            ip=dict(),
            mac=dict(),
            comment=dict(),
            owner=dict(type='entity', resource_type='users', flat_name='owner_id'),
            owner_group=dict(type='entity', resource_type='usergroups', flat_name='owner_id'),
            owner_type=dict(type='invisible'),
            provision_method=dict(choices=['build', 'image', 'bootdisk']),
            image=dict(type='entity'),
            compute_attributes=dict(type='dict'),
        ),
        mutually_exclusive=[
            ['owner', 'owner_group']
        ],
    )

    # additional param validation
    if '.' not in module.foreman_params['name']:
        module.fail_json(msg="The hostname must be FQDN")

    if not module.desired_absent:
        if 'build' in module.foreman_params and module.foreman_params['build']:
            # When 'build'=True, 'managed' has to be True. Assuming that user's priority is to build.
            if 'managed' in module.foreman_params and not module.foreman_params['managed']:
                module.warn("when 'build'=True, 'managed' is ignored and forced to True")
            module.foreman_params['managed'] = True
        elif 'build' not in module.foreman_params and 'managed' in module.foreman_params and not module.foreman_params['managed']:
            # When 'build' is not given and 'managed'=False, have to clear 'build' context that might exist on the server.
            module.foreman_params['build'] = False

        if 'mac' in module.foreman_params:
            module.foreman_params['mac'] = module.foreman_params['mac'].lower()

        if 'owner' in module.foreman_params:
            module.foreman_params['owner_type'] = 'User'
        elif 'owner_group' in module.foreman_params:
            module.foreman_params['owner_type'] = 'Usergroup'

    with module.api_connection():
        if not module.desired_absent:
            module.auto_lookup_entities()
        expected_puppetclasses = module.foreman_params.pop('puppetclasses', None)
        entity = module.run()
        if not module.desired_absent and 'environment_id' in entity:
            ensure_puppetclasses(module, 'host', entity, expected_puppetclasses)


if __name__ == '__main__':
    main()
