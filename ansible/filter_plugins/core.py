#!/usr/bin/env python
from ansible.errors import AnsibleFilterError
from ansible.utils.display import Display
from ansible.module_utils.six import string_types

display = Display()

def to_equinix_metal_tags(tags):
    '''Filter to convert agnosticd tags to Equinix Tags format'''
    if not isinstance(tags, list):
        raise AnsibleFilterError(
            '''Invalid type used with to_equinix_metal_tags filter,
            expect a list, got %s''' %(type(tags)))

    converted = []
    try:
        for tag in tags:
            if not isinstance(tag, dict):
                raise AnsibleFilterError(
                    'Invalid input for to_equinix_metal_tag, expect list of dict, got list of %s'
                    %(type(tag))
                )
            if 'key' not in tag or 'value' not in tag:
                raise AnsibleFilterError(
                    'Invalid input for to_equinix_metal_tag, key/value keys expected in elements.'
                )
            if not isinstance(tag['key'], string_types) or tag['key'] == "":
                raise AnsibleFilterError(
                    'Invalid input for to_equinix_metal_tag, key must be a non-empty string.'
                )
            if not isinstance(tag['value'], string_types) or tag['value'] == "":
                raise AnsibleFilterError(
                    'Invalid input for to_equinix_metal_tag, value must be a non-empty string.'
                )

            converted.append('%s=%s' %(tag['key'], tag['value']))
    except Exception as e:
        raise AnsibleFilterError(e)

    return converted

def from_equinix_metal_tags(tags):
    '''Convert Equinix Tags to a dict'''

    if not isinstance(tags, list):
        raise AnsibleFilterError(
            '''Invalid type used with from_equinix_metal_tags filter,
            expect a list, got %s''' %(type(tags)))

    converted = dict()
    try:
        for tag in tags:
            if not isinstance(tag, string_types):
                raise AnsibleFilterError(
                    '''Invalid type used with from_equinix_metal_tags filter,
                    expect a string, got %s''' %(type(tag)))

            if '=' in tag:
                splitted = tag.split("=")
                if splitted[0] == "":
                    raise AnsibleFilterError(
                        'Invalid type used with from_equinix_metal_tags filter, '
                        'key is empty string.'
                    )
                converted[splitted[0]] = splitted[1]
    except Exception as e:
        raise AnsibleFilterError(e)

    return converted

class FilterModule(object):
    ''' AgnosticD core jinja2 filters '''

    def filters(self):
        return {
            'to_equinix_metal_tags': to_equinix_metal_tags,
            'from_equinix_metal_tags': from_equinix_metal_tags,
        }
