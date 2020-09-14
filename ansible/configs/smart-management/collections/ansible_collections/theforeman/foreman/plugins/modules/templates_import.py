#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2020 Anton Nesterov (@nesanton)
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
module: templates_import
version_added: 1.0.0
short_description: Sync Templates from a repository
description:
  - Sync provisioning templates, report_templates, partition tables and job templates from external git repository or file system.
  - Based on foreman_templates plugin U(https://github.com/theforeman/foreman_templates).
author:
  - "Anton Nesterov (@nesanton)"
notes:
  - Due to a bug in the foreman_templates plugin, this module won't report C(changed=true)
    when the only change is the Organization/Location association of the imported templates.
    Please see U(https://projects.theforeman.org/issues/29534) for details.
  - Default values for all module options can be set using M(theforeman.foreman.setting) for TemplateSync category or on the settings page in WebUI.
options:
  prefix:
    description:
      - Adds specified string to beginning of all imported templates that do not yet have that prefix.
    required: false
    type: str
  associate:
    description:
      - Associate to Operatingsystems, Locations and Organizations based on metadata.
    required: false
    type: str
    choices:
     - always
     - new
     - never
  verbose:
    description:
      - Add template reports to the output.
    required: false
    type: bool
  force:
    description:
      - Update templates that are locked.
    required: false
    type: bool
  lock:
    description:
      - Lock imported templates.
    required: false
    type: bool
  branch:
    description:
      - Branch of the I(repo). Only for git-based repositories.
    required: false
    type: str
  repo:
    description:
      - Filesystem path or repo (with protocol), for example /tmp/dir or git://example.com/repo.git or https://example.com/repo.git.
    required: false
    type: str
  filter:
    description:
      - Sync only templates with name matching this regular expression, after I(prefix) was applied.
      - Case-insensitive, snippets are not filtered.
    required: false
    type: str
  negate:
    description:
      - Negate the filter condition.
    required: false
    type: bool
  dirname:
    description:
      - The directory within Git repo containing the templates.
    required: false
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
- name: Sync templates from git repo
  theforeman.foreman.templates_import:
    repo: https://github.com/theforeman/community-templates.git
    branch: 1.24-stable
    associate: new
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "changeme"
'''

RETURN = '''
message:
  description: Information about the import.
  returned: success
  type: dict
  contains:
    repo:
      description: Repository, the templates were imported from.
      type: str
    branch:
      description: Branch used in the repository.
      type: str
report:
  description: Report of the import.
  returned: success
  type: dict
  contains:
    changed:
      description: List of templates that have been updated.
      type: list
    new:
      description: List of templates that have been created.
      type: list
templates:
  description: Final state of the templates.
  returned: success
  type: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanTaxonomicAnsibleModule, _flatten_entity


def main():
    module = ForemanTaxonomicAnsibleModule(
        foreman_spec=dict(
            associate=dict(choices=['always', 'new', 'never']),
            prefix=dict(),
            branch=dict(),
            repo=dict(),
            filter=dict(),
            dirname=dict(),
            verbose=dict(type='bool'),
            force=dict(type='bool'),
            lock=dict(type='bool'),
            negate=dict(type='bool'),
        ),
        supports_check_mode=False,
        required_plugins=[('templates', ['*'])],
    )

    with module.api_connection():

        module.auto_lookup_entities()

        # Build a list of all existing templates of all supported types to check if we are adding any new
        template_report = []

        template_types = ['provisioning_templates', 'report_templates', 'ptables']
        if 'job_templates' in module.foremanapi.resources:
            template_types.append('job_templates')

        for template_type in template_types:
            template_report += [(resource['name'], resource['id']) for resource in module.list_resource(template_type)]

        result = module.resource_action('templates', 'import', record_change=False, params=_flatten_entity(module.foreman_params, module.foreman_spec))
        msg_templates = result['message'].pop('templates', [])

        report = {'changed': [], 'new': []}
        templates = {}

        for template in msg_templates:
            if template['changed']:
                report['changed'].append(template['name'])
                module.set_changed()
            elif template['imported']:
                if (template['name'], template['id']) not in template_report:
                    report['new'].append(template['name'])
                    module.set_changed()
            templates[template.pop('name')] = template

        module.exit_json(templates=templates, message=result['message'], report=report)


if __name__ == '__main__':
    main()
