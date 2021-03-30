# Copyright (c) 2020 Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

import hashlib
import re
from ansible.errors import AnsibleFilterError

def agnosticd_dynamic_source_name(source):
    if 'name' in source:
        return source['name']
    if re.match('[\w\-]+\.([\w\-]+)$', source['src']):
        return source['src']
    m = re.search(r'/([\w\-]+)(\.git)?$', source['src'])
    if m:
        return m.group(1)
    raise AnsibleFilterError("Unable to determine source name from {}, name must be provided".format(source['src']))

def agnosticd_dynamic_source_version(source):
    return source.get('version', 'latest')

def agnosticd_dynamic_git_source_name(source):
    m = re.search(r'/([^/]+)(\.git)?$', source['repo'])
    prefix = m.group(1) + '-'
    if 'version' in source:
        prefix += source['version'] + '-'
    return prefix + hashlib.sha256((
        source['repo'] + ':' + source.get('version', '')
    ).encode('utf-8')).hexdigest()

# ---- Ansible filters ----
class FilterModule(object):
    def filters(self):
        return {
            'agnosticd_dynamic_source_name': agnosticd_dynamic_source_name,
            'agnosticd_dynamic_source_version': agnosticd_dynamic_source_version,
            'agnosticd_dynamic_git_source_name': agnosticd_dynamic_git_source_name
        }
