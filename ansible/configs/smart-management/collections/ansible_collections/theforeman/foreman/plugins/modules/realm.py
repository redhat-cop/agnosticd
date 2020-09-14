#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Lester R Claudio <claudiol@redhat.com>
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
module: realm
version_added: 1.0.0
short_description: Manage Realms
description:
  - Manage Realms
author:
  - "Lester R Claudio (@claudiol1)"
options:
  name:
    description:
      - Name of the realm
    required: true
    type: str
  realm_proxy:
    description:
      - Proxy to use for this realm
    required: true
    type: str
  realm_type:
    description:
      - Realm type
    choices:
      - Red Hat Identity Management
      - FreeIPA
      - Active Directory
    required: true
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
- name: "Create EXAMPLE.LOCAL Realm"
  theforeman.foreman.realm:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "EXAMPLE.COM"
    realm_proxy: "foreman.example.com"
    realm_type: "Red Hat Identity Management"
    state: present
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    realms:
      description: List of realms.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule


class ForemanRealmModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanRealmModule(
        foreman_spec=dict(
            name=dict(required=True),
            realm_proxy=dict(type='entity', required=True, resource_type='smart_proxies'),
            realm_type=dict(required=True, choices=['Red Hat Identity Management', 'FreeIPA', 'Active Directory']),
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
