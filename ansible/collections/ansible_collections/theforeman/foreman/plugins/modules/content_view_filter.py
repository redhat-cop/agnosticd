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
module: content_view_filter
version_added: 1.0.0
short_description: Manage Content View Filters
description:
    - Create and manage content View filters
author: "Sean O'Keeffe (@sean797)"
options:
  architecture:
    description:
      - package architecture
    type: str
  name:
    description:
      - Name of the Content View Filter
    type: str
    required: true
  description:
    description:
      - Description of the Content View Filter
    type: str
  content_view:
    description:
      - Name of the content view
    required: true
    type: str
  filter_state:
    description:
      - State of the content view filter
    default: present
    choices:
      - present
      - absent
    type: str
  repositories:
    description:
      - List of repositories that include name and product
      - An empty Array means all current and future repositories
    default: []
    type: list
    elements: dict
  rule_state:
    description:
      - State of the content view filter rule
    default: present
    choices:
      - present
      - absent
    type: str
  filter_type:
    description:
      - Content view filter type
    required: true
    choices:
      - rpm
      - package_group
      - erratum
      - docker
    type: str
  rule_name:
    description:
      - Content view filter rule name or package name
      - If omitted, the value of I(name) will be used if necessary
    aliases:
      - package_name
      - package_group
      - tag
    type: str
  date_type:
    description:
      - Search using the 'Issued On' or 'Updated On'
      - Only valid on I(filter_type=erratum).
    default: updated
    choices:
      - issued
      - updated
    type: str
  end_date:
    description:
      - erratum end date (YYYY-MM-DD)
    type: str
  start_date:
    description:
      - erratum start date (YYYY-MM-DD)
    type: str
  errata_id:
    description:
      - erratum id
    type: str
  max_version:
    description:
      - package maximum version
    type: str
  min_version:
    description:
      - package minimum version
    type: str
  types:
    description:
      - erratum types (enhancement, bugfix, security)
    default: ["bugfix", "enhancement", "security"]
    type: list
    elements: str
  version:
    description:
      - package version
    type: str
  inclusion:
    description:
      - Create an include filter
    default: False
    type: bool
  original_packages:
    description:
      - Include all RPMs with no errata
    type: bool
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: Exclude csh
  theforeman.foreman.content_view_filter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "package filter 1"
    organization: "Default Organization"
    content_view: Web Servers
    filter_type: "rpm"
    package_name: tcsh

- name: Include newer csh versions
  theforeman.foreman.content_view_filter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "package filter 1"
    organization: "Default Organization"
    content_view: Web Servers
    filter_type: "rpm"
    package_name: tcsh
    min_version: 6.20.00
    inclusion: True
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    content_view_filters:
      description: List of content view filters.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloMixin, ForemanStatelessEntityAnsibleModule

content_filter_spec = {
    'id': {},
    'name': {},
    'description': {},
    'repositories': {'type': 'entity_list'},
    'inclusion': {},
    'content_view': {'type': 'entity'},
    'filter_type': {'flat_name': 'type'},
    'original_packages': {},
}

content_filter_rule_erratum_spec = {
    'id': {},
    'date_type': {},
    'end_date': {},
    'start_date': {},
    'types': {'type': 'list'},
}

content_filter_rule_erratum_id_spec = {
    'id': {},
    'errata_id': {},
    'date_type': {},
}

content_filter_rule_rpm_spec = {
    'id': {},
    'rule_name': {'flat_name': 'name'},
    'end_date': {},
    'max_version': {},
    'min_version': {},
    'version': {},
    'architecture': {},
}

content_filter_rule_package_group_spec = {
    'id': {},
    'rule_name': {'flat_name': 'name'},
    'uuid': {},
}

content_filter_rule_docker_spec = {
    'id': {},
    'rule_name': {'flat_name': 'name'},
}


class KatelloContentViewFilterModule(KatelloMixin, ForemanStatelessEntityAnsibleModule):
    pass


def main():
    module = KatelloContentViewFilterModule(
        foreman_spec=dict(
            name=dict(required=True),
            description=dict(),
            repositories=dict(type='list', default=[], elements='dict'),
            inclusion=dict(type='bool', default=False),
            original_packages=dict(type='bool'),
            content_view=dict(type='entity', scope=['organization'], required=True),
            filter_type=dict(required=True, choices=['rpm', 'package_group', 'erratum', 'docker']),
            filter_state=dict(default='present', choices=['present', 'absent']),
            rule_state=dict(default='present', choices=['present', 'absent']),
            rule_name=dict(aliases=['package_name', 'package_group', 'tag']),
            date_type=dict(default='updated', choices=['issued', 'updated']),
            end_date=dict(),
            errata_id=dict(),
            max_version=dict(),
            min_version=dict(),
            start_date=dict(),
            types=dict(default=["bugfix", "enhancement", "security"], type='list', elements='str'),
            version=dict(),
            architecture=dict(),
        ),
        entity_opts=dict(scope=['content_view']),
    )

    filter_state = module.foreman_params.pop('filter_state')
    rule_state = module.foreman_params.pop('rule_state')

    if module.foreman_params['filter_type'] == 'erratum':
        module.foreman_params['rule_name'] = None
    elif 'rule_name' not in module.foreman_params:
        module.foreman_params['rule_name'] = module.foreman_params['name']

    with module.api_connection():
        scope = module.scope_for('organization')

        cv_scope = module.scope_for('content_view')
        if module.foreman_params['repositories']:
            repositories = []
            for repo in module.foreman_params['repositories']:
                product = module.find_resource_by_name('products', repo['product'], params=scope, thin=True)
                product_scope = {'product_id': product['id']}
                repositories.append(module.find_resource_by_name('repositories', repo['name'], params=product_scope, thin=True))
            module.foreman_params['repositories'] = repositories

        entity = module.lookup_entity('entity')
        content_view_filter = module.ensure_entity(
            'content_view_filters',
            module.foreman_params,
            entity,
            params=cv_scope,
            state=filter_state,
            foreman_spec=content_filter_spec,
        )

        if content_view_filter is not None:
            cv_filter_scope = {'content_view_filter_id': content_view_filter['id']}
            if 'errata_id' in module.foreman_params:
                # should we try to find the errata the user is asking for? or just pass it blindly?
                # errata = module.find_resource('errata', 'id={0}'.format(module.foreman_params['errata_id']), params=scope)
                rule_spec = content_filter_rule_erratum_id_spec
                search_scope = {'errata_id': module.foreman_params['errata_id']}
                search_scope.update(cv_filter_scope)
                search = None
            else:
                rule_spec = globals()['content_filter_rule_%s_spec' % (module.foreman_params['filter_type'])]
                search_scope = cv_filter_scope
                if module.foreman_params['rule_name'] is not None:
                    search = 'name="{0}"'.format(module.foreman_params['rule_name'])
                else:
                    search = None
            # not using find_resource_by_name here, because not all filters (errata) have names
            content_view_filter_rule = module.find_resource('content_view_filter_rules', search, params=search_scope, failsafe=True) if entity else None

            if module.foreman_params['filter_type'] == 'package_group':
                package_group = module.find_resource_by_name('package_groups', module.foreman_params['rule_name'], params=scope)
                module.foreman_params['uuid'] = package_group['uuid']

            # drop 'name' from the dict, as otherwise it might override 'rule_name'
            rule_dict = module.foreman_params.copy()
            rule_dict.pop('name', None)

            module.ensure_entity(
                'content_view_filter_rules',
                rule_dict,
                content_view_filter_rule,
                params=cv_filter_scope,
                state=rule_state,
                foreman_spec=rule_spec,
            )


if __name__ == '__main__':
    main()
