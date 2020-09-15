#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Baptiste AGASSE (baptiste.agasse@gmail.com)
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
module: subnet
version_added: 1.0.0
short_description: Manage Subnets
description:
  - Create, update, and delete Subnets
author:
  - "Baptiste Agasse (@bagasse)"
requirements:
  - ipaddress
options:
  name:
    description: Subnet name
    required: true
    type: str
  description:
    description: Description of the subnet
    type: str
  updated_name:
    description: New subnet name. When this parameter is set, the module will not be idempotent.
    type: str
  network_type:
    description: Subnet type
    default: IPv4
    choices: ["IPv4", "IPv6"]
    type: str
  dns_primary:
    description: Primary DNS server for this subnet
    required: false
    type: str
  dns_secondary:
    description: Secondary DNS server for this subnet
    required: false
    type: str
  domains:
    description: List of DNS domains the subnet should assigned to
    required: false
    type: list
    elements: str
  gateway:
    description: Subnet gateway IP address
    required: false
    type: str
  network:
    description: Subnet IP address
    required: true
    type: str
  cidr:
    description: CIDR prefix length; Required if I(network_type=IPv4) and no I(mask) provided
    type: int
  mask:
    description: Subnet netmask. Required if I(network_type=IPv4) and no I(cidr) prefix length provided
    type: str
  from_ip:
    description: First IP address of the host IP allocation pool
    required: false
    type: str
  to_ip:
    description: Last IP address of the host IP allocation pool
    required: false
    type: str
  boot_mode:
    description: Boot mode used by hosts in this subnet
    required: false
    default: DHCP
    choices: ["DHCP", "Static"]
    type: str
  ipam:
    description: IPAM mode for this subnet
    required: false
    default: DHCP
    choices:
      - "DHCP"
      - "Internal DB"
      - "Random DB"
      - "EUI-64"
      - "None"
    type: str
  dhcp_proxy:
    description: DHCP Smart proxy for this subnet
    required: false
    type: str
  httpboot_proxy:
    description: HTTP Boot Smart proxy for this subnet
    required: false
    type: str
  tftp_proxy:
    description: TFTP Smart proxy for this subnet
    required: false
    type: str
  discovery_proxy:
    description:
      - Discovery Smart proxy for this subnet
      - This option is only available if the discovery plugin is installed.
    required: false
    type: str
  dns_proxy:
    description: DNS Smart proxy for this subnet
    required: false
    type: str
  template_proxy:
    description: Template Smart proxy for this subnet
    required: false
    type: str
  remote_execution_proxies:
    description:
      - Remote execution Smart proxies for this subnet
      - This option is only available if the remote_execution plugin is installed.
    required: false
    type: list
    elements: str
  vlanid:
    description: VLAN ID
    required: false
    type: int
  mtu:
    description: MTU
    required: false
    type: int
  parameters:
    description:
      - Subnet specific host parameters
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
  - theforeman.foreman.foreman.nested_parameters
'''

EXAMPLES = '''
- name: My subnet
  theforeman.foreman.subnet:
    name: "My subnet"
    description: "My description"
    network: "192.168.0.0"
    mask: "255.255.255.192"
    gateway: "192.168.0.1"
    from_ip: "192.168.0.2"
    to_ip: "192.168.0.42"
    boot_mode: "Static"
    dhcp_proxy: "smart-proxy1.foo.example.com"
    tftp_proxy: "smart-proxy1.foo.example.com"
    dns_proxy: "smart-proxy2.foo.example.com"
    template_proxy: "smart-proxy2.foo.example.com"
    vlanid: 452
    mtu: 9000
    domains:
    - "foo.example.com"
    - "bar.example.com"
    organizations:
    - "Example Org"
    locations:
    - "Toulouse"
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
    subnets:
      description: List of subnets.
      type: list
      elements: dict
'''

import traceback
from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanTaxonomicEntityAnsibleModule, ParametersMixin, missing_required_lib
)
try:
    import ipaddress
    HAS_IPADDRESS = True
except ImportError:
    HAS_IPADDRESS = False
    IPADDRESS_IMP_ERR = traceback.format_exc()


class ForemanSubnetModule(ParametersMixin, ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanSubnetModule(
        argument_spec=dict(
            updated_name=dict(),
        ),
        foreman_spec=dict(
            name=dict(required=True),
            description=dict(),
            network_type=dict(choices=['IPv4', 'IPv6'], default='IPv4'),
            dns_primary=dict(),
            dns_secondary=dict(),
            domains=dict(type='entity_list'),
            gateway=dict(),
            network=dict(required=True),
            cidr=dict(type='int'),
            mask=dict(),
            from_ip=dict(flat_name='from'),
            to_ip=dict(flat_name='to'),
            boot_mode=dict(choices=['DHCP', 'Static'], default='DHCP'),
            ipam=dict(choices=['DHCP', 'Internal DB', 'Random DB', 'EUI-64', 'None'], default='DHCP'),
            dhcp_proxy=dict(type='entity', flat_name='dhcp_id', resource_type='smart_proxies'),
            httpboot_proxy=dict(type='entity', flat_name='httpboot_id', resource_type='smart_proxies'),
            tftp_proxy=dict(type='entity', flat_name='tftp_id', resource_type='smart_proxies'),
            discovery_proxy=dict(type='entity', flat_name='discovery_id', resource_type='smart_proxies'),
            dns_proxy=dict(type='entity', flat_name='dns_id', resource_type='smart_proxies'),
            template_proxy=dict(type='entity', flat_name='template_id', resource_type='smart_proxies'),
            remote_execution_proxies=dict(type='entity_list', resource_type='smart_proxies'),
            vlanid=dict(type='int'),
            mtu=dict(type='int'),
        ),
        required_plugins=[('discovery', ['discovery_proxy'])],
    )

    if not HAS_IPADDRESS:
        module.fail_json(msg=missing_required_lib("ipaddress"), exception=IPADDRESS_IMP_ERR)

    module_params = module.foreman_params

    if not module.desired_absent:
        if module_params['network_type'] == 'IPv4':
            if 'mask' not in module_params and 'cidr' not in module_params:
                module.fail_json(msg='When specifying IPv4 networks, either "mask" or "cidr" is required.')
            IPNetwork = ipaddress.IPv4Network
        else:
            IPNetwork = ipaddress.IPv6Network
        if 'mask' in module_params and 'cidr' not in module_params:
            module_params['cidr'] = IPNetwork(u'%s/%s' % (module_params['network'], module_params['mask'])).prefixlen
        elif 'mask' not in module_params and 'cidr' in module_params:
            module_params['mask'] = str(IPNetwork(u'%s/%s' % (module_params['network'], module_params['cidr'])).netmask)

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
