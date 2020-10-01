# Copyright (c) 2020 Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

import re

from ansible import errors

def agnosticd_dynamic_cache_enabled(source):
    '''
    Return whether cache is enabled for this source.
    Cache may be enabled explicitly or otherwise detected from the version string.
    Versions that appear to use semantic versioning will be enabled for cache.
    '''
    if 'cache' in source:
        return bool(source['cache'])
    if 'version' not in source:
        return False
    elif re.search(r'\d+\.\d+\.\d+', source['version']):
        return True
    else:
        return False

def agnosticd_dynamic_cache_disabled(source):
    '''
    Return whether cache is disbled for this source.
    '''
    return not agnosticd_dynamic_cache_enabled(source)

class TestModule(object):
    def tests(self):
        return dict(
            agnosticd_dynamic_cache_enabled=agnosticd_dynamic_cache_enabled,
            agnosticd_dynamic_cache_disabled=agnosticd_dynamic_cache_disabled
        )
