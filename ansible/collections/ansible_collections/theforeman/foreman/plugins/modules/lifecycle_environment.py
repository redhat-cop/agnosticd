#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Andrew Kofink <ajkofink@gmail.com>
# (c) 2019, Baptiste Agasse <baptiste.agasse@gmail.com>
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
module: lifecycle_environment
version_added: 1.0.0
short_description: Manage Lifecycle Environments
description:
    - Create and manage lifecycle environments
author:
  - "Andrew Kofink (@akofink)"
  - "Baptiste Agasse (@bagasse)"
options:
  name:
    description:
      - Name of the lifecycle environment
    required: true
    type: str
  label:
    description:
      - Label of the lifecycle environment. This field cannot be updated.
    type: str
  description:
    description:
      - Description of the lifecycle environment
    type: str
  prior:
    description:
      - Name of the parent lifecycle environment
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Add a production lifecycle environment"
  theforeman.foreman.lifecycle_environment:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Production"
    label: "production"
    organization: "Default Organization"
    prior: "Library"
    description: "The production environment"
    state: "present"
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    lifecycle_environments:
      description: List of lifecycle environments.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


class KatelloLifecycleEnvironmentModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloLifecycleEnvironmentModule(
        foreman_spec=dict(
            name=dict(required=True),
            label=dict(),
            description=dict(),
            prior=dict(type='entity', resource_type='lifecycle_environments', scope=['organization']),
        ),
    )

    with module.api_connection():
        entity = module.lookup_entity('entity')

        # Default to 'Library' for new env with no 'prior' provided
        if 'prior' not in module.foreman_params and not entity:
            module.foreman_params['prior'] = 'Library'

        if entity and not module.desired_absent:
            if 'label' in module.foreman_params and entity['label'] != module.foreman_params['label']:
                module.fail_json(msg="Label cannot be updated on a lifecycle environment.")

            if 'prior' in module.foreman_params and entity['prior']['id'] != module.lookup_entity('prior')['id']:
                module.fail_json(msg="Prior cannot be updated on a lifecycle environment.")

        module.run()


if __name__ == '__main__':
    main()
