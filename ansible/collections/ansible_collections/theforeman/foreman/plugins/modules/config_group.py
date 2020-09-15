#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Baptiste Agasse
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
module: config_group
version_added: 1.0.0
short_description: Manage (Puppet) Config Groups
description:
  - Create, update, and delete (Puppet) config groups
author:
  - "Baptiste Agasse (@bagasse)"
options:
  name:
    description: The config group name
    required: true
    type: str
  updated_name:
    description: New config group name. When this parameter is set, the module will not be idempotent.
    type: str
  puppetclasses:
    description: List of puppet classes to include in this group
    required: false
    type: list
    elements: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
'''

EXAMPLES = '''
- name: create new config group
  theforeman.foreman.config_group:
    name: "My config group"
    puppetclasses:
      - ntp
      - mymodule::myclass
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
    config_groups:
      description: List of config groups.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule


class ForemanConfigGroupModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanConfigGroupModule(
        argument_spec=dict(
            updated_name=dict(),
        ),
        foreman_spec=dict(
            name=dict(required=True),
            puppetclasses=dict(type='entity_list'),
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
