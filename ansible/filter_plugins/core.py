#!/usr/bin/env python
from copy import deepcopy
from ansible.errors import AnsibleFilterError
from ansible.utils.display import Display
from ansible.module_utils.six import string_types, integer_types

display = Display()

def ec2_tags_to_dict(tags):
    '''Filter to convert agnosticd tags to Equinix Tags format'''

    function_name="ec2_tags_to_dict"

    if not isinstance(tags, list):
        raise AnsibleFilterError(
            '''Invalid type used with %s filter,
            expect a list, got %s''' %(function_name, type(tags)))

    converted = {}
    try:
        for tag in tags:
            keynocase = 'key'
            if 'Key' in tag:
                keynocase = 'Key'

            valuenocase = 'value'
            if 'Value' in tag:
                valuenocase = 'Value'

            if keynocase not in tag:
                raise AnsibleFilterError(
                    '%s: Invalid input, key keys expected in elements.'
                    %(function_name)
                )

            if valuenocase not in tag:
                raise AnsibleFilterError(
                    '%s: Invalid input, value keys expected in elements.'
                    %(function_name)
                )

            if not isinstance(tag[keynocase], string_types) or tag[keynocase] == "":
                raise AnsibleFilterError(
                    '%s: Invalid input, key must be a non-empty string.' %(function_name)
                )
            if not isinstance(tag[valuenocase], string_types) or tag[valuenocase] == "":
                raise AnsibleFilterError(
                    '%s: Invalid input, value must be a non-empty string.'
                    %(function_name)
                )

            converted[tag[keynocase]] = tag[valuenocase]
    except Exception as e:
        raise AnsibleFilterError(e)

    return converted


def dict_to_equinix_metal_tags(tags, delim='='):
    '''Filter to convert dictionary to Equinix Tags format'''

    function_name = "dict_to_equinix_metal_tags"

    if not isinstance(tags, dict):
        raise AnsibleFilterError(
            '''Invalid type used with %s filter,
            expect a dict, got %s''' %(function_name, type(tags)))

    converted = []

    try:
        for key in tags:
            if isinstance(tags[key], integer_types):
                tags[key]=str(tags[key])

            if not isinstance(key, string_types):
                raise AnsibleFilterError(
                    '%s: Invalid input, expect keys to be string, got key of type %s'
                    %(function_name, type(key))
                )
            if not isinstance(tags[key], string_types):
                raise AnsibleFilterError(
                    '%s: Invalid input, expect dict of string, got value of type %s'
                    %(function_name, type(tags[key]))
                )

            converted.append('%s%s%s' %(key,delim, tags[key]))

    except Exception as e:
        raise AnsibleFilterError(e)

    return converted

def ec2_tags_to_equinix_metal_tags(tags):
    '''Filter to convert agnosticd tags to Equinix Tags format'''
    function_name = "ec2_tags_to_equinix_metal_tags"

    if not isinstance(tags, list):
        raise AnsibleFilterError(
            '''Invalid type used with %s filter,
            expect a list, got %s''' %(function_name, type(tags)))

    converted = []
    try:
        for tag in tags:
            if not isinstance(tag, dict):
                raise AnsibleFilterError(
                    '%s: Invalid input, expect list of dict, got list of %s'
                    %(function_name, type(tag))
                )

            keynocase = 'key'
            if 'Key' in tag:
                keynocase = 'Key'

            valuenocase = 'value'
            if 'Value' in tag:
                valuenocase = 'Value'

            if keynocase not in tag:
                raise AnsibleFilterError(
                    '%s: Invalid input, key keys expected in elements.'
                    %(function_name)
                )

            if valuenocase not in tag:
                raise AnsibleFilterError(
                    '%s: Invalid input, value keys expected in elements.'
                    %(function_name)
                )

            if not isinstance(tag[keynocase], string_types) or tag[keynocase] == "":
                raise AnsibleFilterError(
                    '%s: Invalid input, key must be a non-empty string.'
                    %(function_name)
                )
            if not isinstance(tag[valuenocase], string_types) or tag[valuenocase] == "":
                raise AnsibleFilterError(
                    '%s: Invalid input, value must be a non-empty string.'
                    %(function_name)
                )

            converted.append('%s=%s' %(tag[keynocase], tag[valuenocase]))
    except Exception as e:
        raise AnsibleFilterError(e)

    return converted

def equinix_metal_tags_to_dict(tags, delim='='):
    '''Convert Equinix Tags to a dict'''

    function_name = "equinix_metal_tags_to_dict"

    if not isinstance(tags, list):
        raise AnsibleFilterError(
            '''Invalid type used with %s filter,
            expect a list, got %s''' %(function_name, type(tags)))

    converted = dict()
    try:
        for tag in tags:
            if not isinstance(tag, string_types):
                raise AnsibleFilterError(
                    '''Invalid type used with %s filter,
                    expect a string, got %s''' %(function_name, type(tag)))

            if delim in tag:
                splitted = tag.split(delim, 1)
                if splitted[0] == "":
                    raise AnsibleFilterError(
                        'Invalid type used with %s filter, key is empty string.'
                        %(function_name)
                    )
                converted[splitted[0]] = splitted[1]
    except Exception as e:
        raise AnsibleFilterError(e)

    return converted



# Backport https://github.com/ansible-collections/amazon.aws/commit/bc1dc58a882b563a4e5448d693ef08b4c2bbbceb#diff-11d6a927433f45aa84de2f54fa0adf33e8094ebb417c75ea476ffe61b4e4f587
# here to support old version of boto that we use in our different virtualenvs
def dict_sanitize_boto3_filter(filters_dict):
    filters_sanitized = dict()
    for k, v in filters_dict.items():
        if isinstance(v, bool):
            filters_sanitized[k] = [str(v).lower()]
        elif isinstance(v, integer_types):
            filters_sanitized[k] = [str(v)]
        elif isinstance(v, string_types):
            filters_sanitized[k]= [v]
        else:
            filters_sanitized[k] = v

    return filters_sanitized

def image_to_ec2_filters(image):
    '''Convert agnosticd instances[].image dict to ec2 filters to be used in ec2_ami_info'''

    function_name = "image_to_ec2_filters"

    if not isinstance(image, dict):
        raise AnsibleFilterError(
            '''Invalid type used with %s filter,
            expect a dict, got %s''' %(function_name, type(image)))

    filters = dict()

    if 'tags' in image:
        if not isinstance(image['tags'], dict):
            raise AnsibleFilterError(
                '''Invalid type for tags used with %s filter,
                expect a dict, got %s''' %(function_name, type(image['tags'])))

        for key in image['tags']:
            filters['tag:'+key] = image['tags'][key]

    if 'architecture' in image:
        filters['architecture'] = image['architecture']
    else:
        filters['architecture'] = 'x86_64'

    if 'name' in image:
        filters['name'] = image['name']

    if 'aws_filters' in image:
        filters.update(image['aws_filters'])

    return dict_sanitize_boto3_filter(filters)

def agnosticd_get_all_images(image, predefined, done=None):
    '''Cascade and list images (and fallback images) from an image
    or a list of images'''

    function_name = "agnosticd_get_all_images"
    if done is None:
        done = {}

    # str can be links to another images or list of images
    if isinstance(image, str):
        if image in predefined:
            # Detect infinite loops
            if image in done:
                raise AnsibleFilterError(
                    '%s: Loop detected in image definitions: %s' %(function_name, done))

            done[image] = True
            # call again by resolving the image defined in predefined
            return agnosticd_get_all_images(predefined[image], predefined, done)

        # No match, return no image (backward-compatible)
        return []

    if isinstance(image, dict):
        return [image]

    if isinstance(image, list):
        result = []
        for _image in image:
            result.extend(agnosticd_get_all_images(_image, predefined, done))

        return result

def agnosticd_filter_out_installed_collections(requirements, installed_collections):
    '''Remove collections from a requirement content that are already installed.

    argument collections is a dict, usually output of the command:
    ansible-galaxy collection list --format json
    , ex:
    {
        "/usr/share/ansible/collections/ansible_collections": {
            {
                "community.general": {
                "version": "6.3.0"
                },
                "openstack.cloud": {
                "version": "2.0.0"
                }
            }
        }
    }
    '''

    requirements = deepcopy(requirements)
    function_name = "agnosticd_remove_collection_already_installed"

    if not isinstance(requirements, dict):
        raise AnsibleFilterError(
            '%s: requirement content arg should be a dict' %(function_name)
        )
    if not isinstance(installed_collections, dict):
        raise AnsibleFilterError(
            '%s: collections arg should be a dict' %(function_name)
        )

    if 'collections' not in requirements:
        return requirements

    installed = {}
    for _, collections_ in installed_collections.items():
        for collection, value in collections_.items():
            if collection in installed:
                continue
            installed[collection] = value["version"]

    keep_collections = []

    for collection in requirements['collections']:
        if 'name' not in collection:
            continue

        if collection['name'] not in installed:
            # collection is not installed, keep it
            keep_collections.append(collection)
        else:
            display.warning(
                "skipping installation of %s==%s ; %s==%s already installed in EE"
                %(collection['name'],
                  collection['version'],
                  collection['name'],
                  installed[collection['name']])
            )


    requirements['collections'] = keep_collections

    return requirements


def agnosticd_instances_to_odcr(instances, agnosticd_images):
    '''Convert agnosticd instances list to on demand capacity reservations'''

    result = []

    for instance in instances:

        instance_type = instance.get('flavor', {}).get('ec2', None)
        if not instance_type:
            raise AnsibleFilterError(
                'instance_type or flavor.ec2 is required in instance definition'
            )

        if instance['name'] in agnosticd_images:
            instance['instance_platform'] = instance.get(
                'instance_platform',
                agnosticd_images.get(instance['name'], {}).get('platform_details', 'Linux/UNIX'))
            if instance['instance_platform'] == 'Red Hat BYOL Linux':
                # Red Hat BYOL Linux is not supported by ODCR, use Linux/UNIX
                instance['instance_platform'] = 'Linux/UNIX'

        result.append({
            'instance_count': instance.get('count', 1),
            'instance_type': instance_type,
            'instance_platform': instance.get('instance_platform', 'Linux/UNIX'),
        })

    return result

def agnosticd_expand_instances(instances):
    """Expand instances list to a flat list of instances, using the count field"""

    function_name = "agnosticd_expand_instances"

    if not isinstance(instances, list):
        raise AnsibleFilterError(
            '%s: instances should be a list, got %s' %(function_name, type(instances))
        )

    expanded = []
    for instance in instances:
        if not isinstance(instance, dict):
            raise AnsibleFilterError(
                '%s: instance should be a dict, got %s' %(function_name, type(instance))
            )

        count = instance.get('count', 1)
        if not isinstance(count, integer_types) or count < 1:
            raise AnsibleFilterError(
                '%s: count should be a positive integer, got %s' %(function_name, count)
            )

        if count == 1:
            # If count is 1, just add the instance as is
            expanded.append(deepcopy(instance))
            continue

        for i in range(count):
            new_instance = deepcopy(instance)
            new_instance['count'] = 1  # Reset count to 1 for each instance
            new_instance['name'] = f"{instance.get('name')}{i+1}"
            expanded.append(new_instance)

    return expanded

class FilterModule(object):
    ''' AgnosticD core jinja2 filters '''

    def filters(self):
        return {
            'ec2_tags_to_equinix_metal_tags': ec2_tags_to_equinix_metal_tags,
            'ec2_tags_to_dict': ec2_tags_to_dict,
            'dict_to_equinix_metal_tags': dict_to_equinix_metal_tags,
            'equinix_metal_tags_to_dict': equinix_metal_tags_to_dict,
            'image_to_ec2_filters': image_to_ec2_filters,
            'agnosticd_get_all_images': agnosticd_get_all_images,
            'agnosticd_filter_out_installed_collections': agnosticd_filter_out_installed_collections,
            'agnosticd_instances_to_odcr': agnosticd_instances_to_odcr,
            'agnosticd_expand_instances': agnosticd_expand_instances,
        }
