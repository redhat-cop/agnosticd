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
module: repository
version_added: 1.0.0
short_description: Manage Repositories
description:
  - Crate and manage repositories
author: "Eric D Helms (@ehelms)"
options:
  name:
    description:
      - Name of the repository
    required: true
    type: str
  description:
    description:
      - Description of the repository
    required: false
    type: str
  product:
    description:
      - Product to which the repository lives in
    required: true
    type: str
  label:
    description:
      - label of the repository
    type: str
  content_type:
    description:
      - The content type of the repository
    required: true
    choices:
      - deb
      - docker
      - file
      - ostree
      - puppet
      - yum
      - ansible_collection
    type: str
  url:
    description:
      - Repository URL to sync from
    required: false
    type: str
  ignore_global_proxy:
    description:
      - Whether content sync should use or ignore the global http proxy setting
      - This is deprecated with Katello 3.13
      - It has been superseeded by I(http_proxy_policy)
    required: false
    type: bool
  http_proxy_policy:
    description:
      - Which proxy to use for content synching
    choices:
      - global_default_http_proxy
      - none
      - use_selected_http_proxy
    required: false
    type: str
  http_proxy:
    description:
      - Name of the http proxy to use for content synching
      - Should be combined with I(http_proxy_policy='use_selected_http_proxy')
    required: false
    type: str
  gpg_key:
    description:
    - Repository GPG key
    required: false
    type: str
  ssl_ca_cert:
    description:
    - Repository SSL CA certificate
    required: false
    type: str
  ssl_client_cert:
    description:
    - Repository SSL client certificate
    required: false
    type: str
  ssl_client_key:
    description:
    - Repository SSL client private key
    required: false
    type: str
  download_policy:
    description:
      - download policy for sync from upstream
    choices:
      - background
      - immediate
      - on_demand
    required: false
    type: str
  mirror_on_sync:
    description:
      - toggle "mirror on sync" where the state of the repository mirrors that of the upstream repository at sync time
    default: true
    type: bool
    required: false
  verify_ssl_on_sync:
    description:
      - verify the upstream certifcates are signed by a trusted CA
    type: bool
    required: false
  upstream_username:
    description:
      - username to access upstream repository
    type: str
  upstream_password:
    description:
      - password to access upstream repository
    type: str
  docker_upstream_name:
    description:
      - name of the upstream docker repository
      - only available for I(content_type=docker)
    type: str
  docker_tags_whitelist:
    description:
      - list of tags to sync for Container Image repository
      - only available for I(content_type=docker)
    type: list
    elements: str
  deb_releases:
    description:
      - comma separated list of releases to be synced from deb-archive
      - only available for I(content_type=deb)
    type: str
  deb_components:
    description:
      - comma separated list of repo components to be synced from deb-archive
      - only available for I(content_type=deb)
    type: str
  deb_architectures:
    description:
      - comma separated list of architectures to be synced from deb-archive
      - only available for I(content_type=deb)
    type: str
  deb_errata_url:
    description:
      - URL to sync Debian or Ubuntu errata information from
      - only available on Orcharhino
      - only available for I(content_type=deb)
    type: str
    required: false
  unprotected:
    description:
      - publish the repository via HTTP
    type: bool
    required: false
  checksum_type:
    description:
      - Checksum of the repository
    type: str
    required: false
    choices:
      - sha1
      - sha256
  ignorable_content:
    description:
      - List of content units to ignore while syncing a yum repository.
      - Must be subset of rpm,drpm,srpm,distribution,erratum.
    type: list
    elements: str
    required: false
  ansible_collection_requirements:
    description:
      - Contents of requirement yaml file to sync from URL
    type: str
    required: false
  auto_enabled:
    description:
      - repositories will be automatically enabled on a registered host subscribed to this product
    type: bool
    required: false
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Create repository"
  theforeman.foreman.repository:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My repository"
    state: present
    content_type: "yum"
    product: "My Product"
    organization: "Default Organization"
    url: "http://yum.theforeman.org/plugins/latest/el7/x86_64/"
    mirror_on_sync: true
    download_policy: background

- name: "Create repository with content credentials"
  theforeman.foreman.repository:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My repository 2"
    state: present
    content_type: "yum"
    product: "My Product"
    organization: "Default Organization"
    url: "http://yum.theforeman.org/releases/latest/el7/x86_64/"
    download_policy: background
    mirror_on_sync: true
    gpg_key: RPM-GPG-KEY-my-product2
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    repositories:
      description: List of repositories.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


class KatelloRepositoryModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloRepositoryModule(
        foreman_spec=dict(
            product=dict(type='entity', scope=['organization'], required=True),
            label=dict(),
            name=dict(required=True),
            content_type=dict(required=True, choices=['docker', 'ostree', 'yum', 'puppet', 'file', 'deb', 'ansible_collection']),
            url=dict(),
            ignore_global_proxy=dict(type='bool'),
            http_proxy_policy=dict(choices=['global_default_http_proxy', 'none', 'use_selected_http_proxy']),
            http_proxy=dict(type='entity'),
            gpg_key=dict(type='entity', resource_type='content_credentials', scope=['organization']),
            ssl_ca_cert=dict(type='entity', resource_type='content_credentials', scope=['organization']),
            ssl_client_cert=dict(type='entity', resource_type='content_credentials', scope=['organization']),
            ssl_client_key=dict(type='entity', resource_type='content_credentials', scope=['organization']),
            download_policy=dict(choices=['background', 'immediate', 'on_demand']),
            mirror_on_sync=dict(type='bool', default=True),
            verify_ssl_on_sync=dict(type='bool'),
            upstream_username=dict(),
            upstream_password=dict(no_log=True),
            docker_upstream_name=dict(),
            docker_tags_whitelist=dict(type='list', elements='str'),
            deb_errata_url=dict(),
            deb_releases=dict(),
            deb_components=dict(),
            deb_architectures=dict(),
            description=dict(),
            unprotected=dict(type='bool'),
            checksum_type=dict(choices=['sha1', 'sha256']),
            ignorable_content=dict(type='list', elements='str'),
            ansible_collection_requirements=dict(),
            auto_enabled=dict(type='bool'),
        ),
        argument_spec=dict(
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
        entity_opts={'scope': ['product']},
    )

    if module.foreman_params['content_type'] != 'docker':
        invalid_list = [key for key in ['docker_upstream_name', 'docker_tags_whitelist'] if key in module.foreman_params]
        if invalid_list:
            module.fail_json(msg="({0}) can only be used with content_type 'docker'".format(",".join(invalid_list)))

    if module.foreman_params['content_type'] != 'deb':
        invalid_list = [key for key in ['deb_errata_url', 'deb_releases', 'deb_components', 'deb_architectures'] if key in module.foreman_params]
        if invalid_list:
            module.fail_json(msg="({0}) can only be used with content_type 'deb'".format(",".join(invalid_list)))

    if module.foreman_params['content_type'] != 'ansible_collection':
        invalid_list = [key for key in ['ansible_collection_requirements'] if key in module.foreman_params]
        if invalid_list:
            module.fail_json(msg="({0}) can only be used with content_type 'ansible_collection'".format(",".join(invalid_list)))

    if module.foreman_params['content_type'] != 'yum':
        invalid_list = [key for key in ['ignorable_content'] if key in module.foreman_params]
        if invalid_list:
            module.fail_json(msg="({0}) can only be used with content_type 'yum'".format(",".join(invalid_list)))

    if 'ignore_global_proxy' in module.foreman_params and 'http_proxy_policy' not in module.foreman_params:
        module.foreman_params['http_proxy_policy'] = 'none' if module.foreman_params['ignore_global_proxy'] else 'global_default_http_proxy'

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
