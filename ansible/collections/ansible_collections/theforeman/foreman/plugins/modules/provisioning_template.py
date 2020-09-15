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
module: provisioning_template
version_added: 1.0.0
short_description: Manage Provisioning Templates
description:
  - Manage Provisioning Templates
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
  - "Matthias Dellweg (@mdellweg) ATIX AG"
options:
  audit_comment:
    description:
      - Content of the audit comment field
    required: false
    type: str
  kind:
    description:
      - The provisioning template kind
    required: false
    choices:
      - Bootdisk
      - cloud-init
      - finish
      - iPXE
      - job_template
      - kexec
      - POAP
      - provision
      - ptable
      - PXEGrub
      - PXEGrub2
      - PXELinux
      - registration
      - script
      - snippet
      - user_data
      - ZTP
    type: str
  template:
    description:
      - The content of the provisioning template.
      - Either this or I(file_name) is required as a source for the Provisioning Template "content".
    required: false
    type: str
  file_name:
    description:
      - The path of a template file, that shall be imported.
      - Either this or I(template) is required as a source for the Provisioning Template "content".
    required: false
    type: path
  locked:
    description:
      - Determines whether the template shall be locked
    required: false
    type: bool
  name:
    description:
      - The name of the Provisioning Template.
      - If omited, will be determined from the C(name) header of the template or the filename (in that order).
      - The special value "*" can be used to perform bulk actions (modify, delete) on all existing templates.
    required: false
    type: str
  updated_name:
    description: New provisioning template name. When this parameter is set, the module will not be idempotent.
    type: str
  operatingsystems:
    description: The Operatingsystems the template shall be assigned to
    required: false
    type: list
    elements: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''

# Keep in mind, that in this case, the inline parameters will be overwritten
- name: "Create a Provisioning Template inline"
  theforeman.foreman.provisioning_template:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: A New Finish Template
    kind: finish
    state: present
    template: |
      <%#
          name: Finish timetravel
          kind: finish
      %>
      cd /
      rm -rf *
    locations:
      - Gallifrey
    organizations:
      - TARDIS INC

- name: "Create a Provisioning Template from a file"
  theforeman.foreman.provisioning_template:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    file_name: timeywimey_template.erb
    state: present
    locations:
      - Gallifrey
    organizations:
      - TARDIS INC

# Due to the module logic, deleting requires a template dummy,
# either inline or from a file.
- name: "Delete a Provisioning Template"
  theforeman.foreman.provisioning_template:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: timeywimey_template
    template: |
      <%#
          dummy:
      %>
    state: absent

- name: "Create a Provisioning Template from a file and modify with parameter"
  theforeman.foreman.provisioning_template:
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
- name: "Parsing a directory of provisioning templates"
  theforeman.foreman.provisioning_template:
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
- name: Ensure latest version of all Provisioning Community Templates
  theforeman.foreman.provisioning_template:
    server_url: "https://foreman.example.com"
    username:  "admin"
    password:  "changeme"
    state: present
    template: '{{ lookup("file", item.src) }}'
  with_filetree: '/path/to/provisioning/templates'
  when: item.state == 'file'


# with name set to "*" bulk actions can be performed
- name: "Delete *ALL* provisioning templates"
  theforeman.foreman.provisioning_template:
    username: "admin"
    password: "admin"
    server_url: "https://foreman.example.com"
    name: "*"
    state: absent

- name: "Assign all provisioning templates to the same organization(s)"
  theforeman.foreman.provisioning_template:
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
    provisioning_templates:
      description: List of provisioning templates.
      type: list
      elements: dict
'''


import os

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanTaxonomicEntityAnsibleModule,
    parse_template,
    parse_template_from_file,
)


def find_template_kind(module, module_params):
    if 'kind' not in module_params:
        return module_params

    module_params['snippet'] = (module_params['kind'] == 'snippet')
    if module_params['snippet']:
        module_params.pop('kind')
    else:
        module_params['kind'] = module.find_resource_by_name('template_kinds', module_params['kind'], thin=True)
    return module_params


class ForemanProvisioningTemplateModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanProvisioningTemplateModule(
        argument_spec=dict(
            audit_comment=dict(),
            file_name=dict(type='path'),
            state=dict(default='present', choices=['absent', 'present_with_defaults', 'present']),
            updated_name=dict(),
        ),
        foreman_spec=dict(
            kind=dict(choices=[
                'Bootdisk',
                'cloud-init',
                'finish',
                'iPXE',
                'job_template',
                'kexec',
                'POAP',
                'provision',
                'ptable',
                'PXEGrub',
                'PXEGrub2',
                'PXELinux',
                'registration',
                'script',
                'snippet',
                'user_data',
                'ZTP',
            ], type='entity', flat_name='template_kind_id', resolve=False),
            template=dict(),
            locked=dict(type='bool'),
            name=dict(),
            operatingsystems=dict(type='entity_list'),
            snippet=dict(type='invisible'),
        ),
        mutually_exclusive=[
            ['file_name', 'template'],
        ],
        required_one_of=[
            ['name', 'file_name', 'template'],
        ],
    )

    # We do not want a template text for bulk operations
    if module.foreman_params.get('name') == '*':
        if module.foreman_params.get('file_name') or module.foreman_params.get('template') or module.foreman_params.get('updated_name'):
            module.fail_json(
                msg="Neither file_name nor template nor updated_name allowed if 'name: *'!")

    entity = None
    file_name = module.foreman_params.pop('file_name', None)

    if file_name or 'template' in module.foreman_params:
        if file_name:
            parsed_dict = parse_template_from_file(file_name, module)
        else:
            parsed_dict = parse_template(module.foreman_params['template'], module)
        # sanitize name from template data
        # The following condition can actually be hit, when someone is trying to import a
        # template with the name set to '*'.
        # Besides not being sensible, this would go horribly wrong in this module.
        if parsed_dict.get('name') == '*':
            module.fail_json(msg="Cannot use '*' as a template name!")
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
        if module.foreman_params.get('updated_name'):
            module.fail_json(msg="updated_name not allowed if 'name: *'!")
        if module.state == 'present_with_defaults':
            module.fail_json(msg="'state: present_with_defaults' and 'name: *' cannot be used together")
        if module.desired_absent:
            further_params = set(module.foreman_params.keys()) - {'name', 'entity'}
            if further_params:
                module.fail_json(msg='When deleting all templates, there is no need to specify further parameters: %s ' % further_params)

    with module.api_connection():
        if 'audit_comment' in module.foreman_params:
            extra_params = {'audit_comment': module.foreman_params['audit_comment']}
        else:
            extra_params = {}

        if affects_multiple:
            module.set_entity('entity', None)  # prevent lookup
            entities = module.list_resource('provisioning_templates')
            if not entities:
                # Nothing to do; shortcut to exit
                module.exit_json()
            if not module.desired_absent:  # not 'thin'
                entities = [module.show_resource('provisioning_templates', entity['id']) for entity in entities]
                module.auto_lookup_entities()
            module.foreman_params.pop('name')
            for entity in entities:
                module.ensure_entity('provisioning_templates', module.foreman_params, entity, params=extra_params)
        else:
            # The name could have been determined to late, so copy it again
            module.foreman_params['entity'] = module.foreman_params['name']

            module.foreman_params = find_template_kind(module, module.foreman_params)

            module.run(params=extra_params)


if __name__ == '__main__':
    main()
