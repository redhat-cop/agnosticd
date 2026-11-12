#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: azure_openenv_cleanup_subscription
short_description: Hardened Azure open-environment subscription / RG cleanup
version_added: "2.9"
description:
  - Deletes ARO clusters (with NAT teardown), nested blockers (AIServices,
    Resource Mover, etc.), then topo-sorted resource groups.
  - Does not release pool allocations; Sandbox API owns that (standalone clean_sub is the ops exception).
  - Use resource_groups to limit deletion on shared subscriptions (delete-open-env).
options:
  subscription_id:
    description: Azure subscription GUID to clean.
    required: true
    type: str
  auth_source:
    description:
      - Credential source. C(cli) uses AzureCliCredential (after az login).
      - C(env) uses DefaultAzureCredential (AZURE_CLIENT_ID / SECRET / TENANT).
    type: str
    default: cli
    choices: [cli, env]
  resource_groups:
    description:
      - If set, only these resource groups (and in-scope ARO/blockers) are deleted.
      - Omit for full subscription cleanup (pooled sandbox destroy).
    type: list
    elements: str
    required: false
  ignore_leftover_prefixes:
    description:
      - Leftover RG name prefixes that do not fail the module (e.g. VisualStudioOnline-).
    type: list
    elements: str
    default: []
  dry_run:
    description: Preview actions without deleting.
    type: bool
    default: false
  label:
    description: Log label (defaults to subscription_id).
    type: str
    required: false
author:
  - Red Hat GPTE
'''

EXAMPLES = r'''
- name: Full pooled subscription cleanup
  azure_openenv_cleanup_subscription:
    subscription_id: "{{ pool_subscription_id }}"
    auth_source: cli
    ignore_leftover_prefixes:
      - VisualStudioOnline-

- name: Guid-scoped cleanup on shared subscription
  azure_openenv_cleanup_subscription:
    subscription_id: "{{ azure_subscription_id }}"
    auth_source: cli
    resource_groups:
      - "openenv-{{ guid }}"
'''

RETURN = r'''
failed_rgs:
  description: Resource groups that failed to delete.
  type: list
  returned: always
leftover_rgs:
  description: Resource groups still present after cleanup (excluding ignored prefixes).
  type: list
  returned: always
leftover_aro:
  description: ARO clusters still present in scope.
  type: list
  returned: always
'''

import traceback

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible.module_utils.azure_openenv_cleanup import (
        cleanup_azure_subscription,
    )
    from ansible.module_utils.azure_openenv_cleanup.cleanup import (
        HAS_ARO,
        HAS_AZURE,
        IMPORT_ERROR,
    )
    HAS_CLEANUP = True
    CLEANUP_IMPORT_ERROR = None
except Exception as e:
    HAS_CLEANUP = False
    CLEANUP_IMPORT_ERROR = e
    HAS_AZURE = False
    HAS_ARO = False
    IMPORT_ERROR = e


def main():
    module = AnsibleModule(
        argument_spec=dict(
            subscription_id=dict(type='str', required=True),
            auth_source=dict(type='str', default='cli', choices=['cli', 'env']),
            resource_groups=dict(type='list', elements='str', required=False, default=None),
            ignore_leftover_prefixes=dict(type='list', elements='str', default=[]),
            dry_run=dict(type='bool', default=False),
            label=dict(type='str', required=False, default=None),
        ),
        supports_check_mode=True,
    )

    if not HAS_CLEANUP:
        module.fail_json(
            msg='Failed to import azure_openenv_cleanup: {0}'.format(CLEANUP_IMPORT_ERROR),
            exception=traceback.format_exc(),
        )
    if not HAS_AZURE:
        module.fail_json(
            msg='Azure Python SDK dependencies missing: {0}'.format(IMPORT_ERROR),
        )
    # azure-mgmt-redhatopenshift preferred; cleanup falls back to `az aro` if missing.

    dry_run = module.params['dry_run'] or module.check_mode
    messages = []

    def _log(msg):
        messages.append(str(msg))
        module.log(str(msg))

    try:
        result = cleanup_azure_subscription(
            subscription_id=module.params['subscription_id'],
            auth_source=module.params['auth_source'],
            dry_run=dry_run,
            only_resource_groups=module.params['resource_groups'],
            ignore_leftover_prefixes=module.params['ignore_leftover_prefixes'],
            label=module.params['label'],
            log=_log,
        )
    except Exception as e:
        module.fail_json(
            msg='Azure openenv cleanup failed: {0}'.format(e),
            exception=traceback.format_exc(),
            messages=messages,
        )

    payload = dict(
        changed=not dry_run,
        failed_rgs=result.failed_rgs,
        leftover_rgs=result.leftover_rgs,
        leftover_aro=result.leftover_aro,
        messages=messages,
    )
    if not result.ok and not dry_run:
        module.fail_json(
            msg=(
                'Azure cleanup incomplete; leftover RGs={0} ARO={1}'.format(
                    result.leftover_rgs or result.failed_rgs,
                    result.leftover_aro,
                )
            ),
            **payload
        )
    module.exit_json(**payload)


if __name__ == '__main__':
    main()
