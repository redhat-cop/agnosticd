#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Manisha Singhal (ATIX AG)
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
module: scc_product
version_added: 1.0.0
short_description: Subscribe SUSE Customer Center Account Products
description:
  - Manage SUSE Customer Center Products
  - This module requires the foreman_scc_manager plugin set up in the server
  - See U(https://github.com/ATIX-AG/foreman_scc_manager)
author:
  - "Manisha Singhal (@manisha15) ATIX AG"
options:
  scc_product:
    description: Full name of the product of suse customer center account
    required: true
    type: str
    aliases:
      - friendly_name
  scc_account:
    description: Name of the suse customer center account associated with product
    required: true
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Subscribe to suse customer center product"
  theforeman.foreman.scc_product:
    friendly_name: "Product1"
    scc_account: "Test"
    organization: "Test Organization"
'''

RETURN = ''' # '''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloAnsibleModule


def main():
    module = KatelloAnsibleModule(
        foreman_spec=dict(
            scc_product=dict(required=True, type='entity', aliases=['friendly_name'], scope=['scc_account'], thin=False),
            scc_account=dict(required=True, type='entity', scope=['organization']),
        ),
        required_plugins=[('scc_manager', ['*'])],
    )

    module.task_timeout = 4 * 60

    with module.api_connection():
        scc_product = module.lookup_entity('scc_product')

        if not scc_product.get('product_id'):
            payload = {'id': scc_product['id']}
            payload.update(module.scope_for('scc_account'))
            module.resource_action('scc_products', 'subscribe', payload)


if __name__ == '__main__':
    main()
