#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017 Matthias Dellweg & Bernhard Hopfenmüller (ATIX AG)
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
module: global_parameter
version_added: 1.0.0
short_description: Manage Global Parameters
description:
  - "Manage Global Parameter Entities"
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
  - "Matthias Dellweg (@mdellweg) ATIX AG"
  - "Manisha Singhal (@manisha15) ATIX AG"
options:
  name:
    description:
      - Name of the Global Parameter
    required: true
    type: str
  updated_name:
    description:
      - New name of the Global Parameter. When this parameter is set, the module will not be idempotent.
    type: str
  value:
    description:
      - Value of the Global Parameter
    required: false
    type: raw
  parameter_type:
    description:
      - Type of value
    default: string
    choices:
      - string
      - boolean
      - integer
      - real
      - array
      - hash
      - yaml
      - json
    type: str
notes:
  - The I(parameter_type) only has an effect on Foreman >= 1.22
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
'''

EXAMPLES = '''
- name: "Create a Global Parameter"
  theforeman.foreman.global_parameter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "TheAnswer"
    value: "42"
    state: present_with_defaults

- name: "Update a Global Parameter"
  theforeman.foreman.global_parameter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "TheAnswer"
    value: "43"
    state: present

- name: "Delete a Global Parameter"
  theforeman.foreman.global_parameter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "TheAnswer"
    state: absent
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    global_parameters:
      description: List of global parameters.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule, parameter_value_to_str


class ForemanCommonParameterModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanCommonParameterModule(
        foreman_spec=dict(
            name=dict(required=True),
            value=dict(type='raw'),
            parameter_type=dict(default='string', choices=['string', 'boolean', 'integer', 'real', 'array', 'hash', 'yaml', 'json']),
        ),
        argument_spec=dict(
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
            updated_name=dict(),
        ),
        required_if=(
            ['state', 'present_with_defaults', ['value']],
            ['state', 'present', ['value']],
        ),
    )

    with module.api_connection():
        entity = module.lookup_entity('entity')

        if not module.desired_absent:
            # Convert values according to their corresponding parameter_type
            if entity and 'parameter_type' not in entity:
                entity['parameter_type'] = 'string'
            module.foreman_params['value'] = parameter_value_to_str(module.foreman_params['value'], module.foreman_params['parameter_type'])
            if entity and 'value' in entity:
                entity['value'] = parameter_value_to_str(entity['value'], entity.get('parameter_type', 'string'))

        module.run()


if __name__ == '__main__':
    main()
