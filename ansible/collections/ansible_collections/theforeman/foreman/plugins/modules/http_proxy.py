#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2020 Evgeni Golov
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
module: http_proxy
version_added: 1.1.0
short_description: Manage HTTP Proxies
description:
  - Create, update, and delete HTTP Proxies
author:
  - "Evgeni Golov (@evgeni)"
options:
  name:
    description:
      - The HTTP Proxy name
    required: true
    type: str
  url:
    description:
      - URL of the HTTP Proxy
      - Required when creating a new HTTP Proxy.
    required: False
    type: str
  proxy_username:
    description:
      - Username used to authenticate with the HTTP Proxy
    required: False
    type: str
  proxy_password:
    description:
      - Password used to authenticate with the HTTP Proxy
      - When this parameter is set, the module will not be idempotent.
    required: False
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
- name: create example.org proxy
  theforeman.foreman.http_proxy:
    name: "example.org"
    url: "http://example.org:3128"
    locations:
      - "Munich"
    organizations:
      - "ACME"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    http_proxies:
      description: List of HTTP proxies.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule


class ForemanHttpProxyModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanHttpProxyModule(
        foreman_spec=dict(
            name=dict(required=True),
            url=dict(),
            proxy_username=dict(flat_name='username'),
            proxy_password=dict(no_log=True, flat_name='password'),
        ),
    )

    with module.api_connection():
        entity = module.lookup_entity('entity')

        if not module.desired_absent:
            if 'url' not in module.foreman_params:
                if not entity:
                    module.fail_json(msg="The 'url' parameter is required when creating a new HTTP Proxy.")
                else:
                    module.foreman_params['url'] = entity['url']

        module.run()


if __name__ == '__main__':
    main()
