#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Andrew Kofink <ajkofink@gmail.com>
# (c) 2019, Matthias Dellweg <dellweg@atix.de>
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
module: sync_plan
version_added: 1.0.0
short_description: Manage Sync Plans
description:
  - Manage sync plans
author:
  - "Andrew Kofink (@akofink)"
  - "Matthis Dellweg (@mdellweg) ATIX-AG"
options:
  name:
    description:
      - Name of the sync plan
    required: true
    type: str
  description:
    description:
      - Description of the sync plan
    type: str
  interval:
    description:
      - How often synchronization should run
    choices:
      - hourly
      - daily
      - weekly
      - custom cron
    required: true
    type: str
  enabled:
    description:
      - Whether the sync plan is active
    required: true
    type: bool
  sync_date:
    description:
      - Start date and time of the first synchronization
    required: true
    type: str
  cron_expression:
    description:
      - A cron expression as found in crontab files
      - This must be provided together with I(interval='custom cron').
    type: str
  products:
    description:
      - List of products to include in the sync plan
    required: false
    type: list
    elements: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Create or update weekly RHEL sync plan"
  theforeman.foreman.sync_plan:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Weekly RHEL Sync"
    organization: "Default Organization"
    interval: "weekly"
    enabled: false
    sync_date: "2017-01-01 00:00:00 UTC"
    products:
      - 'Red Hat Enterprise Linux Server'
    state: present
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    sync_plans:
      description: List of sync plans.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


class KatelloSyncPlanModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloSyncPlanModule(
        foreman_spec=dict(
            name=dict(required=True),
            description=dict(),
            interval=dict(choices=['hourly', 'daily', 'weekly', 'custom cron'], required=True),
            enabled=dict(type='bool', required=True),
            sync_date=dict(required=True),
            cron_expression=dict(),
            products=dict(type='entity_list', scope=['organization'], resolve=False),
        ),
        argument_spec=dict(
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
        required_if=[
            ['interval', 'custom cron', ['cron_expression']],
        ],
    )

    if (module.foreman_params['interval'] != 'custom cron') and ('cron_expression' in module.foreman_params):
        module.fail_json(msg='"cron_expression" cannot be combined with "interval"!="custom cron".')

    with module.api_connection():
        entity = module.lookup_entity('entity')
        scope = module.scope_for('organization')

        handle_products = not (module.desired_absent or module.state == 'present_with_defaults') and 'products' in module.foreman_params
        if handle_products:
            module.lookup_entity('products')

        products = module.foreman_params.pop('products', None)
        sync_plan = module.run()

        if handle_products:
            desired_product_ids = set(product['id'] for product in products)
            current_product_ids = set(product['id'] for product in entity['products']) if entity else set()

            module.record_before('sync_plans/products', {'id': sync_plan['id'], 'product_ids': current_product_ids})
            module.record_after('sync_plans/products', {'id': sync_plan['id'], 'product_ids': desired_product_ids})
            module.record_after_full('sync_plans/products', {'id': sync_plan['id'], 'product_ids': desired_product_ids})

            if desired_product_ids != current_product_ids:
                if not module.check_mode:
                    product_ids_to_add = desired_product_ids - current_product_ids
                    if product_ids_to_add:
                        payload = {
                            'id': sync_plan['id'],
                            'product_ids': list(product_ids_to_add),
                        }
                        payload.update(scope)
                        module.resource_action('sync_plans', 'add_products', payload)
                    product_ids_to_remove = current_product_ids - desired_product_ids
                    if product_ids_to_remove:
                        payload = {
                            'id': sync_plan['id'],
                            'product_ids': list(product_ids_to_remove),
                        }
                        payload.update(scope)
                        module.resource_action('sync_plans', 'remove_products', payload)
                else:
                    module.set_changed()


if __name__ == '__main__':
    main()
