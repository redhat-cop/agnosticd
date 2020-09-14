#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2020 Baptiste Agasse (@bagasse)
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
module: smart_class_parameter
version_added: 1.0.0
short_description: Manage Smart Class Parameters
description:
  - Update Smart Class Parameters.
  - Smart Class Parameters are created/deleted for Puppet classes during import and cannot be created or deleted otherwise.
author:
  - "Baptiste Agasse (@bagasse)"
options:
  puppetclass_name:
    description: Name of the puppetclass that own the parameter
    required: true
    type: str
  parameter:
    description: Name of the parameter
    required: true
    type: str
  description:
    description: Description of the Smart Class Parameter
    type: str
  override:
    description: Whether the smart class parameter value is managed by Foreman
    type: bool
  default_value:
    description: Value to use by default.
    type: raw
  hidden_value:
    description: When enabled the parameter is hidden in the UI.
    type: bool
  omit:
    description:
      - Don't send this parameter in classification output.
      - Puppet will use the value defined in the Puppet manifest for this parameter.
    type: bool
  override_value_order:
    description: The order in which values are resolved.
    type: list
    elements: str
  validator_type:
    description: Types of validation values.
    type: str
    choices:
      - regexp
      - list
  validator_rule:
    description: Used to enforce certain values for the parameter values.
    type: str
  parameter_type:
    description: Types of variable values. If C(none), set the parameter type to empty value.
    type: str
    choices:
      - string
      - boolean
      - integer
      - real
      - array
      - hash
      - yaml
      - json
      - none
  required:
    description: If true, will raise an error if there is no default value and no matcher provide a value.
    type: bool
  merge_overrides:
    description: Merge all matching values (only array/hash type).
    type: bool
  merge_default:
    description: Include default value when merging all matching values.
    type: bool
  avoid_duplicates:
    description: Remove duplicate values (only array type)
    type: bool
  override_values:
    description: Value overrides
    required: false
    type: list
    elements: dict
    suboptions:
      match:
        description: Override match
        required: true
        type: str
      value:
        description: Override value, required if omit is false
        type: raw
      omit:
        description: Don't send this parameter in classification output, replaces use_puppet_default.
        type: bool
  state:
    description: State of the entity.
    type: str
    default: present
    choices:
      - present
      - present_with_defaults
extends_documentation_fragment:
  - theforeman.foreman.foreman
'''

EXAMPLES = '''
- name: "Update prometheus::server alertmanagers_config param default value"
  theforeman.foreman.smart_class_parameter:
    puppetclass_name: "prometheus::server"
    parameter: alertmanagers_config
    override: true
    required: true
    default_value: /etc/prometheus/alert.yml
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: "Update prometheus::server alertmanagers_config param default value"
  theforeman.foreman.smart_class_parameter:
    puppetclass_name: "prometheus::server"
    parameter: alertmanagers_config
    override: true
    override_value_order:
      - fqdn
      - hostgroup
      - domain
    required: true
    default_value: /etc/prometheus/alert.yml
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    override_values:
      - match: domain=example.com
        value: foo
      - match: domain=foo.example.com
        omit: true
    state: present
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    smart_class_parameters:
      description: List of smart class parameters.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule, parameter_value_to_str

override_value_foreman_spec = dict(
    match=dict(required=True),
    value=dict(type='raw'),
    omit=dict(type='bool'),
)


class ForemanSmartClassParameterModule(ForemanEntityAnsibleModule):
    # TODO: greatly similar to how parameters are managed, dry it up ?
    def ensure_override_values(self, entity, expected_override_values):
        if expected_override_values is not None:
            parameter_type = entity.get('parameter_type', 'string')
            scope = {'smart_class_parameter_id': entity['id']}
            if not self.desired_absent:
                current_override_values = {override_value['match']: override_value for override_value in entity.get('override_values', [])}
                desired_override_values = {override_value['match']: override_value for override_value in expected_override_values}

                for match in desired_override_values:
                    desired_override_value = desired_override_values[match]
                    if 'value' in desired_override_value:
                        desired_override_value['value'] = parameter_value_to_str(desired_override_value['value'], parameter_type)
                    current_override_value = current_override_values.pop(match, None)
                    if current_override_value:
                        current_override_value['value'] = parameter_value_to_str(current_override_value['value'], parameter_type)
                    self.ensure_entity(
                        'override_values', desired_override_value, current_override_value,
                        state="present", foreman_spec=override_value_foreman_spec, params=scope)
                for current_override_value in current_override_values.values():
                    self.ensure_entity(
                        'override_values', None, current_override_value, state="absent", foreman_spec=override_value_foreman_spec, params=scope)


def main():
    module = ForemanSmartClassParameterModule(
        argument_spec=dict(
            puppetclass_name=dict(required=True),
            parameter=dict(required=True),
            state=dict(default='present', choices=['present_with_defaults', 'present']),
        ),
        foreman_spec=dict(
            parameter_type=dict(choices=['string', 'boolean', 'integer', 'real', 'array', 'hash', 'yaml', 'json', 'none']),
            validator_type=dict(choices=['list', 'regexp']),
            validator_rule=dict(),
            description=dict(),
            default_value=dict(type='raw'),
            omit=dict(type='bool'),
            override=dict(type='bool'),
            merge_default=dict(type='bool'),
            merge_overrides=dict(type='bool'),
            avoid_duplicates=dict(type='bool'),
            required=dict(type='bool'),
            hidden_value=dict(type='bool'),
            override_value_order=dict(type='list', elements='str'),
            # tried nested_list here but, if using nested_list, override_values are not part of loaded entity.
            # override_values=dict(type='nested_list', elements='dict', foreman_spec=override_value_foreman_spec),
            override_values=dict(type='list', elements='dict'),
        ),
        # smart_class_parameters are created on puppetclass import and cannot be created/deleted from API,
        # so if we don't find it, it's an error.
        entity_opts=dict(failsafe=False),
    )

    module_params = module.foreman_params
    if module_params.get('parameter_type', 'string') not in ['array', 'hash']:
        if 'merge_default' in module_params or 'merge_overrides' in module_params:
            module.fail_json(msg="merge_default or merge_overrides can be used only with array or hash parameter_type")
    if module_params.get('parameter_type', 'string') != 'array' and 'avoid_duplicates' in module_params:
        module.fail_json(msg="avoid_duplicates can be used only with array parameter_type")

    search = "puppetclass_name={0} and parameter={1}".format(module_params['puppetclass_name'], module_params['parameter'])
    override_values = module_params.pop('override_values', None)

    if 'override_value_order' in module_params:
        module_params['override_value_order'] = '\n'.join(module_params['override_value_order'])
    if 'parameter_type' in module_params and module_params['parameter_type'] == 'none':
        module_params['parameter_type'] = ''

    with module.api_connection():
        entity = module.find_resource('smart_class_parameters', search=search)
        module.set_entity('entity', entity)
        # When override is set to false, foreman API don't accept parameter_type and all 'override options' have to be set to false if present
        if not module_params.get('override', False):
            module_params['parameter_type'] = ''
            for override_option in ['merge_default', 'merge_overrides', 'avoid_duplicates']:
                if override_option in entity and entity[override_option]:
                    module_params[override_option] = False

        # Foreman API returns 'hidden_value?' instead of 'hidden_value' this is a bug ?
        if 'hidden_value?' in entity:
            entity['hidden_value'] = entity.pop('hidden_value?')
        if 'default_value' in module_params:
            module_params['default_value'] = parameter_value_to_str(module_params['default_value'], module_params.get('parameter_type', 'string'))
        if 'default_value' in entity:
            entity['default_value'] = parameter_value_to_str(entity['default_value'], entity.get('parameter_type', 'string'))

        entity = module.run()
        module.ensure_override_values(entity, override_values)


if __name__ == '__main__':
    main()
