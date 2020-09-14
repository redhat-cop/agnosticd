#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Andrew Kofink <ajkofink@gmail.com>
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
module: subscription_manifest
version_added: 1.0.0
short_description: Manage Subscription Manifests
description:
  - Upload, refresh and delete Subscription Manifests
author: "Andrew Kofink (@akofink)"
options:
  manifest_path:
    description:
      - Path to the manifest zip file
      - This parameter will be ignored if I(state=absent) or I(state=refreshed)
    type: path
  state:
    description:
      - The state of the manifest
    default: present
    choices:
      - absent
      - present
      - refreshed
    type: str
  repository_url:
    description:
       - URL to retrieve content from
    aliases: [ redhat_repository_url ]
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Upload the RHEL developer edition manifest"
  theforeman.foreman.subscription_manifest:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    state: present
    manifest_path: "/tmp/manifest.zip"
'''

RETURN = ''' # '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


def main():
    module = KatelloEntityAnsibleModule(
        argument_spec=dict(
            manifest_path=dict(type='path'),
            state=dict(default='present', choices=['absent', 'present', 'refreshed']),
            repository_url=dict(aliases=['redhat_repository_url']),
        ),
        foreman_spec=dict(
            organization=dict(type='entity', required=True, thin=False),
        ),
        required_if=[
            ['state', 'present', ['manifest_path']],
        ],
        supports_check_mode=False,
    )

    module.task_timeout = 5 * 60

    with module.api_connection():
        organization = module.lookup_entity('organization')
        scope = module.scope_for('organization')

        try:
            existing_manifest = organization['owner_details']['upstreamConsumer']
        except KeyError:
            existing_manifest = None

        if module.state == 'present':
            if 'repository_url' in module.foreman_params:
                payload = {'redhat_repository_url': module.foreman_params['repository_url']}
                org_spec = dict(id=dict(), redhat_repository_url=dict())
                organization = module.ensure_entity('organizations', payload, organization, state='present', foreman_spec=org_spec)

            try:
                with open(module.foreman_params['manifest_path'], 'rb') as manifest_file:
                    files = {'content': (module.foreman_params['manifest_path'], manifest_file, 'application/zip')}
                    params = {}
                    if 'repository_url' in module.foreman_params:
                        params['repository_url'] = module.foreman_params['repository_url']
                    params.update(scope)
                    result = module.resource_action('subscriptions', 'upload', params, files=files, record_change=False, ignore_task_errors=True)
                    for error in result['humanized']['errors']:
                        if "same as existing data" in error:
                            # Nothing changed, but everything ok
                            break
                        if "older than existing data" in error:
                            module.fail_json(msg="Manifest is older than existing data.")
                        else:
                            module.fail_json(msg="Upload of the manifest failed: %s" % error)
                    else:
                        module.set_changed()
            except IOError as e:
                module.fail_json(msg="Unable to read the manifest file: %s" % e)
        elif module.desired_absent and existing_manifest:
            module.resource_action('subscriptions', 'delete_manifest', scope)
        elif module.state == 'refreshed':
            if existing_manifest:
                module.resource_action('subscriptions', 'refresh_manifest', scope)
            else:
                module.fail_json(msg="No manifest found to refresh.")


if __name__ == '__main__':
    main()
