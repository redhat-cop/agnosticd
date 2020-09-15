#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017 Matthias M Dellweg (ATIX AG)
# (c) 2017 Bernhard Hopfenmüller (ATIX AG)
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
module: operatingsystem
version_added: 1.0.0
short_description: Manage Operating Systems
description:
  - Manage Operating Systems
author:
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
  - "Bernhard Hopfenmüller (@Fobhep) ATIX AG"
options:
  name:
    description:
      - Name of the Operating System
    required: true
    type: str
  updated_name:
    description: New operating system name. When this parameter is set, the module will not be idempotent.
    type: str
  release_name:
    description:
      - Release name of the operating system (recommended for debian)
    type: str
  description:
    description:
      - Description of the Operating System
    required: false
    type: str
  os_family:
    description:
      - Distribution family of the Operating System
    aliases:
      - family
  major:
    description:
      - major version of the Operating System
    required: false
    type: str
  minor:
    description:
      - minor version of the Operating System
    required: false
    type: str
  architectures:
    description:
      - architectures, the operating system can be installed on
    required: false
    type: list
    elements: str
  media:
    description:
      - list of installation media
    required: false
    type: list
    elements: str
  ptables:
    description:
      - list of partitioning tables
    required: false
    type: list
    elements: str
  provisioning_templates:
    description:
      - List of provisioning templates that are associated with the operating system.
      - Specify the full list of template names you want to associate with your OS.
      - For example ["Kickstart default", "Kickstart default finish", "Kickstart default iPXE", "custom"].
      - After specifying the template associations, you can set the default association in
      - the M(theforeman.foreman.os_default_template) module.
    required: false
    type: list
    elements: str
  password_hash:
    description:
      - hashing algorithm for passwd
    required: false
    choices:
      - MD5
      - SHA256
      - SHA512
      - Base64
      - Base64-Windows
    type: str
  parameters:
    description:
      - Operating System specific host parameters
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.nested_parameters
  - theforeman.foreman.foreman.os_family
'''

EXAMPLES = '''
- name: "Create an Operating System"
  theforeman.foreman.operatingsystem:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: Debian
    release_name: stretch
    family: Debian
    major: 9
    parameters:
      - name: additional-packages
        value: python vim
    state: present

- name: "Ensure existence of an Operating System (provide default values)"
  theforeman.foreman.operatingsystem:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: Centos
    family: Redhat
    major: 7
    password_hash: SHA256
    state: present_with_defaults

- name: "Delete an Operating System"
  theforeman.foreman.operatingsystem:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: Debian
    family: Debian
    major: 9
    state: absent
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    operatinsystems:
      description: List of operatinsystems.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanEntityAnsibleModule,
    ParametersMixin,
    OS_LIST,
)


class ForemanOperatingsystemModule(ParametersMixin, ForemanEntityAnsibleModule):
    PARAMETERS_FLAT_NAME = 'os_parameters_attributes'


def main():
    module = ForemanOperatingsystemModule(
        foreman_spec=dict(
            name=dict(required=True),
            release_name=dict(),
            description=dict(),
            os_family=dict(choices=OS_LIST, flat_name='family', aliases=['family']),
            major=dict(),
            minor=dict(),
            architectures=dict(type='entity_list'),
            media=dict(type='entity_list', flat_name='medium_ids', resource_type='media'),
            ptables=dict(type='entity_list'),
            provisioning_templates=dict(type='entity_list'),
            password_hash=dict(choices=['MD5', 'SHA256', 'SHA512', 'Base64', 'Base64-Windows']),
        ),
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'present_with_defaults', 'absent']),
            updated_name=dict(),
        ),
        required_if=[
            ['state', 'present', ['name', 'major', 'os_family']],
            ['state', 'present_with_defaults', ['name', 'major', 'os_family']],
        ],
        required_one_of=[
            ['description', 'name'],
            ['description', 'major'],
        ],
    )

    module_params = module.foreman_params

    with module.api_connection():

        # Try to find the Operating System to work on
        # name is however not unique, but description is, as well as "<name> <major>[.<minor>]"
        entity = None
        # If we have a description, search for it
        if 'description' in module_params and module_params['description'] != '':
            search_string = 'description="{0}"'.format(module_params['description'])
            entity = module.find_resource('operatingsystems', search_string, failsafe=True)
        # If we did not yet find a unique OS, search by name & version
        # In case of state == absent, those information might be missing, we assume that we did not find an operatingsytem to delete then
        if entity is None and 'name' in module_params and 'major' in module_params:
            search_string = ','.join('{0}="{1}"'.format(key, module_params[key]) for key in ('name', 'major', 'minor') if key in module_params)
            entity = module.find_resource('operatingsystems', search_string, failsafe=True)

        if not entity and (module.state == 'present' or module.state == 'present_with_defaults'):
            # we actually attempt to create a new one...
            for param_name in ['major', 'os_family', 'password_hash']:
                if param_name not in module_params.keys():
                    module.fail_json(msg='{0} is a required parameter to create a new operating system.'.format(param_name))

        module.set_entity('entity', entity)
        module.run()


if __name__ == '__main__':
    main()
