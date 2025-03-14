#!/usr/bin/env python3


__metaclass__ = type
DOCUMENTATION = """
    lookup: agnosticd_requirements
    author: Guillaume Core <gucore@redhat.com>
    version_added: "2.12"
    short_description: Load list of requirements + strategic merge.
    description:
      - Return dictionary of requirements content after strategic merge
    options:
      _terms:
        description: list of paths
"""

EXAMPLES = """
- name: load requirements
  debug:
    msg: "{{ lookup('agnosticd_requirements', 'path1', 'path2') }}"
"""

RETURN = """
_raw:
   description: Content of requirements after strategic merge
"""

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
from os.path import exists
import yaml

display = Display()

def set_in_list(elem, l):
    name = elem.get('name')
    if not isinstance(l, list):
        return

    for i, el in enumerate(l):
        if el.get('name') == elem.get('name'):
            l[i] = elem
            return

    l.append(elem)

def agnosticd_load_and_compile_requirements(*paths):
    requirements = []
    for path in paths:
        if not exists(path):
            continue

        with open(path) as stream:
            try:
                content = yaml.safe_load(stream)
                requirements.append(content)
            except yaml.YAMLError as exc:
                raise AnsibleLookupError(
                    'agnosticd_requirements: %s' %(exc))

    return agnosticd_compile_requirements(requirements)


def agnosticd_compile_requirements(requirements):
    '''This function makes sure collections are not installed several times
    by compiling the requirement_files together using a strategic merge (key == name).

    Last requirement file takes precedence.'''

    roles = []
    collections = []

    for requirement in requirements:

       if requirement == []:
            continue
       if requirement == {}:
            continue

       if not isinstance(requirement, dict):
           raise AnsibleLookupError(
               'agnosticd_requirements: only dict are supported: %s' %(requirements))
       # Roles
       for role in requirement.get('roles', []):
           set_in_list(role, roles)

       for collection in requirement.get('collections', []):
           set_in_list(collection, collections)

    result = {}

    if len(roles) > 0:
        result['roles'] = roles
    if len(collections) > 0:
        result['collections'] = collections

    return result

class LookupModule(LookupBase):

    def run(self, terms, **kwargs):
        result = []
        paths = []
        for term in terms:
            if isinstance(term, str):
                paths.append(term)
            if isinstance(term, list):
                for t in term:
                    paths.append(t)

        result = [agnosticd_load_and_compile_requirements(*paths)]
        return result
