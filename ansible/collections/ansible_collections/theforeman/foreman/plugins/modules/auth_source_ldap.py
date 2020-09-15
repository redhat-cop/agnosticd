#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Christoffer Reijer (Basalt AB)
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
module: auth_source_ldap
version_added: 1.0.0
short_description: Manage LDAP Authentication Sources
description:
  - Create, update, and delete LDAP authentication sources
author:
  - "Christoffer Reijer (@ephracis) Basalt AB"
options:
  name:
    description: The name of the LDAP authentication source
    required: true
    type: str
  host:
    description: The hostname of the LDAP server
    required: true
    type: str
  port:
    description: The port number of the LDAP server
    required: false
    type: int
    default: 389
  account:
    description: Account name to use when accessing the LDAP server.
    required: false
    type: str
  account_password:
    description:
      - Account password to use when accessing the LDAP server.
      - Required when using I(onthefly_register).
      - When this parameter is set, the module will not be idempotent.
    required: false
    type: str
  base_dn:
    description: The base DN to use when searching.
    required: false
    type: str
  attr_login:
    description:
      - Attribute containing login ID.
      - Required when using I(onthefly_register).
    required: false
    type: str
  attr_firstname:
    description:
      - Attribute containing first name.
      - Required when using I(onthefly_register).
    required: false
    type: str
  attr_lastname:
    description:
      - Attribute containing last name.
      - Required when using I(onthefly_register).
    required: false
    type: str
  attr_mail:
    description:
      - Attribute containing email address.
      - Required when using I(onthefly_register).
    required: false
    type: str
  attr_photo:
    description: Attribute containing user photo
    required: false
    type: str
  onthefly_register:
    description: Whether or not to register users on the fly.
    required: false
    type: bool
  usergroup_sync:
    description: Whether or not to sync external user groups on login
    required: false
    type: bool
  tls:
    description: Whether or not to use TLS when contacting the LDAP server.
    required: false
    type: bool
  groups_base:
    description: Base DN where groups reside.
    required: false
    type: str
  use_netgroups:
    description: Whether to use NIS netgroups instead of posix groups, not valid for I(server_type=active_directory)
    required: false
    type: bool
  server_type:
    description: Type of the LDAP server
    required: false
    choices: ["free_ipa", "active_directory", "posix"]
    type: str
  ldap_filter:
    description: Filter to apply to LDAP searches
    required: false
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
- name: LDAP Authentication source
  theforeman.foreman.auth_source_ldap:
    name: "Example LDAP"
    host: "ldap.example.org"
    server_url: "https://foreman.example.com"
    locations:
      - "Uppsala"
    organizations:
      - "Sweden"
    username: "admin"
    password: "secret"
    state: present

- name: LDAP Authentication with automatic registration
  theforeman.foreman.auth_source_ldap:
    name: "Example LDAP"
    host: "ldap.example.org"
    onthefly_register: True
    account: uid=ansible,cn=sysaccounts,cn=etc,dc=example,dc=com
    account_password: secret
    base_dn: dc=example,dc=com
    groups_base: cn=groups,cn=accounts, dc=example,dc=com
    server_type: free_ipa
    attr_login: uid
    attr_firstname: givenName
    attr_lastname: sn
    attr_mail: mail
    attr_photo: jpegPhoto
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
    auth_source_ldaps:
      description: List of auth sources for LDAP.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule


class ForemanAuthSourceLdapModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanAuthSourceLdapModule(
        foreman_spec=dict(
            name=dict(required=True),
            host=dict(required=True),
            port=dict(type='int', default=389),
            account=dict(),
            account_password=dict(no_log=True),
            base_dn=dict(),
            attr_login=dict(),
            attr_firstname=dict(),
            attr_lastname=dict(),
            attr_mail=dict(),
            attr_photo=dict(),
            onthefly_register=dict(type='bool'),
            usergroup_sync=dict(type='bool'),
            tls=dict(type='bool'),
            groups_base=dict(),
            server_type=dict(choices=["free_ipa", "active_directory", "posix"]),
            ldap_filter=dict(),
            use_netgroups=dict(type='bool'),
        ),
        required_if=[['onthefly_register', True, ['attr_login', 'attr_firstname', 'attr_lastname', 'attr_mail']]],
    )

    # additional parameter checks
    if 'use_netgroups' in module.foreman_params and module.foreman_params['server_type'] == 'active_directory':
        module.fail_json(msg='use_netgroups cannot be used when server_type=active_directory')

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
