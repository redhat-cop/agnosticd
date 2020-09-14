#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Baptiste AGASSE (baptiste.agasse@gmail.com)
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
module: usergroup
version_added: 1.0.0
short_description: Manage User Groups
description:
  - Create, update, and delete user groups
author:
  - "Baptiste Agasse (@bagasse)"
options:
  name:
    description:
      - Name of the group
    required: true
    type: str
  updated_name:
    description:
      - New user group name. When this parameter is set, the module will not be idempotent.
    required: false
    type: str
  admin:
    description:
      - Whether or not the users in this group are administrators
    required: false
    default: false
    type: bool
  roles:
    description:
      - List of roles assigned to the group
    required: false
    type: list
    elements: str
  users:
    description:
      - List of users assigned to the group
    required: false
    type: list
    elements: str
  usergroups:
    description:
      - List of other groups assigned to the group
    required: false
    type: list
    elements: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
'''

EXAMPLES = '''
- name: Create a user group
  theforeman.foreman.usergroup:
    name: test
    admin: no
    roles:
      - Manager
    users:
      - myuser1
      - myuser2
    usergroups:
      - mynestedgroup
    state: present
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    usergroups:
      description: List of usergroups.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule


class ForemanUsergroupModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanUsergroupModule(
        argument_spec=dict(
            updated_name=dict(),
        ),
        foreman_spec=dict(
            name=dict(required=True),
            admin=dict(required=False, type='bool', default=False),
            users=dict(required=False, type='entity_list'),
            usergroups=dict(required=False, type='entity_list'),
            roles=dict(required=False, type='entity_list'),
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
