#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019, Maxim Burgerhout <maxim@wzzrd.com>
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
module: host_collection
version_added: 1.0.0
short_description: Manage Host Collections
description:
    - Create and Manage host collections
author:
    - "Maxim Burgerhout (@wzzrd)"
    - "Christoffer Reijer (@ephracis)"
options:
  description:
    description:
      - Description of the host collection
    required: false
    type: str
  name:
    description:
      - Name of the host collection
    required: true
    type: str
  updated_name:
    description:
      - New name of the host collection. When this parameter is set, the module will not be idempotent.
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Create Foo host collection"
  theforeman.foreman.host_collection:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Foo"
    description: "Foo host collection for Foo servers"
    organization: "My Cool new Organization"
    state: present
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    host_collections:
      description: List of host collections.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


class KatelloHostCollectionModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloHostCollectionModule(
        argument_spec=dict(
            updated_name=dict(),
        ),
        foreman_spec=dict(
            name=dict(required=True),
            description=dict(),
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
