# (c) 2021 Johnathan Kupferer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: unvault_string
    author: Johnathan Kupferer <jkupfere@redhat.com>
    version_added: "2.9"
    short_description: return unvaulted content of string
    description:
      - This lookup returns the unvaulted content of a string.
      - If the string does not start with "$ANSIBLE_VAULT;" then it is just passed through.
    options:
      _terms:
        description: strings to unvault
        required: True
"""

EXAMPLES = """
- name: "Say hello with vault password 'password'"
  vars:
    message:
      $ANSIBLE_VAULT;1.1;AES256
      30376531373636383363376663356630393734623738396535313431376331356661396662666638
      6462323066646639343066373062616434626437383033620a343834363237336131316336666439
      36366666636331356463373531346633346137383333653039353236613830643236663638393162
      3632643836646533620a323861653131623936653732653534316637346536613237383735336666
      3664
  debug:
    msg: "{{ lookup('unvault_string', message) }}"
"""     

RETURN = """
  _raw:
    description:
      - list of strings to unvault
    type: list
    elements: raw   
"""

from ansible.plugins.lookup import LookupBase

class LookupModule(LookupBase): 
    def run(self, terms, variables=None, **kwargs):
        self.set_options(direct=kwargs)
        ret = []
        for term in terms:
            if term.startswith('$ANSIBLE_VAULT;'):
                ret.append(self._loader._vault.decrypt(term.encode('utf-8')).decode('utf-8'))
            else:
                ret.append(term)
        return ret
