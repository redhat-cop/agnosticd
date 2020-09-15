#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018, Baptiste Agasse <baptiste.agagsse@gmail.com>
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
module: content_credential
version_added: 1.0.0
short_description: Manage Content Credentials
description:
  - Create and manage content credentials
author: "Baptiste Agasse (@bagasse)"
options:
  name:
    description:
      - Name of the content credential
    required: true
    type: str
  content_type:
    description:
    - Type of credential
    choices:
    - gpg_key
    - cert
    required: true
    type: str
  content:
    description:
    - Content of the content credential
    required: true
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Create katello client GPG key"
  theforeman.foreman.content_credential:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "RPM-GPG-KEY-my-repo"
    content_type: gpg_key
    organization: "Default Organization"
    content: "{{ lookup('file', 'RPM-GPG-KEY-my-repo') }}"
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    content_credentials:
      description: List of content credentials.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


class KatelloContentCredentialModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloContentCredentialModule(
        foreman_spec=dict(
            name=dict(required=True),
            content_type=dict(required=True, choices=['gpg_key', 'cert']),
            content=dict(required=True),
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
