#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Bernhard Hopfenmüller (ATIX AG)
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
module: host_power
version_added: 1.0.0
short_description: Manage Power State of Hosts
description:
  - "Manage power state of a host"
  - "This beta version can start and stop an existing foreman host and question the current power state."
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
  - "Baptiste Agasse (@bagasse)"
options:
  name:
    description: Name (FQDN) of the host
    required: true
    aliases:
      - hostname
    type: str
  state:
    description: Desired power state
    default: state
    choices:
      - 'on'
      - 'start'
      - 'off'
      - 'stop'
      - 'soft'
      - 'reboot'
      - 'cycle'
      - 'reset'
      - 'state'
      - 'status'
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
'''

EXAMPLES = '''
- name: "Switch a host on"
  theforeman.foreman.host_power:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    hostname: "test-host.domain.test"
    state: on

- name: "Switch a host off"
  theforeman.foreman.host_power:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    hostname: "test-host.domain.test"
    state: off

- name: "Query host power state"
  theforeman.foreman.host_power:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    hostname: "test-host.domain.test"
    state: state
    register: result
- debug:
    msg: "Host power state is {{ result.power_state }}"


'''

RETURN = '''
power_state:
    description: current power state of host
    returned: always
    type: str
    sample: "off"
 '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule


def main():
    module = ForemanEntityAnsibleModule(
        foreman_spec=dict(
            name=dict(aliases=['hostname'], required=True),
        ),
        argument_spec=dict(
            state=dict(default='state', choices=['on', 'start', 'off', 'stop', 'soft', 'reboot', 'cycle', 'reset', 'state', 'status']),
        )
    )

    module_params = module.foreman_params

    with module.api_connection():
        # power_status endpoint was only added in foreman 1.22.0 per https://projects.theforeman.org/issues/25436
        # Delete this piece when versions below 1.22 are off common use
        # begin delete
        if 'power_status' not in module.foremanapi.resource('hosts').actions:
            params = {'id': module_params['name'], 'power_action': 'status'}
            power_state = module.resource_action('hosts', 'power', params=params, ignore_check_mode=True)
            power_state['state'] = 'on' if power_state['power'] == 'running' else 'off'
        else:
            # end delete (on delete un-indent the below two lines)
            params = {'id': module_params['name']}
            power_state = module.resource_action('hosts', 'power_status', params=params, ignore_check_mode=True)

        if module.state in ['state', 'status']:
            module.exit_json(power_state=power_state['state'])
        elif ((module.state in ['on', 'start'] and power_state['state'] == 'on')
              or (module.state in ['off', 'stop'] and power_state['state'] == 'off')):
            module.exit_json()
        else:
            params['power_action'] = module.state
            module.resource_action('hosts', 'power', params=params)


if __name__ == '__main__':
    main()
