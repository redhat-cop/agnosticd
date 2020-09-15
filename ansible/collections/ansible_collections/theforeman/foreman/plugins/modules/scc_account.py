#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Manisha Singhal (ATIX AG)
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
module: scc_account
version_added: 1.0.0
short_description: Manage SUSE Customer Center Accounts
description:
  - Manage SUSE Customer Center Accounts
  - This module requires the foreman_scc_manager plugin set up in the server
  - See U(https://github.com/ATIX-AG/foreman_scc_manager)
author:
  - "Manisha Singhal (@manisha15) ATIX AG"
options:
  name:
    description: Name of the suse customer center account
    required: true
    type: str
  login:
    description: Login id of suse customer center account
    required: false
    type: str
  scc_account_password:
    description: Password of suse customer center account
    required: false
    type: str
  base_url:
    description: URL of SUSE for suse customer center account
    required: false
    type: str
  interval:
    description: Interval for syncing suse customer center account
    required: false
    type: str
    choices: ["never", "daily", "weekly", "monthly"]
  sync_date:
    description: Last Sync time of suse customer center account
    required: false
    type: str
  organization:
    description: Name of related organization
    type: str
    required: true
  test_connection:
    description: Test suse customer center account credentials that connects to the server
    required: false
    default: false
    type: bool
  updated_name:
    description: Name to be updated of suse customer center account
    type: str
  state:
    description: State of the suse customer center account
    default: present
    choices: ["present", "absent", "synced"]
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Create a suse customer center account"
  theforeman.foreman.scc_account:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Test"
    login: "abcde"
    scc_account_password: "12345"
    base_url: "https://scc.suse.com"
    state: present

- name: "Update a suse customer center account"
  theforeman.foreman.scc_account:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Test1"
    state: present

- name: "Delete a suse customer center account"
  theforeman.foreman.scc_account:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Test"
    state: absent
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    scc_accounts:
      description: List of scc accounts.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


class KatelloSccAccountModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloSccAccountModule(
        foreman_spec=dict(
            name=dict(required=True),
            updated_name=dict(),
            login=dict(),
            scc_account_password=dict(no_log=True, flat_name='password'),
            base_url=dict(),
            sync_date=dict(),
            interval=dict(choices=['never', 'daily', 'weekly', 'monthly']),
        ),
        argument_spec=dict(
            test_connection=dict(type='bool', default=False),
            state=dict(default='present', choices=['present', 'absent', 'synced']),
        ),
        required_plugins=[('scc_manager', ['*'])],
    )

    module.task_timeout = 4 * 60

    with module.api_connection():
        module.foreman_spec['entity']['failsafe'] = (module.state != 'synced')
        entity = module.lookup_entity('entity')

        if not module.desired_absent:
            if not entity:
                if 'login' not in module.foreman_params:
                    module.fail_json(msg="scc account login not provided")
                if 'scc_account_password' not in module.foreman_params:
                    module.fail_json(msg="Scc account password not provided")

            if module.foreman_params['test_connection']:
                scc_account_credentials = {}
                if entity:
                    scc_account_credentials['id'] = entity['id']
                if 'login' in module.foreman_params:
                    scc_account_credentials['login'] = module.foreman_params['login']
                if 'scc_account_password' in module.foreman_params:
                    scc_account_credentials['password'] = module.foreman_params['scc_account_password']
                if 'base_url' in module.foreman_params:
                    scc_account_credentials['base_url'] = module.foreman_params['base_url']
                module.resource_action('scc_accounts', 'test_connection', scc_account_credentials, ignore_check_mode=True)

        if module.state == 'synced':
            module.resource_action('scc_accounts', 'sync', {'id': entity['id']})
        else:
            module.run()


if __name__ == '__main__':
    main()
