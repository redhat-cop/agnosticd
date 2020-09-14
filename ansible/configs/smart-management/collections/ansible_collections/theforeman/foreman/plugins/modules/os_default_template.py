#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017 Matthias M Dellweg (ATIX AG)
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
module: os_default_template
version_added: 1.0.0
short_description: Manage Default Template Associations To Operating Systems
description:
  - Manage OSDefaultTemplate Entities
author:
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
options:
  operatingsystem:
    description:
      - Title of the Operating System (name, or name and major version, that uniquely identifies the OS)
    required: true
    type: str
  template_kind:
    description:
      - name of the template kind
    required: true
    type: str
  provisioning_template:
    description:
      - name of provisioning template
    required: false
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
'''

EXAMPLES = '''
- name: "Create an Association"
  theforeman.foreman.os_default_template:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    operatingsystem: "CoolOS"
    template_kind: "finish"
    provisioning_template: "CoolOS finish"
    state: present

- name: "Delete an Association"
  theforeman.foreman.os_default_template:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    operatingsystem: "CoolOS"
    template_kind: "finish"
    state: absent
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    os_default_templates:
      description: List of operatingsystem default templates.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule


class ForemanOsDefaultTemplateModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanOsDefaultTemplateModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'present_with_defaults', 'absent']),
        ),
        foreman_spec=dict(
            operatingsystem=dict(required=True, type='entity'),
            template_kind=dict(required=True, type='entity'),
            provisioning_template=dict(type='entity', thin=False),
        ),
        required_if=(
            ['state', 'present', ['provisioning_template']],
            ['state', 'present_with_defaults', ['provisioning_template']],
        ),
        entity_opts={'scope': ['operatingsystem']},
    )

    if 'provisioning_template' in module.foreman_params and module.desired_absent:
        module.fail_json(msg='Provisioning template must not be specified for deletion.')

    with module.api_connection():
        template_kind_id = module.lookup_entity('template_kind')['id']
        if not module.desired_absent:
            if module.lookup_entity('provisioning_template')['template_kind_id'] != template_kind_id:
                module.fail_json(msg='Provisioning template kind mismatching.')

        scope = module.scope_for('operatingsystem')
        # Default templates do not support a scoped search
        # see: https://projects.theforeman.org/issues/27722
        entities = module.list_resource('os_default_templates', params=scope)
        entity = next((item for item in entities if item['template_kind_id'] == template_kind_id), None)
        module.set_entity('entity', entity)

        module.run()


if __name__ == '__main__':
    main()
