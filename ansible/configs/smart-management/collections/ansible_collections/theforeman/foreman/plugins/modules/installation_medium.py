#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Manuel Bonk (ATIX AG)
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
module: installation_medium
version_added: 1.0.0
short_description: Manage Installation Media
description:
  - Create, update, and delete Installation Media
author:
  - "Manuel Bonk(@manuelbonk) ATIX AG"
options:
  name:
    description:
      - The full installation medium name.
      - The special name "*" (only possible as parameter) is used to perform bulk actions (modify, delete) on all existing partition tables.
    required: true
    type: str
  updated_name:
    description: New full installation medium name. When this parameter is set, the module will not be idempotent.
    type: str
  operatingsystems:
    description: List of operating systems the installation medium should be assigned to
    required: false
    type: list
    elements: str
  os_family:
    description:
      - The OS family the template shall be assigned with.
      - If no os_family is set but a operatingsystem, the value will be derived from it.
  path:
    description: Path to the installation medium
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.taxonomy
  - theforeman.foreman.foreman.os_family
'''

EXAMPLES = '''
- name: create new debian medium
  theforeman.foreman.installation_medium:
    name: "wheezy"
    locations:
      - "Munich"
    organizations:
      - "ACME"
    operatingsystems:
      - "Debian"
    path: "http://debian.org/mirror/"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    media:
      description: List of installation media.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule, OS_LIST


class ForemanInstallationMediumModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanInstallationMediumModule(
        argument_spec=dict(
            updated_name=dict(),
            state=dict(default='present', choices=['present', 'present_with_defaults', 'absent']),
        ),
        foreman_spec=dict(
            name=dict(required=True),
            operatingsystems=dict(type='entity_list'),
            os_family=dict(choices=OS_LIST),
            path=dict(),
        ),
        entity_opts=dict(
            resource_type='media',
        ),
        entity_name='medium',
    )

    module_params = module.foreman_params
    entity = None

    name = module_params['name']

    affects_multiple = name == '*'
    # sanitize user input, filter unuseful configuration combinations with 'name: *'
    if affects_multiple:
        if module.state == 'present_with_defaults':
            module.fail_json(msg="'state: present_with_defaults' and 'name: *' cannot be used together")
        if module.params['updated_name']:
            module.fail_json(msg="updated_name not allowed if 'name: *'!")
        if module.desired_absent:
            further_params = set(module_params.keys()) - {'name', 'entity'}
            if further_params:
                module.fail_json(msg='When deleting all installation media, there is no need to specify further parameters: %s ' % further_params)

    with module.api_connection():
        if affects_multiple:
            module.set_entity('entity', None)  # prevent lookup
            entities = module.list_resource('media')
            if not entities:
                # Nothing to do shortcut to exit
                module.exit_json()
            if not module.desired_absent:  # not 'thin'
                entities = [module.show_resource('media', entity['id']) for entity in entities]
                module.auto_lookup_entities()
            module_params.pop('name')
            for entity in entities:
                module.ensure_entity('media', module_params, entity)
        else:
            entity = module.lookup_entity('entity')
            if not module.desired_absent and 'operatingsystems' in module_params:
                operatingsystems = module.lookup_entity('operatingsystems')
                if len(operatingsystems) == 1 and 'os_family' not in module_params and entity is None:
                    module_params['os_family'] = module.show_resource('operatingsystems', operatingsystems[0]['id'])['family']

            module.run()


if __name__ == '__main__':
    main()
