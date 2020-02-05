#!/usr/bin/python
# 
# Copyright: (c) 2020, Johnathan Kupferer <jkupfere@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# This plugin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os

from ansible.errors import AnsibleError, AnsibleUndefinedVariable
from ansible.module_utils.six import string_types
from ansible.module_utils._text import to_text
from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):
    '''Print statements during execution and save user info to file'''

    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset(('msg',))

    def run(self, tmp=None, task_vars=None):
        self._supports_check_mode = True

        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp # tmp no longer has any effect

        result['msg'] = 'user.info: ' + self._task.args['msg']
        result['_ansible_verbose_always'] = True

        try:
            output_dir = self._templar.template(
                task_vars.get('output_dir',
                    task_vars['hostvars'].get('localhost',{}).get('output_dir',
                        task_vars.get('playbook_dir', '.')
                    )
                )
            )
            fh = open(os.path.join(output_dir, 'user-info.yaml'), 'a')
            fh.write('- ' + json.dumps(self._task.args['msg']) + "\n")
            fh.close()
            result['failed'] = False
        except Exception as e:
            result['failed'] = True
            result['error'] = str(e)

        return result
