#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) Philipp Joos 2017
# (c) Baptiste Agasse 2019
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
module: compute_profile
version_added: 1.0.0
short_description: Manage Compute Profiles
description:
  - Create, update, and delete Compute Profiles
author:
  - "Philipp Joos (@philippj)"
  - "Baptiste Agasse (@bagasse)"
options:
  name:
    description: compute profile name
    required: true
    type: str
  updated_name:
    description: new compute profile name
    required: false
    type: str
  compute_attributes:
    description: Compute attributes related to this compute profile. Some of these attributes are specific to the underlying compute resource type
    required: false
    type: list
    elements: dict
    suboptions:
      compute_resource:
        description:
          - Name of the compute resource the attribute should be for
        type: str
      vm_attrs:
        description:
          - Hash containing the data of vm_attrs
        aliases:
          - vm_attributes
        type: dict
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
'''

EXAMPLES = '''
- name: compute profile
  theforeman.foreman.compute_profile:
    name: example_compute_profile
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: present

- name: another compute profile
  theforeman.foreman.compute_profile:
    name: another_example_compute_profile
    compute_attributes:
    - compute_resource: ovirt_compute_resource1
      vm_attrs:
        cluster: 'a96d44a4-f14a-1015-82c6-f80354acdf01'
        template: 'c88af4b7-a24a-453b-9ac2-bc647ca2ef99'
        instance_type: 'cb8927e7-a404-40fb-a6c1-06cbfc92e077'
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: present

- name: compute profile2
  theforeman.foreman.compute_profile:
    name: example_compute_profile2
    compute_attributes:
    - compute_resource: ovirt_compute_resource01
      vm_attrs:
        cluster: a96d44a4-f14a-1015-82c6-f80354acdf01
        cores: 1
        sockets: 1
        memory: 1073741824
        ha: 0
        interfaces_attributes:
          0:
            name: ""
            network: 390666e1-dab3-4c99-9f96-006b2e2fd801
            interface: virtio
        volumes_attributes:
          0:
            size_gb: 16
            storage_domain: 19c50090-1ab4-4023-a63f-75ee1018ed5e
            preallocate: '1'
            wipe_after_delete: '0'
            interface: virtio_scsi
            bootable: 'true'
    - compute_resource: libvirt_compute_resource03
      vm_attrs:
        cpus: 1
        memory: 2147483648
        nics_attributes:
          0:
            type: bridge
            bridge: ""
            model: virtio
        volumes_attributes:
          0:
            pool_name: default
            capacity: 16G
            allocation: 16G
            format_type: raw
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: present

- name: Remove compute profile
  theforeman.foreman.compute_profile:
    name: example_compute_profile2
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: absent
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    compute_profiles:
      description: List of compute profiles.
      type: list
      elements: dict
      contains:
        id:
          description: Database id of the compute profile.
          type: int
        name:
          description: Name of the compute profile.
          type: str
        compute_attributes:
          description: Attributes for this compute profile.
          type: list
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule


compute_attribute_foreman_spec = {
    'compute_resource': {'type': 'entity'},
    'vm_attrs': {'type': 'dict', 'aliases': ['vm_attributes']},
}


class ForemanComputeProfileModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanComputeProfileModule(
        foreman_spec=dict(
            name=dict(required=True),
            compute_attributes=dict(type='nested_list', foreman_spec=compute_attribute_foreman_spec),
        ),
        argument_spec=dict(
            updated_name=dict(),
        ),
    )

    compute_attributes = module.foreman_params.pop('compute_attributes', None)

    with module.api_connection():
        entity = module.run()

        # Apply changes on underlying compute attributes only when present
        if entity and module.state == 'present' and compute_attributes is not None:
            # Update or create compute attributes
            scope = {'compute_profile_id': entity['id']}
            for ca_module_params in compute_attributes:
                ca_module_params['compute_resource'] = module.find_resource_by_name(
                    'compute_resources', name=ca_module_params['compute_resource'], failsafe=False, thin=False)
                ca_entities = ca_module_params['compute_resource'].get('compute_attributes', [])
                ca_entity = next((item for item in ca_entities if item.get('compute_profile_id') == entity['id']), None)
                module.ensure_entity('compute_attributes', ca_module_params, ca_entity, foreman_spec=compute_attribute_foreman_spec, params=scope)


if __name__ == '__main__':
    main()
