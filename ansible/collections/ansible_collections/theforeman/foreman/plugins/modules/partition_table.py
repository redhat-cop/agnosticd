#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017 Matthias Dellweg & Bernhard Hopfenmüller (ATIX AG)
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
module: partition_table
version_added: 1.0.0
short_description: Manage Partition Table Templates
description:
  - Manage Partition Table Templates
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
  - "Matthias Dellweg (@mdellweg) ATIX AG"
options:
  file_name:
    description:
      - The path of a template file, that shall be imported.
      - Either this or I(layout) is required as a source for the Partition Template "content".
    required: false
    type: path
  layout:
    description:
      - The content of the Partitioning Table Template
      - Either this or I(file_name) is required as a source for the Partition Template "content".
    required: false
    type: str
  locked:
    description:
      - Determines whether the template shall be locked
    required: false
    type: bool
  name:
    description:
      - The name of the Partition Table.
      - If omited, will be determined from the C(name) header of the template or the filename (in that order).
      - The special value "*" can be used to perform bulk actions (modify, delete) on all existing Partition Tables.
    required: false
    type: str
  updated_name:
    description: New name of the template. When this parameter is set, the module will not be idempotent.
    required: false
    type: str
  os_family:
    description:
      - The OS family the template shall be assigned with.
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.taxonomy
  - theforeman.foreman.foreman.os_family
'''

EXAMPLES = '''

# Keep in mind, that in this case, the inline parameters will be overwritten
- name: "Create a Partition Table inline"
  theforeman.foreman.partition_table:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: A New Partition Template
    state: present
    layout: |
      <%#
        name: A Partition Template
      %>
        zerombr
        clearpart --all --initlabel
        autopart
    locations:
      - Gallifrey
    organizations:
      - TARDIS INC

- name: "Create a Partition Template from a file"
  theforeman.foreman.partition_table:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    file_name: timeywimey_template.erb
    state: present
    locations:
      - Gallifrey
    organizations:
      - TARDIS INC

- name: "Delete a Partition Template"
  theforeman.foreman.partition_table:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: timeywimey
    layout: |
      <%#
          dummy:
      %>
    state: absent

- name: "Create a Partition Template from a file and modify with parameter(s)"
  theforeman.foreman.partition_table:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    file_name: timeywimey_template.erb
    name: Wibbly Wobbly Template
    state: present
    locations:
      - Gallifrey
    organizations:
      - TARDIS INC

# Providing a name in this case wouldn't be very sensible.
# Alternatively make use of with_filetree to parse recursively with filter.
- name: "Parsing a directory of partition templates"
  theforeman.foreman.partition_table:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    file_name: "{{ item }}"
    state: present
    locations:
      - SKARO
    organizations:
      - DALEK INC
    with_fileglob:
       - "./arsenal_templates/*.erb"

# If the templates are stored locally and the ansible module is executed on a remote host
- name: Ensure latest version of all Ptable Community Templates
  theforeman.foreman.partition_table:
    server_url: "https://foreman.example.com"
    username:  "admin"
    password:  "changeme"
    state: present
    layout: '{{ lookup("file", item.src) }}'
  with_filetree: '/path/to/partition/tables'
  when: item.state == 'file'


# with name set to "*" bulk actions can be performed
- name: "Delete *ALL* partition tables"
  theforeman.foreman.partition_table:
    username: "admin"
    password: "admin"
    server_url: "https://foreman.example.com"
    name: "*"
    state: absent

- name: "Assign all partition tables to the same organization(s)"
  theforeman.foreman.partition_table:
    username: "admin"
    password: "admin"
    server_url: "https://foreman.example.com"
    name: "*"
    state: present
    organizations:
      - DALEK INC
      - sky.net
      - Doc Brown's garage

'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    ptables:
      description: List of partition tables.
      type: list
      elements: dict
'''


import os

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanTaxonomicEntityAnsibleModule,
    parse_template,
    parse_template_from_file,
    OS_LIST,
)


class ForemanPtableModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanPtableModule(
        argument_spec=dict(
            file_name=dict(type='path'),
            state=dict(default='present', choices=['absent', 'present_with_defaults', 'present']),
            updated_name=dict(),
        ),
        foreman_spec=dict(
            layout=dict(),
            locked=dict(type='bool'),
            name=dict(),
            os_family=dict(choices=OS_LIST),
        ),
        mutually_exclusive=[
            ['file_name', 'layout'],
        ],
        required_one_of=[
            ['name', 'file_name', 'layout'],
        ],
    )

    # We do not want a layout text for bulk operations
    if module.foreman_params.get('name') == '*':
        if module.foreman_params.get('file_name') or module.foreman_params.get('layout') or module.foreman_params.get('updated_name'):
            module.fail_json(
                msg="Neither file_name nor layout nor updated_name allowed if 'name: *'!")

    entity = None
    file_name = module.foreman_params.pop('file_name', None)

    if file_name or 'layout' in module.foreman_params:
        if file_name:
            parsed_dict = parse_template_from_file(file_name, module)
        else:
            parsed_dict = parse_template(module.foreman_params['layout'], module)
        parsed_dict['layout'] = parsed_dict.pop('template')
        if 'oses' in parsed_dict:
            parsed_dict['os_family'] = parsed_dict.pop('oses')
        # sanitize name from template data
        # The following condition can actually be hit, when someone is trying to import a
        # template with the name set to '*'.
        # Besides not being sensible, this would go horribly wrong in this module.
        if parsed_dict.get('name') == '*':
            module.fail_json(msg="Cannot use '*' as a partition table name!")
        # module params are priorized
        parsed_dict.update(module.foreman_params)
        module.foreman_params = parsed_dict

    # make sure, we have a name
    if 'name' not in module.foreman_params:
        if file_name:
            module.foreman_params['name'] = os.path.splitext(
                os.path.basename(file_name))[0]
        else:
            module.fail_json(
                msg='No name specified and no filename to infer it.')

    affects_multiple = module.foreman_params['name'] == '*'
    # sanitize user input, filter unuseful configuration combinations with 'name: *'
    if affects_multiple:
        if module.state == 'present_with_defaults':
            module.fail_json(msg="'state: present_with_defaults' and 'name: *' cannot be used together")
        if module.desired_absent:
            further_params = set(module.foreman_params.keys()) - {'name', 'entity'}
            if further_params:
                module.fail_json(msg='When deleting all partition tables, there is no need to specify further parameters: %s ' % further_params)

    with module.api_connection():
        if affects_multiple:
            module.set_entity('entity', None)  # prevent lookup
            entities = module.list_resource('ptables')
            if not entities:
                # Nothing to do; shortcut to exit
                module.exit_json()
            if not module.desired_absent:  # not 'thin'
                entities = [module.show_resource('ptables', entity['id']) for entity in entities]
                module.auto_lookup_entities()
            module.foreman_params.pop('name')
            for entity in entities:
                module.ensure_entity('ptables', module.foreman_params, entity)
        else:
            # The name could have been determined to late, so copy it again
            module.foreman_params['entity'] = module.foreman_params['name']

            module.run()


if __name__ == '__main__':
    main()
