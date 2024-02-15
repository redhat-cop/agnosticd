# (c) 2021 Johnathan Kupferer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: agnosticd_user_data
    author: Johnathan Kupferer <jkupfere@redhat.com>
    version_added: "2.9"
    short_description: fetch data values set with agnosticd_user_info
    description:
      - This lookup returns data values set with agnosticd_user_info. 
    options:
      _terms:
        description: Data keys set in agnosticd_user_info.
        required: True
      user:
        description: User name to fetch data for specific user.
        required: False
"""

EXAMPLES = """
- name: "Set admin_password from value set with agnosticd_user_info"
  set_fact:
    admin_password: "{{ lookup('agnosticd_user_data', 'admin_password') }}"
  when: admin_password is undefined

- name: "Set user_password from value set with agnosticd_user_info for user1"
  set_fact:
    user_password: "{{ lookup('agnosticd_user_data', 'password', user='user1') }}"
  when: user_password is undefined
"""     

RETURN = """
  _raw:
    description:
      - list of values to get from agnosticd_user_info data
    type: list
    elements: raw   
"""

import os
import yaml

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

class LookupModule(LookupBase): 
    def run(self, terms, user=None, **kwargs):
        self.set_options(direct=kwargs)
        ret = []

        output_dir = self._templar.template('{{ output_dir | default(playbook_dir) | default(".") }}')
        user_data = {}
        try:
            fh = open(os.path.join(output_dir, 'user-data.yaml'), 'r')
            user_data = yaml.safe_load(fh)
            fh.close()
        except FileNotFoundError:
            pass

        if user:
            user_data = user_data.get('users', {}).get(user)

        for term in terms:
            if term == '*':
                ret.append(user_data)
            else:
                ret.append(user_data.get(term) if user_data else None)

        return ret
