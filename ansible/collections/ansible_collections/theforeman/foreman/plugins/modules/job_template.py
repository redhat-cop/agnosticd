#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Manuel Bonk & Matthias Dellweg (ATIX AG)
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
module: job_template
version_added: 1.0.0
short_description: Manage Job Templates
description:
  - Manage Remote Execution Job Templates
author:
  - "Manuel Bonk (@manuelbonk) ATIX AG"
  - "Matthias Dellweg (@mdellweg) ATIX AG"
options:
  audit_comment:
    description:
      - Content of the audit comment field
    type: str
  description_format:
    description:
      - description of the job template. Template inputs can be referenced.
    type: str
  file_name:
    description:
      - The path of a template file, that shall be imported.
      - Either this or I(template) is required as a source for the Job Template "content".
    type: path
  job_category:
    description:
      - The category the template should be assigend to
    type: str
  locked:
    description:
      - Determines whether the template shall be locked
    default: false
    type: bool
  name:
    description:
      - The name of the Job Template.
      - If omited, will be determined from the C(name) header of the template or the filename (in that order).
      - The special value "*" can be used to perform bulk actions (modify, delete) on all existing templates.
    type: str
  provider_type:
    description:
      - Determines via which provider the template shall be executed
    required: false
    type: str
  snippet:
    description:
      - Determines whether the template shall be a snippet
    default: false
    type: bool
  template:
    description:
      - The content of the Job Template.
      - Either this or I(file_name) is required as a source for the Job Template "content".
    type: str
  template_inputs:
    description:
      - The template inputs used in the Job Template
    type: list
    elements: dict
    suboptions:
      advanced:
        description:
          - Template Input is advanced
        default: false
        type: bool
      description:
        description:
          - description of the Template Input
        type: str
      fact_name:
        description:
          - Fact name, used when input type is fact
        type: str
      input_type:
        description:
          - input type
        required: true
        choices:
          - user
          - fact
          - variable
          - puppet_parameter
        type: str
      name:
        description:
          - name of the Template Input
        required: true
        type: str
      options:
        description:
          - Template values for user inputs. Must be an array of any type.
        type: list
        elements: raw
      puppet_class_name:
        description:
          - Puppet class name, used when input type is puppet_parameter
        type: str
      puppet_parameter_name:
        description:
          - Puppet parameter name, used when input type is puppet_parameter
        type: str
      required:
        description:
          - Is the input required
        type: bool
      variable_name:
        description:
          - Variable name, used when input type is variable
        type: str
      value_type:
        description:
          - Type of the value
        choices:
          - plain
          - search
          - date
        type: str
      resource_type:
        description:
          - Type of the resource
        type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''

- name: "Create a Job Template inline"
  theforeman.foreman.job_template:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: A New Job Template
    state: present
    template: |
      <%#
          name: A Job Template
      %>
      rm -rf <%= input("toDelete") %>
    template_inputs:
      - name: toDelete
        input_type: user
    locations:
    - Gallifrey
    organizations:
    - TARDIS INC

- name: "Create a Job Template from a file"
  theforeman.foreman.job_template:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: a new job template
    file_name: timeywimey_template.erb
    template_inputs:
      - name: a new template input
        input_type: user
    state: present
    locations:
    - Gallifrey
    organizations:
    - TARDIS INC

- name: "remove a job template's template inputs"
  theforeman.foreman.job_template:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: a new job template
    template_inputs: []
    state: present
    locations:
    - Gallifrey
    organizations:
    - TARDIS INC

- name: "Delete a Job Template"
  theforeman.foreman.job_template:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: timeywimey
    state: absent

- name: "Create a Job Template from a file and modify with parameter(s)"
  theforeman.foreman.job_template:
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
- name: Parsing a directory of Job templates
  theforeman.foreman.job_template:
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
- name: Ensure latest version of all your Job Templates
  theforeman.foreman.job_template:
    server_url: "https://foreman.example.com"
    username:  "admin"
    password:  "changeme"
    state: present
    template: '{{ lookup("file", item.src) }}'
  with_filetree: '/path/to/job/templates'
  when: item.state == 'file'


# with name set to "*" bulk actions can be performed
- name: "Delete *ALL* Job Templates"
  theforeman.foreman.job_template:
    username: "admin"
    password: "admin"
    server_url: "https://foreman.example.com"
    name: "*"
    state: absent

- name: "Assign all Job Templates to the same organization(s)"
  theforeman.foreman.job_template:
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
    job_templates:
      description: List of job templates.
      type: list
      elements: dict
    template_inputs:
      description: List of template inputs associated with the job template.
      type: list
      elements: dict
'''

import os
from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanTaxonomicEntityAnsibleModule,
    parse_template,
    parse_template_from_file,
)


template_defaults = {
    'provider_type': 'SSH',
    'job_category': 'unknown',
}


template_input_foreman_spec = {
    'name': dict(required=True),
    'description': dict(),
    'required': dict(type='bool'),
    'advanced': dict(type='bool'),
    'input_type': dict(required=True, choices=[
        'user',
        'fact',
        'variable',
        'puppet_parameter',
    ]),
    'fact_name': dict(),
    'variable_name': dict(),
    'puppet_class_name': dict(),
    'puppet_parameter_name': dict(),
    'options': dict(type='list', elements='raw'),
    'value_type': dict(choices=[
        'plain',
        'search',
        'date',
    ]),
    'resource_type': dict(),
}


class ForemanJobTemplateModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanJobTemplateModule(
        foreman_spec=dict(
            description_format=dict(),
            job_category=dict(),
            locked=dict(type='bool', default=False),
            name=dict(),
            provider_type=dict(),
            snippet=dict(type='bool'),
            template=dict(),
            template_inputs=dict(type='nested_list', foreman_spec=template_input_foreman_spec),
        ),
        argument_spec=dict(
            audit_comment=dict(),
            file_name=dict(type='path'),
            state=dict(default='present', choices=['absent', 'present_with_defaults', 'present']),
        ),
        mutually_exclusive=[
            ['file_name', 'template'],
        ],
        required_one_of=[
            ['name', 'file_name', 'template'],
        ],
    )

    # We do not want a layout text for bulk operations
    if module.foreman_params.get('name') == '*':
        if module.foreman_params.get('file_name') or module.foreman_params.get('template'):
            module.fail_json(
                msg="Neither file_name nor template allowed if 'name: *'!")

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
            module.fail_json(msg="Cannot use '*' as a job template name!")
        # module params are priorized
        parsed_dict.update(module.foreman_params)
        # make sure certain values are set
        module.foreman_params = template_defaults.copy()
        module.foreman_params.update(parsed_dict)

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
                module.fail_json(msg='When deleting all job templates, there is no need to specify further parameters: %s ' % further_params)

    with module.api_connection():
        if 'audit_comment' in module.foreman_params:
            extra_params = {'audit_comment': module.foreman_params['audit_comment']}
        else:
            extra_params = {}

        if affects_multiple:
            module.set_entity('entity', None)  # prevent lookup
            entities = module.list_resource('job_templates')
            if not entities:
                # Nothing to do; shortcut to exit
                module.exit_json()
            if not module.desired_absent:  # not 'thin'
                entities = [module.show_resource('job_templates', entity['id']) for entity in entities]
                module.auto_lookup_entities()
            module.foreman_params.pop('name')
            for entity in entities:
                module.ensure_entity('job_templates', module.foreman_params, entity, params=extra_params)
        else:
            # The name could have been determined to late, so copy it again
            module.foreman_params['entity'] = module.foreman_params['name']
            entity = module.lookup_entity('entity')
            # TemplateInputs need to be added as separate entities later
            template_inputs = module.foreman_params.get('template_inputs')

            job_template = module.run(params=extra_params)

            update_dependent_entities = (module.state == 'present' or (module.state == 'present_with_defaults' and module.changed))
            if update_dependent_entities and template_inputs is not None:
                scope = {'template_id': job_template['id']}

                # Manage TemplateInputs here
                current_template_input_list = module.list_resource('template_inputs', params=scope) if entity else []
                current_template_inputs = {item['name']: item for item in current_template_input_list}
                for template_input_dict in template_inputs:
                    template_input_dict = {key: value for key, value in template_input_dict.items() if value is not None}

                    template_input_entity = current_template_inputs.pop(template_input_dict['name'], None)

                    module.ensure_entity(
                        'template_inputs', template_input_dict, template_input_entity,
                        params=scope, foreman_spec=template_input_foreman_spec,
                    )

                # At this point, desired template inputs have been removed from the dict.
                for template_input_entity in current_template_inputs.values():
                    module.ensure_entity(
                        'template_inputs', None, template_input_entity, state="absent",
                        params=scope, foreman_spec=template_input_foreman_spec,
                    )


if __name__ == '__main__':
    main()
