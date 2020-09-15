#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018, Sean O'Keeffe <seanokeeffe797@gmail.com>
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
module: content_view_version
version_added: 1.0.0
short_description: Manage Content View Versions
description:
  - Publish, Promote or Remove a Content View Version
author: Sean O'Keeffe (@sean797)
notes:
  - You cannot use this to remove a Content View Version from a Lifecycle environment, you should promote another version first.
  - For idempotency you must specify either C(version) or C(current_lifecycle_environment).
options:
  content_view:
    description:
      - Name of the content view
    required: true
    type: str
  description:
    description:
      - Description of the Content View Version
    type: str
  version:
    description:
      - The content view version number (i.e. 1.0)
    type: str
  lifecycle_environments:
    description:
      - The lifecycle environments the Content View Version should be in.
    type: list
    elements: str
  force_promote:
    description:
      - Force content view promotion and bypass lifecycle environment restriction
    default: false
    type: bool
    aliases:
      - force
  force_yum_metadata_regeneration:
    description:
      - Force metadata regeneration when performing Publish and Promote tasks
    type: bool
    default: false
  current_lifecycle_environment:
    description:
      - The lifecycle environment that is already associated with the content view version
      - Helpful for promoting a content view version
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Ensure content view version 2.0 is in Test & Pre Prod"
  theforeman.foreman.content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    content_view: "CV 1"
    organization: "Default Organization"
    version: 2.0
    lifecycle_environments:
      - Test
      - Pre Prod

- name: "Ensure content view version in Test is also in Pre Prod"
  theforeman.foreman.content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    content_view: "CV 1"
    organization: "Default Organization"
    current_lifecycle_environment: Test
    lifecycle_environments:
      - Pre Prod

- name: "Publish a content view, not idempotent"
  theforeman.foreman.content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    content_view: "CV 1"
    organization: "Default Organization"

- name: "Publish a content view and promote that version to Library & Dev, not idempotent"
  theforeman.foreman.content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    content_view: "CV 1"
    organization: "Default Organization"
    lifecycle_environments:
      - Library
      - Dev

- name: "Ensure content view version 1.0 doesn't exist"
  theforeman.foreman.content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    content_view: "Web Servers"
    organization: "Default Organization"
    version: 1.0
    state: absent
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    content_view_versions:
      description: List of content view versions.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


def promote_content_view_version(module, content_view_version, environments, force, force_yum_metadata_regeneration):
    current_environment_ids = {environment['id'] for environment in content_view_version['environments']}
    desired_environment_ids = {environment['id'] for environment in environments}
    promote_to_environment_ids = list(desired_environment_ids - current_environment_ids)

    if promote_to_environment_ids:
        payload = {
            'id': content_view_version['id'],
            'environment_ids': promote_to_environment_ids,
            'force': force,
            'force_yum_metadata_regeneration': force_yum_metadata_regeneration,
        }

        module.record_before('content_view_versions', {'id': content_view_version['id'], 'environments': content_view_version['environments']})
        module.resource_action('content_view_versions', 'promote', params=payload)
        module.record_after('content_view_versions', {'id': content_view_version['id'], 'environments': environments})
        module.record_after_full('content_view_versions', {'id': content_view_version['id'], 'environments': environments})


class KatelloContentViewVersionModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloContentViewVersionModule(
        foreman_spec=dict(
            content_view=dict(type='entity', required=True, scope=['organization']),
            description=dict(),
            version=dict(),
            lifecycle_environments=dict(type='entity_list', scope=['organization']),
            force_promote=dict(type='bool', aliases=['force'], default=False),
            force_yum_metadata_regeneration=dict(type='bool', default=False),
            current_lifecycle_environment=dict(type='entity', resource_type='lifecycle_environments', scope=['organization']),
        ),
        mutually_exclusive=[['current_lifecycle_environment', 'version']],
    )

    module.task_timeout = 60 * 60

    with module.api_connection():
        scope = module.scope_for('organization')
        content_view = module.lookup_entity('content_view')

        if 'current_lifecycle_environment' in module.foreman_params:
            search_scope = {'content_view_id': content_view['id'], 'environment_id': module.lookup_entity('current_lifecycle_environment')['id']}
            content_view_version = module.find_resource('content_view_versions', search=None, params=search_scope)
        elif 'version' in module.foreman_params:
            search = "content_view_id={0},version={1}".format(content_view['id'], module.foreman_params['version'])
            content_view_version = module.find_resource('content_view_versions', search=search, failsafe=True)
        else:
            content_view_version = None
        module.set_entity('entity', content_view_version)

        if module.desired_absent:
            module.ensure_entity('content_view_versions', None, content_view_version, params=scope)
        else:
            module.auto_lookup_entities()
            if content_view_version is None:
                payload = {
                    'id': content_view['id'],
                }
                if 'description' in module.foreman_params:
                    payload['description'] = module.foreman_params['description']
                if 'force_yum_metadata_regeneration' in module.foreman_params:
                    payload['force_yum_metadata_regeneration'] = module.foreman_params['force_yum_metadata_regeneration']
                if 'version' in module.foreman_params:
                    split_version = list(map(int, str(module.foreman_params['version']).split('.')))
                    payload['major'] = split_version[0]
                    payload['minor'] = split_version[1]

                response = module.resource_action('content_views', 'publish', params=payload)
                # workaround for https://projects.theforeman.org/issues/28138
                if not module.check_mode:
                    content_view_version_id = response['output'].get('content_view_version_id') or response['input'].get('content_view_version_id')
                    content_view_version = module.show_resource('content_view_versions', content_view_version_id)
                else:
                    content_view_version = {'id': -1, 'environments': []}

            if 'lifecycle_environments' in module.foreman_params:
                promote_content_view_version(
                    module,
                    content_view_version,
                    module.foreman_params['lifecycle_environments'],
                    force=module.foreman_params['force_promote'],
                    force_yum_metadata_regeneration=module.foreman_params['force_yum_metadata_regeneration'],
                )


if __name__ == '__main__':
    main()
