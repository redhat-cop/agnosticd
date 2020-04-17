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
import yaml
import os

# Force yaml string representation for safe dump
yaml.SafeDumper.yaml_representers[None] = lambda self, data: \
    yaml.representer.SafeRepresenter.represent_str(
        self,
        str(data),
    )

from ansible.errors import AnsibleError, AnsibleUndefinedVariable
from ansible.module_utils.six import string_types
from ansible.module_utils._text import to_text
from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):
    '''Print statements during execution and save user info to file'''

    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset(('msg','data','user'))

    def run(self, tmp=None, task_vars=None):
        self._supports_check_mode = True

        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp # tmp no longer has any effect

        msg = self._task.args.get('msg')
        data = self._task.args.get('data', {})
        user = self._task.args.get('user')

        if not user and msg != None:
            # Output msg in result, prepend "user.info: " for cloudforms compatibility
            result['msg'] = 'user.info: ' + msg
            # Force display of result like debug
            result['_ansible_verbose_always'] = True

        if data:
            result['data'] = data
            if not isinstance(data, dict):
                result['failed'] = True
                result['error'] = 'data must be a dictionary of name/value pairs'
                return result

        try:
            output_dir = self._templar.template(
                task_vars.get('output_dir',
                    task_vars['hostvars'].get('localhost',{}).get('output_dir',
                        task_vars.get('playbook_dir', '.')
                    )
                )
            )
            if not user and msg != None:
                fh = open(os.path.join(output_dir, 'user-info.yaml'), 'a')
                fh.write('- ' + json.dumps(msg) + "\n")
                fh.close()
            if data or user:
                user_data = None
                try:
                    fh = open(os.path.join(output_dir, 'user-data.yaml'), 'r')
                    user_data = yaml.safe_load(fh)
                    fh.close()
                except FileNotFoundError:
                    pass

                if user_data == None:
                    user_data = {}

                if user:
                    if 'users' not in user_data:
                        user_data['users'] = {}
                    if user in user_data['users']:
                        user_data_item = user_data['users'][user]
                        user_data_item.update(data)
                    else:
                        user_data_item = data
                        user_data['users'][user] = user_data_item
                    if msg:
                        if 'msg' in user_data_item:
                            user_data_item['msg'] += "\n" + msg
                        else:
                            user_data_item['msg'] = msg
                else:
                    user_data.update(data)

                fh = open(os.path.join(output_dir, 'user-data.yaml'), 'w')
                yaml.safe_dump(user_data, stream=fh, explicit_start=True)
                fh.close()
            result['failed'] = False
        except Exception as e:
            result['failed'] = True
            result['error'] = str(e)

        return result
