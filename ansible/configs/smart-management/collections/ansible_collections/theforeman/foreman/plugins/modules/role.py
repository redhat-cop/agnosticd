#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Christoffer Reijer (Basalt AB)
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
module: role
version_added: 1.0.0
short_description: Manage Roles
description:
  - Create, update, and delete Roles
author:
  - "Christoffer Reijer (@ephracis) Basalt AB"
options:
  name:
    description: The name of the role
    required: true
    type: str
  description:
    description: Description of the role
    required: false
    type: str
  filters:
    description: Filters with permissions for this role
    required: false
    type: list
    elements: dict
    suboptions:
      permissions:
        description: List of permissions
        required: true
        type: list
        elements: str
      search:
        description: Filter condition for the resources
        required: false
        type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
- name: role
  theforeman.foreman.role:
    name: "Provisioner"
    description: "Only provision on libvirt"
    locations:
      - "Uppsala"
    organizations:
      - "ACME"
    filters:
      - permissions:
          - view_hosts
        search: "owner_type = Usergroup and owner_id = 4"
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
    roles:
      description: List of roles.
      type: list
      elements: dict
'''

import copy

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule


filter_foreman_spec = dict(
    permissions=dict(type='entity_list', required=True),
    search=dict(),
)


class ForemanRoleModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanRoleModule(
        foreman_spec=dict(
            name=dict(required=True),
            description=dict(),
            filters=dict(type='nested_list', foreman_spec=filter_foreman_spec),
        ),
    )

    with module.api_connection():
        entity = module.lookup_entity('entity')
        new_entity = module.run()

        filters = module.foreman_params.get("filters")
        if not module.desired_absent and filters is not None:
            scope = {'role_id': new_entity['id']}

            if entity:
                current_filters = [module.show_resource('filters', filter['id']) for filter in entity['filters']]
            else:
                current_filters = []
            desired_filters = copy.deepcopy(filters)

            for desired_filter in desired_filters:
                # search for an existing filter
                for current_filter in current_filters:
                    if desired_filter['search'] == current_filter['search']:
                        if set(desired_filter['permissions']) == set(perm['name'] for perm in current_filter['permissions']):
                            current_filters.remove(current_filter)
                            break
                else:
                    desired_filter['permissions'] = module.find_resources_by_name('permissions', desired_filter['permissions'], thin=True)
                    module.ensure_entity('filters', desired_filter, None, params=scope, state='present', foreman_spec=filter_foreman_spec)
            for current_filter in current_filters:
                module.ensure_entity('filters', None, {'id': current_filter['id']}, params=scope, state='absent', foreman_spec=filter_foreman_spec)


if __name__ == '__main__':
    main()
