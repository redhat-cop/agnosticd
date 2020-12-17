# (c) 2020 Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
lookup: host_virtualenv_combined_requirements
author: Johnathan Kupferer <jkupfere@redhat.com>
version_added: "2.9"
short_description: Combine Python virtualenv definitions
description:
- This lookup returns a string representing a Python virtualenv definition from multiple sources with overrides
options:
  _terms:
    description: Requirement sources
    required: True
"""

RETURN = """
_raw:
  description:
  - content of combined virtualenv definitions
"""

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils._text import to_text
from ansible.utils.display import Display
import six
import re

display = Display()

class LookupModule(LookupBase):

    def __read_requirements(self, reqfile, requirements, variables=None):
        lookupfile = self.find_file_in_search_path(variables, 'files', reqfile)
        if not lookupfile:
            raise AnsibleError("could not locate file in lookup: {}".format(reqfile))
        display.vvvv("Requirements file is {}".format(lookupfile))
        b_contents, show_data = self._loader._get_file_contents(lookupfile)
        contents = to_text(b_contents, errors='surrogate_or_strict')

        for line in contents.splitlines():
            if line and line[0] != '#':
                self.__add_requirement(line, requirements)

    def __add_requirement(self, reqspec, requirements):
        m = re.match(r'^(-?)([\w\-.]+)(,?(<|>|<=|>=|==|!=|~=)[0-9.]*\*?)*$', reqspec)
        if m:
            exclude, name, versionspec = (m.group(1), m.group(2), m.group(3))
            if exclude == '-':
                if not versionspec or requirements.get(name) == versionspec:
                    requirements.pop(name, None)
            else:
                requirements[name] = versionspec
        else:
            raise AnsibleError("could not parse requirement {}".format(reqspec))

    def run(self, terms, variables=None, override=None, **kwargs):

        requirements = {}

        for term in terms:
            display.debug("lookup term: {}".format(term))
            if isinstance(term, six.string_types):
                self.__read_requirements(term, requirements, variables=variables)
            else:
                for item in term:
                    self.__read_requirements(item, requirements, variables=variables)

        if isinstance(override, dict):
            requirements.update(override)
        elif override:
            for item in override:
                self.__add_requirement(item, requirements)

        ret = ''
        for k, v in requirements.items():
            if v:
                ret += k + v + "\n"
            else:
                ret += k + "\n"
            
        return [ret]
