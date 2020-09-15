#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2016, Eric D Helms <ericdhelms@gmail.com>
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
module: product
version_added: 1.0.0
short_description: Manage Products
description:
  - Create and manage products
author:
  - "Eric D Helms (@ehelms)"
  - "Matthias Dellweg (@mdellweg) ATIX AG"
options:
  name:
    description:
      - Name of the product
    required: true
    type: str
  label:
    description:
      - Label to show the user
    required: false
    type: str
  gpg_key:
    description:
    - Content GPG key name attached to this product
    required: false
    type: str
  ssl_ca_cert:
    description:
    - Content SSL CA certificate name attached to this product
    required: false
    type: str
  ssl_client_cert:
    description:
    - Content SSL client certificate name attached to this product
    required: false
    type: str
  ssl_client_key:
    description:
    - Content SSL client private key name attached to this product
    required: false
    type: str
  sync_plan:
    description:
      - Sync plan name attached to this product
    required: false
    type: str
  description:
    description:
      - Possibly long descriptionto show the user in detail view
    required: false
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Create Fedora product with a sync plan"
  theforeman.foreman.product:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Fedora"
    organization: "My Cool new Organization"
    sync_plan: "Fedora repos sync"
    state: present

- name: "Create CentOS 7 product with content credentials"
  theforeman.foreman.product:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "CentOS 7"
    gpg_key: "RPM-GPG-KEY-CentOS7"
    organization: "My Cool new Organization"
    state: present
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    products:
      description: List of products.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


class KatelloProductModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloProductModule(
        entity_name='product',
        foreman_spec=dict(
            name=dict(required=True),
            label=dict(),
            gpg_key=dict(type='entity', resource_type='content_credentials', scope=['organization']),
            ssl_ca_cert=dict(type='entity', resource_type='content_credentials', scope=['organization']),
            ssl_client_cert=dict(type='entity', resource_type='content_credentials', scope=['organization']),
            ssl_client_key=dict(type='entity', resource_type='content_credentials', scope=['organization']),
            sync_plan=dict(type='entity', scope=['organization']),
            description=dict(),
        ),
        argument_spec=dict(
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
