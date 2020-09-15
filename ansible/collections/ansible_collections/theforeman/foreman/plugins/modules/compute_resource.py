#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) Philipp Joos 2017
# (c) Baptiste Agasse 2019
# (c) Mark Hlawatschek 2020
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
module: compute_resource
version_added: 1.0.0
short_description: Manage Compute Resources
description:
  - Create, update, and delete Compute Resources
author:
  - "Philipp Joos (@philippj)"
  - "Baptiste Agasse (@bagasse)"
  - "Manisha Singhal (@Manisha15) ATIX AG"
  - "Mark Hlawatschek (@hlawatschek) ATIX AG"
options:
  name:
    description: compute resource name
    required: true
    type: str
  updated_name:
    description: new compute resource name
    required: false
    type: str
  description:
    description: compute resource description
    required: false
    type: str
  provider:
    description: Compute resource provider. Required if I(state=present_with_defaults).
    required: false
    choices: ["vmware", "libvirt", "ovirt", "proxmox", "EC2", "AzureRm", "GCE"]
    type: str
  provider_params:
    description: Parameter specific to compute resource provider. Required if I(state=present_with_defaults).
    required: false
    type: dict
    suboptions:
      url:
        description:
          - URL of the compute resource
        type: str
      user:
        description:
          - Username for the compute resource connection, not valid for I(provider=libvirt)
        type: str
      password:
        description:
          - Password for the compute resource connection, not valid for I(provider=libvirt)
        type: str
      region:
        description:
          - AWS region, AZURE region
        type: str
      tenant:
        description:
          - AzureRM tenant
        type: str
      app_ident:
        description:
          - AzureRM client id
        type: str
      datacenter:
        description:
          - Datacenter the compute resource is in, not valid for I(provider=libvirt)
        type: str
      display_type:
        description:
          - Display type to use for the remote console, only valid for I(provider=libvirt)
        type: str
      use_v4:
        description:
          - Use oVirt API v4, only valid for I(provider=ovirt)
        type: bool
      ovirt_quota:
        description:
          - oVirt quota ID, only valid for I(provider=ovirt)
        type: str
      project:
        description:
          - Project id for I(provider=GCE)
        type: str
      email:
        description:
          - Email for I(provider=GCE)
        type: str
      key_path:
        description:
          - Certificate path for I(provider=GCE)
        type: str
      zone:
        description:
          - zone for I(provider=GCE)
        type: str
      ssl_verify_peer:
        description:
          - verify ssl from provider I(provider=proxmox)
        type: bool
      caching_enabled:
        description:
          - enable caching for I(provider=vmware)
        type: bool
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
- name: Create livirt compute resource
  theforeman.foreman.compute_resource:
    name: example_compute_resource
    locations:
      - Munich
    organizations:
      - ACME
    provider: libvirt
    provider_params:
      url: libvirt.example.com
      display_type: vnc
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: present

- name: Update libvirt compute resource
  theforeman.foreman.compute_resource:
    name: example_compute_resource
    description: updated compute resource
    locations:
      - Munich
    organizations:
      - ACME
    provider: libvirt
    provider_params:
      url: libvirt.example.com
      display_type: vnc
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: present

- name: Delete libvirt compute resource
  theforeman.foreman.compute_resource:
    name: example_compute_resource
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: absent

- name: Create vmware compute resource
  theforeman.foreman.compute_resource:
    name: example_compute_resource
    locations:
      - Munich
    organizations:
      - ACME
    provider: vmware
    provider_params:
      caching_enabled: false
      url: vsphere.example.com
      user: admin
      password: secret
      datacenter: ax01
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: present

- name: Create ovirt compute resource
  theforeman.foreman.compute_resource:
    name: ovirt_compute_resource
    locations:
      - France/Toulouse
    organizations:
      - Example Org
    provider: ovirt
    provider_params:
      url: ovirt.example.com
      user: ovirt-admin@example.com
      password: ovirtsecret
      datacenter: aa92fb54-0736-4066-8fa8-b8b9e3bd75ac
      ovirt_quota: 24868ab9-c2a1-47c3-87e7-706f17d215ac
      use_v4: true
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: present

- name: Create proxmox compute resource
  theforeman.foreman.compute_resource:
    name: proxmox_compute_resource
    locations:
      - Munich
    organizations:
      - ACME
    provider: proxmox
    provider_params:
      url: https://proxmox.example.com:8006/api2/json
      user: root@pam
      password: secretpassword
      ssl_verify_peer: true
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: present

- name: create EC2 compute resource
  theforeman.foreman.compute_resource:
    name: EC2_compute_resource
    description: EC2
    locations:
      - AWS
    organizations:
      - ACME
    provider: EC2
    provider_params:
      user: AWS_ACCESS_KEY
      password: AWS_SECRET_KEY
      region: eu-west-1
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: present

- name: create Azure compute resource
  theforeman.foreman.compute_resource:
    name: AzureRm_compute_resource
    description: AzureRm
    locations:
      - Azure
    organizations:
      - ACME
    provider: AzureRm
    provider_params:
      user: SUBSCRIPTION_ID
      tenant: TENANT_ID
      app_ident: CLIENT_ID
      password: CLIENT_SECRET
      region: westeurope
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: present

- name: create GCE compute resource
  theforeman.foreman.compute_resource:
    name: GCE compute resource
    description: Google Cloud Engine
    locations:
      - GCE
    organizations:
      - ACME
    provider: GCE
    provider_params:
      project: orcharhino
      email: myname@atix.de
      key_path: "/usr/share/foreman/gce_orcharhino_key.json"
      zone: europe-west3-b
    server_url: "https://foreman.example.com"
    username: admin
    password: secret
    state: present

'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    compute_resources:
      description: List of compute resources.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule


def get_provider_info(provider):
    provider_name = provider.lower()

    if provider_name == 'libvirt':
        return 'Libvirt', ['url', 'display_type']

    elif provider_name == 'ovirt':
        return 'Ovirt', ['url', 'user', 'password', 'datacenter', 'use_v4', 'ovirt_quota']

    elif provider_name == 'proxmox':
        return 'Proxmox', ['url', 'user', 'password', 'ssl_verify_peer']

    elif provider_name == 'vmware':
        return 'Vmware', ['url', 'user', 'password', 'datacenter', 'caching_enabled']

    elif provider_name == 'ec2':
        return 'EC2', ['user', 'password', 'region']

    elif provider_name == 'azurerm':
        return 'AzureRm', ['user', 'password', 'tenant', 'region', 'app_ident']

    elif provider_name == 'gce':
        return 'GCE', ['project', 'email', 'key_path', 'zone']

    else:
        return '', []


class ForemanComputeResourceModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanComputeResourceModule(
        foreman_spec=dict(
            name=dict(required=True),
            updated_name=dict(),
            description=dict(),
            provider=dict(choices=['vmware', 'libvirt', 'ovirt', 'proxmox', 'EC2', 'AzureRm', 'GCE']),
            display_type=dict(type='invisible'),
            datacenter=dict(type='invisible'),
            url=dict(type='invisible'),
            caching_enabled=dict(type='invisible'),
            user=dict(type='invisible'),
            password=dict(type='invisible'),
            region=dict(type='invisible'),
            tenant=dict(type='invisible'),
            app_ident=dict(type='invisible'),
            use_v4=dict(type='invisible'),
            ovirt_quota=dict(type='invisible'),
            project=dict(type='invisible'),
            email=dict(type='invisible'),
            key_path=dict(type='invisible'),
            zone=dict(type='invisible'),
            ssl_verify_peer=dict(type='invisible'),
        ),
        argument_spec=dict(
            provider_params=dict(type='dict', options=dict(
                url=dict(),
                display_type=dict(),
                user=dict(),
                password=dict(no_log=True),
                region=dict(),
                tenant=dict(),
                app_ident=dict(),
                datacenter=dict(),
                caching_enabled=dict(type='bool'),
                use_v4=dict(type='bool'),
                ovirt_quota=dict(),
                project=dict(),
                email=dict(),
                key_path=dict(),
                zone=dict(),
                ssl_verify_peer=dict(type='bool'),
            )),
            state=dict(type='str', default='present', choices=['present', 'absent', 'present_with_defaults']),
        ),
        required_if=(
            ['state', 'present_with_defaults', ['provider', 'provider_params']],
        ),
    )

    if not module.desired_absent:
        if 'provider' in module.foreman_params:
            module.foreman_params['provider'], provider_param_keys = get_provider_info(provider=module.foreman_params['provider'])
            provider_params = {k: v for k, v in module.foreman_params.pop('provider_params', dict()).items() if v is not None}

            for key in provider_param_keys:
                if key in provider_params:
                    module.foreman_params[key] = provider_params.pop(key)
            if provider_params:
                module.fail_json(msg="Provider {0} does not support the following given parameters: {1}".format(
                    module.foreman_params['provider'], list(provider_params.keys())))

    with module.api_connection():
        entity = module.lookup_entity('entity')
        if not module.desired_absent and 'provider' not in module.foreman_params and entity is None:
            module.fail_json(msg='To create a compute resource a valid provider must be supplied')

        module.run()


if __name__ == '__main__':
    main()
