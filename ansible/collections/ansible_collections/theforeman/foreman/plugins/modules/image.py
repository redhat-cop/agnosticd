#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2020 Mark Hlawatschek (ATIX AG)
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
# along with This program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: image
version_added: 1.0.0
short_description: Manage Images
description:
  - Create, update, and delete Images
author:
  - "Mark Hlawatschek (@hlawatschek) ATIX AG"
options:
  name:
    description: Image name
    required: true
    type: str
  compute_resource:
    description: Compute resource the image is assigned to
    required: true
    type: str
  uuid:
    aliases:
      - image_uuid
    description: UUID or Marketplace URN of the operatingsystem image
    required: true
    type: str
  image_username:
    description: Username that is used to login into the operating system
    required: true
    type: str
  image_password:
    description: Password that is used to login into the operating system
    required: false
    type: str
  operatingsystem:
    description: Operating system that will be deployed using the image
    required: true
    type: str
  architecture:
    description: architecture of the image
    required: true
    type: str
  user_data:
    description: Image supports user_data
    required: false
    type: bool
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
'''

EXAMPLES = '''
   - name: create Image for EC2
     image:
        name: CentOS
        image_uuid: "ami-0ff760d16d9497662"
        image_username: "centos"
        operatingsystem: "CentOS 7"
        compute_resource: "AWS"
        architecture: "x86_64"
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    images:
      description: List of images.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule


class ForemanImageModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanImageModule(
        argument_spec=dict(
            image_username=dict(required=True),
            image_password=dict(no_log=True),
        ),
        foreman_spec=dict(
            name=dict(required=True),
            username=dict(type='invisible'),
            uuid=dict(required=True, aliases=['image_uuid']),
            password=dict(type='invisible', no_log=True),
            compute_resource=dict(type='entity', required=True),
            architecture=dict(type='entity', required=True),
            operatingsystem=dict(type='entity', required=True),
            user_data=dict(type='bool')
        ),
        entity_opts={'scope': ['compute_resource']},
    )

    module.foreman_params['username'] = module.foreman_params.pop('image_username')
    if 'image_password' in module.foreman_params:
        module.foreman_params['password'] = module.foreman_params.pop('image_password')
    with module.api_connection():
        scope = module.scope_for('compute_resource')
        operatingsystem_id = module.lookup_entity('operatingsystem')['id']
        module.set_entity('entity', module.find_resource(
            'images',
            search='name="{0}",operatingsystem="{1}"'.format(module.foreman_params['name'], operatingsystem_id),
            params=scope,
            failsafe=True,
        ))
        module.run()


if __name__ == '__main__':
    main()
