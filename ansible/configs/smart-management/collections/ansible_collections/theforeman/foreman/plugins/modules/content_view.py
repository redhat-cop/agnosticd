#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2016, Eric D Helms <ericdhelms@gmail.com>
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
module: content_view
version_added: 1.0.0
short_description: Manage Content Views
description:
    - Create and manage content views
author: "Eric D Helms (@ehelms)"
options:
  name:
    description:
      - Name of the Content View
    required: true
    type: str
  description:
    description:
      - Description of the Content View
    type: str
  repositories:
    description:
      - List of repositories that include name and product.
      - Cannot be combined with I(composite=True).
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Name of the Repository to be added
        type: str
        required: true
      product:
        description:
          - Product of the Repository to be added
        type: str
        required: true
  auto_publish:
    description:
      - Auto publish composite view when a new version of a component content view is created.
      - Also note auto publish will only happen when the component is marked "latest".
    default: false
    type: bool
  solve_dependencies:
    description:
      - Solve RPM dependencies by default on Content View publish
    type: bool
  composite:
    description:
      - A composite view contains other content views.
    default: false
    type: bool
  components:
    description:
      - List of content views to includes content_view and either version or latest.
      - Ignored if I(composite=False).
    type: list
    elements: dict
    suboptions:
      content_view:
        description:
          - Content View name to be added to the Composite Content View
        type: str
        required: true
      latest:
        description:
          - Always use the latest Content View Version
        type: bool
        default: False
      content_view_version:
        description:
          - Version of the Content View to add
        type: str
        aliases:
          - version
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Create or update Fedora content view"
  theforeman.foreman.content_view:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Fedora CV"
    organization: "My Cool new Organization"
    repositories:
      - name: 'Fedora 26'
        product: 'Fedora'

- name: "Create a composite content view"
  theforeman.foreman.content_view:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Fedora CCV"
    organization: "My Cool new Organization"
    composite: true
    auto_publish: true
    components:
      - content_view: Fedora CV
        content_view_version: 1.0
      - content_view: Internal CV
        latest: true
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    content_views:
      description: List of content views.
      type: list
      elements: dict
'''

import copy
from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


cvc_foreman_spec = {
    'id': {'type': 'invisible'},
    'content_view': {'type': 'entity', 'required': True},
    'latest': {'type': 'bool', 'default': False},
    'content_view_version': {'type': 'entity', 'aliases': ['version']},
}


class KatelloContentViewModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloContentViewModule(
        foreman_spec=dict(
            name=dict(required=True),
            description=dict(),
            composite=dict(type='bool', default=False),
            auto_publish=dict(type='bool', default=False),
            solve_dependencies=dict(type='bool'),
            components=dict(type='nested_list', foreman_spec=cvc_foreman_spec, resolve=False),
            repositories=dict(type='entity_list', elements='dict', resolve=False, options=dict(
                name=dict(required=True),
                product=dict(required=True),
            )),
        ),
        argument_spec=dict(
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
        mutually_exclusive=[['repositories', 'components']],
    )

    # components is None when we're managing a CCV but don't want to adjust its components
    components = module.foreman_params.pop('components', None)
    if components:
        for component in components:
            if not component['latest'] and component.get('content_view_version') is None:
                module.fail_json(msg="Content View Component must either have latest=True or provide a Content View Version.")

    with module.api_connection():
        entity = module.lookup_entity('entity')
        scope = module.scope_for('organization')

        if not module.desired_absent:
            if 'repositories' in module.foreman_params:
                if module.foreman_params['composite']:
                    module.fail_json(msg="Repositories cannot be parts of a Composite Content View.")
                else:
                    repositories = []
                    for repository in module.foreman_params['repositories']:
                        product = module.find_resource_by_name('products', repository['product'], params=scope, thin=True)
                        repositories.append(module.find_resource_by_name('repositories', repository['name'], params={'product_id': product['id']}, thin=True))
                    module.foreman_params['repositories'] = repositories

        content_view_entity = module.run()

        # only update CVC's of newly created or updated CV's that are composite if components are specified
        update_dependent_entities = (module.state == 'present' or (module.state == 'present_with_defaults' and module.changed))
        if update_dependent_entities and content_view_entity['composite'] and components is not None:
            if not module.changed:
                content_view_entity['content_view_components'] = entity['content_view_components']
            current_cvcs = content_view_entity.get('content_view_components', [])

            # only record a subset of data
            current_cvcs_record = []
            for cvc in current_cvcs:
                entry = {"id": cvc['id'], "content_view_id": cvc['content_view']['id'], "latest": cvc['latest']}
                if 'content_view_version' in cvc and isinstance(cvc['content_view_version'], dict):
                    entry['content_view_version_id'] = cvc['content_view_version'].get('id')
                current_cvcs_record.append(entry)
            module.record_before('content_views/components', {'composite_content_view_id': content_view_entity['id'],
                                                              'content_view_components': current_cvcs_record})
            final_cvcs_record = copy.deepcopy(current_cvcs_record)

            components_to_add = []
            ccv_scope = {'composite_content_view_id': content_view_entity['id']}
            for component in components:
                cvc = {
                    'content_view': module.find_resource_by_name('content_views', name=component['content_view'], params=scope),
                    'latest': component['latest'],
                }
                cvc_matched = next((item for item in current_cvcs if item['content_view']['id'] == cvc['content_view']['id']), None)
                if not cvc['latest']:
                    search = "content_view_id={0},version={1}".format(cvc['content_view']['id'], component['content_view_version'])
                    cvc['content_view_version'] = module.find_resource('content_view_versions', search=search, thin=True)
                    cvc['latest'] = False
                    if cvc_matched and cvc_matched['latest']:
                        # When changing to latest=False & version is the latest we must send 'content_view_version' to the server
                        # Let's fake, it wasn't there...
                        cvc_matched.pop('content_view_version', None)
                        cvc_matched.pop('content_view_version_id', None)
                if cvc_matched:
                    module.ensure_entity(
                        'content_view_components', cvc, cvc_matched, state='present', foreman_spec=cvc_foreman_spec, params=ccv_scope)
                    current_cvcs.remove(cvc_matched)
                else:
                    cvc['content_view_id'] = cvc.pop('content_view')['id']
                    if 'content_view_version' in cvc:
                        cvc['content_view_version_id'] = cvc.pop('content_view_version')['id']
                    components_to_add.append(cvc)

            if components_to_add:
                payload = {
                    'composite_content_view_id': content_view_entity['id'],
                    'components': components_to_add,
                }
                module.resource_action('content_view_components', 'add_components', payload)

                final_cvcs_record.extend(components_to_add)

            # desired cvcs have already been updated and removed from `current_cvcs`
            components_to_remove = [item['id'] for item in current_cvcs]
            if components_to_remove:
                payload = {
                    'composite_content_view_id': content_view_entity['id'],
                    'component_ids': components_to_remove,
                }
                module.resource_action('content_view_components', 'remove_components', payload)

                # some entries in "final" don't have an id yet, as it is only assigned on creation of a cv component,
                # which didn't happen yet when we record the data
                final_cvcs_record = [item for item in final_cvcs_record if item.get('id', 'NEW_ID') not in components_to_remove]

            module.record_after('content_views/components', {'composite_content_view_id': content_view_entity['id'],
                                                             'content_view_components': final_cvcs_record})
            module.record_after_full('content_views/components', {'composite_content_view_id': content_view_entity['id'],
                                                                  'content_view_components': final_cvcs_record})


if __name__ == '__main__':
    main()
