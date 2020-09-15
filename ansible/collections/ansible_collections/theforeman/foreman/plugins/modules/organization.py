#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2016, Eric D Helms <ericdhelms@gmail.com>
# (c) 2017, Matthias M Dellweg <dellweg@atix.de> (ATIX AG)
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
module: organization
version_added: 1.0.0
short_description: Manage Organizations
description:
    - Manage Organizations
author:
    - "Eric D Helms (@ehelms)"
    - "Matthias M Dellweg (@mdellweg) ATIX AG"
options:
  name:
    description:
      - Name of the Organization
    required: true
    type: str
  description:
    description:
      - Description of the Organization
    required: false
    type: str
  label:
    description:
      - Label of the Organization
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.nested_parameters
'''

EXAMPLES = '''
- name: "Create CI Organization"
  theforeman.foreman.organization:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Cool New Organization"
    state: present
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    organizations:
      description: List of organizations.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule, NestedParametersMixin


class ForemanOrganizationModule(NestedParametersMixin, ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanOrganizationModule(
        foreman_spec=dict(
            name=dict(required=True),
            description=dict(),
            label=dict(),
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
