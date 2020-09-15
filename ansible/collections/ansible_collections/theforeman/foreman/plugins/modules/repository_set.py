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
module: repository_set
version_added: 1.0.0
short_description: Enable/disable Repositories in Repository Sets
description:
  - Enable/disable repositories in repository sets
author: "Andrew Kofink (@akofink)"
options:
  name:
    description:
      - Name of the repository set
    required: false
    type: str
  product:
    description:
      - Name of the parent product
    required: false
    type: str
  label:
    description:
      - Label of the repository set, can be used in place of I(name) & I(product)
    required: false
    type: str
  repositories:
    description:
      - Release version and base architecture of the repositories to enable.
      - Some reposotory sets require only I(basearch) or only I(releasever) to be set.
      - See the examples how you can obtain this information using M(theforeman.foreman.resource_info).
      - Required when I(all_repositories) is unset or C(false).
    required: false
    type: list
    elements: dict
    suboptions:
      basearch:
        description:
          - Basearch of the repository to enable.
        type: str
      releasever:
        description:
          - Releasever of the repository to enable.
        type: str
  all_repositories:
    description:
      - Affect all available repositories in the repository set instead of listing them in I(repositories).
      - Required when I(repositories) is unset or an empty list.
    required: false
    type: bool
  state:
    description:
      - Whether the repositories are enabled or not
    required: false
    choices:
      - 'enabled'
      - 'disabled'
    default: enabled
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Enable RHEL 7 RPMs repositories"
  theforeman.foreman.repository_set:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Red Hat Enterprise Linux 7 Server (RPMs)"
    organization: "Default Organization"
    product: "Red Hat Enterprise Linux Server"
    repositories:
    - releasever: "7.0"
      basearch: "x86_64"
    - releasever: "7.1"
      basearch: "x86_64"
    - releasever: "7.2"
      basearch: "x86_64"
    - releasever: "7.3"
      basearch: "x86_64"
    state: enabled

- name: "Enable RHEL 7 RPMs repositories with label"
  theforeman.foreman.repository_set:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    label: rhel-7-server-rpms
    repositories:
    - releasever: "7.0"
      basearch: "x86_64"
    - releasever: "7.1"
      basearch: "x86_64"
    - releasever: "7.2"
      basearch: "x86_64"
    - releasever: "7.3"
      basearch: "x86_64"
    state: enabled

- name: "Disable RHEL 7 Extras RPMs repository"
  theforeman.foreman.repository_set:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: Red Hat Enterprise Linux 7 Server - Extras (RPMs)
    organization: "Default Organization"
    product: Red Hat Enterprise Linux Server
    state: disabled
    repositories:
      - basearch: x86_64

- name: "Enable RHEL 8 BaseOS RPMs repository with label"
  theforeman.foreman.repository_set:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    label: rhel-8-for-x86_64-baseos-rpms
    repositories:
      - releasever: "8"

- name: "Enable Red Hat Virtualization Manager RPMs repository with label"
  theforeman.foreman.repository_set:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    label: "rhel-7-server-rhv-4.2-manager-rpms"
    repositories:
      - basearch: x86_64
    state: enabled

- name: "Enable Red Hat Virtualization Manager RPMs repository without specifying basearch"
  theforeman.foreman.repository_set:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    label: "rhel-7-server-rhv-4.2-manager-rpms"
    all_repositories: true
    state: enabled

- name: "Search for possible repository sets of a product"
  theforeman.foreman.resource_info:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    resource: repository_sets
    search: product_name="Red Hat Virtualization Manager"
  register: data
- name: "Output found repository sets, see the contentUrl section for possible repository substitutions"
  debug:
    var: data

- name: "Search for possible repository sets by label"
  theforeman.foreman.resource_info:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    resource: repository_sets
    search: label=rhel-7-server-rhv-4.2-manager-rpms
  register: data
- name: "Output found repository sets, see the contentUrl section for possible repository substitutions"
  debug:
    var: data

- name: Enable set with and without all_repositories at the same time
  theforeman.foreman.repository_set:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    label: "{{ item.label }}"
    repositories: "{{ item.repositories | default(omit) }}"
    all_repositories: "{{ item.repositories is not defined }}"
    state: enabled
  loop:
    - label: rhel-7-server-rpms
      repositories:
        - releasever: "7Server"
          basearch: "x86_64"
    - label: rhel-7-server-rhv-4.2-manager-rpms
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    repository_sets:
      description: List of repository sets.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


def get_desired_repos(desired_substitutions, available_repos):
    desired_repos = []
    for sub in desired_substitutions:
        desired_repos += filter(lambda available: available['substitutions'] == sub, available_repos)
    return desired_repos


def record_repository_set_state(module, record_data, repo, state_before, state_after):
    repo_change_data = record_data.copy()
    repo_change_data['repo_name'] = repo
    repo_change_data['state'] = state_before
    repo_change_data_after = repo_change_data.copy()
    repo_change_data_after['state'] = state_after
    module.record_before('repository_sets', repo_change_data)
    module.record_after('repository_sets', repo_change_data_after)
    module.record_after_full('repository_sets', repo_change_data_after)


class KatelloRepositorySetModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloRepositorySetModule(
        foreman_spec=dict(
            product=dict(type='entity', scope=['organization']),
            name=dict(),
            label=dict(),
            repositories=dict(type='list', elements='dict', options=dict(
                basearch=dict(),
                releasever=dict(),
            )),
            all_repositories=dict(type='bool'),
        ),
        argument_spec=dict(
            state=dict(default='enabled', choices=['disabled', 'enabled']),
        ),
        required_one_of=[
            ['label', 'name'],
            ['repositories', 'all_repositories'],
        ],
        required_if=[
            ['all_repositories', False, ['repositories']],
            ['repositories', [], ['all_repositories']],
        ],
    )

    repositories = [{k: v for (k, v) in sub.items() if v is not None} for sub in module.foreman_params.get('repositories', [])]

    with module.api_connection():
        scope = module.scope_for('organization')

        record_data = {}
        if 'product' in module.foreman_params:
            record_data['product'] = module.foreman_params['product']
            scope.update(module.scope_for('product'))

        if 'label' in module.foreman_params:
            search = 'label="{0}"'.format(module.foreman_params['label'])
            repo_set = module.find_resource('repository_sets', search=search, params=scope)
            record_data['label'] = module.foreman_params['label']
        else:
            repo_set = module.find_resource_by_name('repository_sets', name=module.foreman_params['name'], params=scope)
            record_data['name'] = module.foreman_params['name']
        module.set_entity('entity', repo_set)

        repo_set_scope = {'id': repo_set['id'], 'product_id': repo_set['product']['id']}
        repo_set_scope.update(scope)

        available_repos = module.resource_action('repository_sets', 'available_repositories', params=repo_set_scope, ignore_check_mode=True)
        available_repos = available_repos['results']
        current_repos = repo_set['repositories']
        if not module.foreman_params.get('all_repositories', False):
            desired_repos = get_desired_repos(repositories, available_repos)
        else:
            desired_repos = available_repos[:]

        current_repo_names = set(map(lambda repo: repo['name'], current_repos))
        desired_repo_names = set(map(lambda repo: repo['repo_name'], desired_repos))

        if not module.foreman_params.get('all_repositories', False) and len(repositories) != len(desired_repo_names):
            repo_set_identification = ' '.join(['{0}: {1}'.format(k, v) for (k, v) in record_data.items()])

            available_repo_details = [{'name': repo['repo_name'], 'repositories': repo['substitutions']} for repo in available_repos]
            desired_repo_details = [{'name': repo['repo_name'], 'repositories': repo['substitutions']} for repo in desired_repos]
            search_details = record_data.copy()
            search_details['repositories'] = repositories

            error_msg = "Desired repositories are not available on the repository set {0}.\nSearched: {1}\nFound: {2}\nAvailable: {3}".format(
                        repo_set_identification, search_details, desired_repo_details, available_repo_details)

            module.fail_json(msg=error_msg)

        if module.state == 'enabled':
            for repo in desired_repo_names - current_repo_names:
                repo_to_enable = next((r for r in available_repos if r['repo_name'] == repo))
                repo_change_params = repo_to_enable['substitutions'].copy()
                repo_change_params.update(repo_set_scope)

                record_repository_set_state(module, record_data, repo, 'disabled', 'enabled')

                module.resource_action('repository_sets', 'enable', params=repo_change_params)
        elif module.state == 'disabled':
            for repo in current_repo_names & desired_repo_names:
                repo_to_disable = next((r for r in available_repos if r['repo_name'] == repo))
                repo_change_params = repo_to_disable['substitutions'].copy()
                repo_change_params.update(repo_set_scope)

                record_repository_set_state(module, record_data, repo, 'enabled', 'disabled')

                module.resource_action('repository_sets', 'disable', params=repo_change_params)


if __name__ == '__main__':
    main()
