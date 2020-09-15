#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Manisha Singhal (ATIX AG)
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
module: hostgroup
version_added: 1.0.0
short_description: Manage Hostgroups
description:
  - Create, update, and delete Hostgroups
author:
  - "Manisha Singhal (@Manisha15) ATIX AG"
  - "Baptiste Agasse (@bagasse)"
options:
  name:
    description: Name of hostgroup
    required: true
    type: str
  updated_name:
    description: New name of hostgroup. When this parameter is set, the module will not be idempotent.
    type: str
  description:
    description: Description of hostgroup
    required: false
    type: str
  parent:
    description: Hostgroup parent name
    required: false
    type: str
  organization:
    description:
      - Organization for scoped resources attached to the hostgroup.
      - Only used for Katello installations.
      - This organization will implicitly be added to the I(organizations) parameter if needed.
    required: false
    type: str
  parameters:
    description:
      - Hostgroup specific host parameters
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
  - theforeman.foreman.foreman.nested_parameters
  - theforeman.foreman.foreman.host_options
'''

EXAMPLES = '''
- name: "Create a Hostgroup"
  theforeman.foreman.hostgroup:
    name: "new_hostgroup"
    architecture: "architecture_name"
    operatingsystem: "operatingsystem_name"
    medium: "media_name"
    ptable: "Partition_table_name"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: "Update a Hostgroup"
  theforeman.foreman.hostgroup:
    name: "new_hostgroup"
    architecture: "updated_architecture_name"
    operatingsystem: "updated_operatingsystem_name"
    organizations:
      - Org One
      - Org Two
    locations:
      - Loc One
      - Loc Two
      - Loc One/Nested loc
    medium: "updated_media_name"
    ptable: "updated_Partition_table_name"
    root_pass: "password"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: "My nested hostgroup"
  theforeman.foreman.hostgroup:
    parent: "new_hostgroup"
    name: "my nested hostgroup"

- name: "My hostgroup with some proxies"
  theforeman.foreman.hostgroup:
    name: "my hostgroup"
    environment: production
    puppet_proxy: puppet-proxy.example.com
    puppet_ca_proxy: puppet-proxy.example.com
    openscap_proxy: openscap-proxy.example.com

- name: "My katello related hostgroup"
  theforeman.foreman.hostgroup:
    organization: "My Org"
    name: "kt hostgroup"
    content_source: capsule.example.com
    lifecycle_environment: "Production"
    content_view: "My content view"
    parameters:
      - name: "kt_activation_keys"
        value: "my_prod_ak"

- name: "Delete a Hostgroup"
  theforeman.foreman.hostgroup:
    name: "new_hostgroup"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: absent
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    hostgroups:
      description: List of hostgroups.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ensure_puppetclasses,
    HostMixin,
    ForemanTaxonomicEntityAnsibleModule,
)


class ForemanHostgroupModule(HostMixin, ForemanTaxonomicEntityAnsibleModule):
    PARAMETERS_FLAT_NAME = 'group_parameters_attributes'


def main():
    module = ForemanHostgroupModule(
        foreman_spec=dict(
            name=dict(required=True),
            description=dict(),
            parent=dict(type='entity'),
            organization=dict(type='entity', required=False, ensure=False),
        ),
        argument_spec=dict(
            updated_name=dict(),
        ),
        required_by=dict(
            content_source=('organization',),
            content_view=('organization',),
            lifecycle_environment=('organization',),
        ),
    )

    module_params = module.foreman_params
    with module.api_connection():
        if not module.desired_absent:
            if 'organization' in module_params:
                if 'organizations' in module_params:
                    if module_params['organization'] not in module_params['organizations']:
                        module_params['organizations'].append(module_params['organization'])
                else:
                    module_params['organizations'] = [module_params['organization']]
        expected_puppetclasses = module_params.pop('puppetclasses', None)
        entity = module.run()
        if not module.desired_absent and 'environment_id' in entity:
            ensure_puppetclasses(module, 'hostgroup', entity, expected_puppetclasses)


if __name__ == '__main__':
    main()
