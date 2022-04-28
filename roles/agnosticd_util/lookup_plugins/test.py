# Copyright: (c) 2020, Johnathan Kupferer <jkupfere@redhat.com>
# Copyright: (c) 2022, Guillaume Core <gucore@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: test
    author: Johnathan Kupferer <jkupfere@redhat.com>, Guillaume Core <gucore@redhat.com>
    version_added: "2.9"
    short_description: check test condition
    description:
      - Return evaluation of test condition
    options:
      _terms:
        description: list of tests
"""

EXAMPLES = """
- name: show templating results
  debug:
    msg: "{{ lookup('test', 'foo is defined') }}"
"""

RETURN = """
_raw:
   description: boolean result of conditional evaluation
"""

from ansible.plugins.lookup import LookupBase
from ansible.plugins.filter.core import to_bool

class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):
        result = []
        for term in terms:
            if isinstance(term, str):
                result.append(self._templar.template('{{(' + term + ')|bool}}'))
            else:
                result.append(to_bool(term))
        return result
