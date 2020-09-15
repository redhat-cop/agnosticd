#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Matthias M Dellweg (ATIX AG)
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
module: setting
version_added: 1.0.0
short_description: Manage Settings
description:
  - Manage Settings
author:
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
options:
  name:
    description:
      - Name of the Setting
    required: true
    type: str
  value:
    description:
      - value to set the Setting to
      - if missing, reset to default
    required: false
    type: raw
extends_documentation_fragment:
  - theforeman.foreman.foreman
'''

EXAMPLES = '''
- name: "Set a Setting"
  theforeman.foreman.setting:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "http_proxy"
    value: "http://localhost:8088"

- name: "Reset a Setting"
  theforeman.foreman.setting:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "http_proxy"
'''

RETURN = '''
foreman_setting:
  description: Created / Updated state of the setting
  returned: success
  type: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanStatelessEntityAnsibleModule, parameter_value_to_str


class ForemanSettingModule(ForemanStatelessEntityAnsibleModule):
    pass


def main():
    module = ForemanSettingModule(
        foreman_spec=dict(
            name=dict(required=True),
            value=dict(type='raw'),
        ),
    )

    with module.api_connection():
        entity = module.lookup_entity('entity')

        if 'value' not in module.foreman_params:
            module.foreman_params['value'] = entity['default'] or ''

        settings_type = entity['settings_type']
        new_value = module.foreman_params['value']
        # Allow to pass integers as string
        if settings_type == 'integer':
            new_value = int(new_value)
        module.foreman_params['value'] = parameter_value_to_str(new_value, settings_type)
        old_value = entity['value']
        entity['value'] = parameter_value_to_str(old_value, settings_type)

        entity = module.ensure_entity('settings', module.foreman_params, entity, state='present')

        if entity:
            # Fake the not serialized input value as output
            entity['value'] = new_value

        module.exit_json(foreman_setting=entity)


if __name__ == '__main__':
    main()
