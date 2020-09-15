# -*- coding: utf-8 -*-
# (c) Matthias Dellweg (ATIX AG) 2017

# pylint: disable=raise-missing-from
# pylint: disable=super-with-arguments

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import hashlib
import json
import os
import operator
import re
import time
import traceback

from contextlib import contextmanager

from collections import defaultdict
from functools import wraps

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_bytes, to_native
from ansible.module_utils import six

try:
    import apypie
    import requests.exceptions
    HAS_APYPIE = True
    inflector = apypie.Inflector()
except ImportError:
    HAS_APYPIE = False
    APYPIE_IMP_ERR = traceback.format_exc()

try:
    import yaml
    HAS_PYYAML = True
except ImportError:
    HAS_PYYAML = False
    PYYAML_IMP_ERR = traceback.format_exc()

parameter_foreman_spec = dict(
    id=dict(type='invisible'),
    name=dict(required=True),
    value=dict(type='raw', required=True),
    parameter_type=dict(default='string', choices=['string', 'boolean', 'integer', 'real', 'array', 'hash', 'yaml', 'json']),
)

parameter_ansible_spec = {k: v for (k, v) in parameter_foreman_spec.items() if k != 'id'}

_PLUGIN_RESOURCES = {
    'discovery': 'discovery_rules',
    'katello': 'subscriptions',
    'openscap': 'scap_contents',
    'remote_execution': 'remote_execution_features',
    'scc_manager': 'scc_accounts',
    'snapshot_management': 'snapshots',
    'templates': 'templates',
}

ENTITY_KEYS = dict(
    hostgroups='title',
    locations='title',
    operatingsystems='title',
    # TODO: Organizations should be search by title (as foreman allow nested orgs) but that's not the case ATM.
    #       Applying this will need to record a lot of tests that is out of scope for the moment.
    # organizations='title',
    scap_contents='title',
    scc_products='friendly_name',
    users='login',
)


def _exception2fail_json(msg='Generic failure: {0}'):
    def decor(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except Exception as e:
                self.fail_from_exception(e, msg.format(to_native(e)))
        return inner
    return decor


class KatelloMixin():
    def __init__(self, **kwargs):
        foreman_spec = dict(
            organization=dict(type='entity', required=True),
        )
        foreman_spec.update(kwargs.pop('foreman_spec', {}))
        required_plugins = kwargs.pop('required_plugins', [])
        required_plugins.append(('katello', ['*']))
        super(KatelloMixin, self).__init__(foreman_spec=foreman_spec, required_plugins=required_plugins, **kwargs)

    @_exception2fail_json(msg="Failed to connect to Foreman server: {0}")
    def connect(self):
        super(KatelloMixin, self).connect()

        self._patch_content_uploads_update_api()
        self._patch_organization_update_api()
        self._patch_subscription_index_api()
        self._patch_sync_plan_api()

    def _patch_content_uploads_update_api(self):
        """This is a workaround for the broken content_uploads update apidoc in katello.
            see https://projects.theforeman.org/issues/27590
        """

        _content_upload_methods = self.foremanapi.apidoc['docs']['resources']['content_uploads']['methods']

        _content_upload_update = next(x for x in _content_upload_methods if x['name'] == 'update')
        _content_upload_update_params_id = next(x for x in _content_upload_update['params'] if x['name'] == 'id')
        _content_upload_update_params_id['expected_type'] = 'string'

        _content_upload_destroy = next(x for x in _content_upload_methods if x['name'] == 'destroy')
        _content_upload_destroy_params_id = next(x for x in _content_upload_destroy['params'] if x['name'] == 'id')
        _content_upload_destroy_params_id['expected_type'] = 'string'

    def _patch_organization_update_api(self):
        """This is a workaround for the broken organization update apidoc in katello.
            see https://projects.theforeman.org/issues/27538
        """

        _organization_methods = self.foremanapi.apidoc['docs']['resources']['organizations']['methods']

        _organization_update = next(x for x in _organization_methods if x['name'] == 'update')
        _organization_update_params_organization = next(x for x in _organization_update['params'] if x['name'] == 'organization')
        _organization_update_params_organization['required'] = False

    def _patch_subscription_index_api(self):
        """This is a workaround for the broken subscriptions apidoc in katello.
        https://projects.theforeman.org/issues/27575
        """

        _subscription_methods = self.foremanapi.apidoc['docs']['resources']['subscriptions']['methods']

        _subscription_index = next(x for x in _subscription_methods if x['name'] == 'index')
        _subscription_index_params_organization_id = next(x for x in _subscription_index['params'] if x['name'] == 'organization_id')
        _subscription_index_params_organization_id['required'] = False

    def _patch_sync_plan_api(self):
        """This is a workaround for the broken sync_plan apidoc in katello.
            see https://projects.theforeman.org/issues/27532
        """

        _organization_parameter = {
            u'validations': [],
            u'name': u'organization_id',
            u'show': True,
            u'description': u'\n<p>Filter sync plans by organization name or label</p>\n',
            u'required': False,
            u'allow_nil': False,
            u'allow_blank': False,
            u'full_name': u'organization_id',
            u'expected_type': u'numeric',
            u'metadata': None,
            u'validator': u'Must be a number.',
        }

        _sync_plan_methods = self.foremanapi.apidoc['docs']['resources']['sync_plans']['methods']

        _sync_plan_add_products = next(x for x in _sync_plan_methods if x['name'] == 'add_products')
        if next((x for x in _sync_plan_add_products['params'] if x['name'] == 'organization_id'), None) is None:
            _sync_plan_add_products['params'].append(_organization_parameter)

        _sync_plan_remove_products = next(x for x in _sync_plan_methods if x['name'] == 'remove_products')
        if next((x for x in _sync_plan_remove_products['params'] if x['name'] == 'organization_id'), None) is None:
            _sync_plan_remove_products['params'].append(_organization_parameter)


class TaxonomyMixin(object):
    def __init__(self, **kwargs):
        foreman_spec = dict(
            organizations=dict(type='entity_list'),
            locations=dict(type='entity_list'),
        )
        foreman_spec.update(kwargs.pop('foreman_spec', {}))
        super(TaxonomyMixin, self).__init__(foreman_spec=foreman_spec, **kwargs)


class ParametersMixin(object):
    def __init__(self, **kwargs):
        self.entity_name = kwargs.pop('entity_name', self.entity_name_from_class)
        parameters_flat_name = getattr(self, "PARAMETERS_FLAT_NAME", None) or '{0}_parameters_attributes'.format(self.entity_name)
        foreman_spec = dict(
            parameters=dict(type='list', elements='dict', options=parameter_ansible_spec, flat_name=parameters_flat_name),
        )
        foreman_spec.update(kwargs.pop('foreman_spec', {}))
        super(ParametersMixin, self).__init__(foreman_spec=foreman_spec, **kwargs)

    def run(self, **kwargs):
        entity = self.lookup_entity('entity')
        if not self.desired_absent:
            if entity and 'parameters' in entity:
                entity['parameters'] = parameters_list_to_str_list(entity['parameters'])
            parameters = self.foreman_params.get('parameters')
            if parameters is not None:
                self.foreman_params['parameters'] = parameters_list_to_str_list(parameters)

        return super(ParametersMixin, self).run(**kwargs)


class NestedParametersMixin(object):
    def __init__(self, **kwargs):
        foreman_spec = dict(
            parameters=dict(type='nested_list', foreman_spec=parameter_foreman_spec),
        )
        foreman_spec.update(kwargs.pop('foreman_spec', {}))
        super(NestedParametersMixin, self).__init__(foreman_spec=foreman_spec, **kwargs)

    def run(self, **kwargs):
        new_entity = super(NestedParametersMixin, self).run(**kwargs)
        if new_entity:
            scope = {'{0}_id'.format(self.entity_name): new_entity['id']}
            self.ensure_scoped_parameters(scope)
        return new_entity

    def ensure_scoped_parameters(self, scope):
        parameters = self.foreman_params.get('parameters')
        if parameters is not None:
            entity = self.lookup_entity('entity')
            if self.state == 'present' or (self.state == 'present_with_defaults' and entity is None):
                if entity:
                    current_parameters = {parameter['name']: parameter for parameter in self.list_resource('parameters', params=scope)}
                else:
                    current_parameters = {}
                desired_parameters = {parameter['name']: parameter for parameter in parameters}

                for name in desired_parameters:
                    desired_parameter = desired_parameters[name]
                    desired_parameter['value'] = parameter_value_to_str(desired_parameter['value'], desired_parameter['parameter_type'])
                    current_parameter = current_parameters.pop(name, None)
                    if current_parameter:
                        if 'parameter_type' not in current_parameter:
                            current_parameter['parameter_type'] = 'string'
                        current_parameter['value'] = parameter_value_to_str(current_parameter['value'], current_parameter['parameter_type'])
                    self.ensure_entity(
                        'parameters', desired_parameter, current_parameter, state="present", foreman_spec=parameter_foreman_spec, params=scope)
                for current_parameter in current_parameters.values():
                    self.ensure_entity(
                        'parameters', None, current_parameter, state="absent", foreman_spec=parameter_foreman_spec, params=scope)


class HostMixin(ParametersMixin):
    def __init__(self, **kwargs):
        foreman_spec = dict(
            compute_resource=dict(type='entity'),
            compute_profile=dict(type='entity'),
            domain=dict(type='entity'),
            subnet=dict(type='entity'),
            subnet6=dict(type='entity', resource_type='subnets'),
            root_pass=dict(no_log=True),
            realm=dict(type='entity'),
            architecture=dict(type='entity'),
            operatingsystem=dict(type='entity'),
            medium=dict(aliases=['media'], type='entity'),
            ptable=dict(type='entity'),
            pxe_loader=dict(choices=['PXELinux BIOS', 'PXELinux UEFI', 'Grub UEFI', 'Grub2 BIOS', 'Grub2 ELF',
                                     'Grub2 UEFI', 'Grub2 UEFI SecureBoot', 'Grub2 UEFI HTTP', 'Grub2 UEFI HTTPS',
                                     'Grub2 UEFI HTTPS SecureBoot', 'iPXE Embedded', 'iPXE UEFI HTTP', 'iPXE Chain BIOS', 'iPXE Chain UEFI']),
            environment=dict(type='entity'),
            puppetclasses=dict(type='entity_list', resolve=False),
            config_groups=dict(type='entity_list'),
            puppet_proxy=dict(type='entity', resource_type='smart_proxies'),
            puppet_ca_proxy=dict(type='entity', resource_type='smart_proxies'),
            openscap_proxy=dict(type='entity', resource_type='smart_proxies'),
            content_source=dict(type='entity', scope=['organization'], resource_type='smart_proxies'),
            lifecycle_environment=dict(type='entity', scope=['organization']),
            kickstart_repository=dict(type='entity', scope=['organization'], resource_type='repositories'),
            content_view=dict(type='entity', scope=['organization']),
        )
        foreman_spec.update(kwargs.pop('foreman_spec', {}))
        required_plugins = kwargs.pop('required_plugins', []) + [
            ('katello', ['content_source', 'lifecycle_environment', 'kickstart_repository', 'content_view']),
            ('openscap', ['openscap_proxy']),
        ]
        mutually_exclusive = kwargs.pop('mutually_exclusive', []) + [['medium', 'kickstart_repository']]
        super(HostMixin, self).__init__(foreman_spec=foreman_spec, required_plugins=required_plugins, mutually_exclusive=mutually_exclusive, **kwargs)


class ForemanAnsibleModule(AnsibleModule):
    """ Baseclass for all foreman related Ansible modules.
        It handles connection parameters and adds the concept of the `foreman_spec`.
        This adds automatic entities resolution based on provided attributes/ sub entities options.
        It adds the following options to foreman_spec 'entity' and 'entity_list' types:
        * search_by (str): Field used to search the sub entity. Defaults to 'name' unless `parent` was set, in which case it defaults to `title`.
        * search_operator (str): Operator used to search the sub entity. Defaults to '='. For fuzzy search use '~'.
        * resource_type (str): Resource type used to build API resource PATH. Defaults to pluralized entity key.
        * resolve (boolean): Defaults to 'True'. If set to false, the sub entity will not be resolved automatically
        * ensure (boolean): Defaults to 'True'. If set to false, it will be removed before sending data to the foreman server.
    """

    def __init__(self, **kwargs):
        # State recording for changed and diff reporting
        self._changed = False
        self._before = defaultdict(list)
        self._after = defaultdict(list)
        self._after_full = defaultdict(list)

        self.foreman_spec, gen_args = _foreman_spec_helper(kwargs.pop('foreman_spec', {}))
        argument_spec = dict(
            server_url=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            validate_certs=dict(type='bool', default=True),
        )
        argument_spec.update(gen_args)
        argument_spec.update(kwargs.pop('argument_spec', {}))
        supports_check_mode = kwargs.pop('supports_check_mode', True)

        self.required_plugins = kwargs.pop('required_plugins', [])

        super(ForemanAnsibleModule, self).__init__(argument_spec=argument_spec, supports_check_mode=supports_check_mode, **kwargs)

        aliases = {alias for arg in argument_spec.values() for alias in arg.get('aliases', [])}
        self.foreman_params = {k: v for (k, v) in self.params.items() if v is not None and k not in aliases}

        self.check_requirements()

        self._foremanapi_server_url = self.foreman_params.pop('server_url')
        self._foremanapi_username = self.foreman_params.pop('username')
        self._foremanapi_password = self.foreman_params.pop('password')
        self._foremanapi_validate_certs = self.foreman_params.pop('validate_certs')

        self.task_timeout = 60
        self.task_poll = 4

        self._thin_default = False
        self.state = 'undefined'

    @contextmanager
    def api_connection(self):
        self.connect()
        yield
        self.exit_json()

    @property
    def changed(self):
        return self._changed

    def set_changed(self):
        self._changed = True

    def _patch_templates_resource_name(self):
        """ Need to support both singular and plural form. The resource was made plural per
             https://projects.theforeman.org/issues/28750
        """
        if 'template' in self.foremanapi.apidoc['docs']['resources']:
            self.foremanapi.apidoc['docs']['resources']['templates'] = self.foremanapi.apidoc['docs']['resources']['template']

    def _patch_location_api(self):
        """This is a workaround for the broken taxonomies apidoc in foreman.
            see https://projects.theforeman.org/issues/10359
        """

        _location_organizations_parameter = {
            u'validations': [],
            u'name': u'organization_ids',
            u'show': True,
            u'description': u'\n<p>Organization IDs</p>\n',
            u'required': False,
            u'allow_nil': True,
            u'allow_blank': False,
            u'full_name': u'location[organization_ids]',
            u'expected_type': u'array',
            u'metadata': None,
            u'validator': u'',
        }
        _location_methods = self.foremanapi.apidoc['docs']['resources']['locations']['methods']

        _location_create = next(x for x in _location_methods if x['name'] == 'create')
        _location_create_params_location = next(x for x in _location_create['params'] if x['name'] == 'location')
        _location_create_params_location['params'].append(_location_organizations_parameter)

        _location_update = next(x for x in _location_methods if x['name'] == 'update')
        _location_update_params_location = next(x for x in _location_update['params'] if x['name'] == 'location')
        _location_update_params_location['params'].append(_location_organizations_parameter)

    def _patch_subnet_rex_api(self):
        """This is a workaround for the broken subnet apidoc in foreman remote execution.
            see https://projects.theforeman.org/issues/19086
        """

        if not self.has_plugin('remote_execution'):
            # the system has no foreman_remote_execution installed, no need to patch
            return

        _subnet_rex_proxies_parameter = {
            u'validations': [],
            u'name': u'remote_execution_proxy_ids',
            u'show': True,
            u'description': u'\n<p>Remote Execution Proxy IDs</p>\n',
            u'required': False,
            u'allow_nil': True,
            u'allow_blank': False,
            u'full_name': u'subnet[remote_execution_proxy_ids]',
            u'expected_type': u'array',
            u'metadata': None,
            u'validator': u'',
        }
        _subnet_methods = self.foremanapi.apidoc['docs']['resources']['subnets']['methods']

        _subnet_create = next(x for x in _subnet_methods if x['name'] == 'create')
        _subnet_create_params_subnet = next(x for x in _subnet_create['params'] if x['name'] == 'subnet')
        _subnet_create_params_subnet['params'].append(_subnet_rex_proxies_parameter)

        _subnet_update = next(x for x in _subnet_methods if x['name'] == 'update')
        _subnet_update_params_subnet = next(x for x in _subnet_update['params'] if x['name'] == 'subnet')
        _subnet_update_params_subnet['params'].append(_subnet_rex_proxies_parameter)

    def check_requirements(self):
        if not HAS_APYPIE:
            self.fail_json(msg=missing_required_lib("apypie"), exception=APYPIE_IMP_ERR)

    @_exception2fail_json(msg="Failed to connect to Foreman server: {0}")
    def connect(self):
        self.foremanapi = apypie.Api(
            uri=self._foremanapi_server_url,
            username=to_bytes(self._foremanapi_username),
            password=to_bytes(self._foremanapi_password),
            api_version=2,
            verify_ssl=self._foremanapi_validate_certs,
        )

        self.ping()

        self._patch_templates_resource_name()
        self._patch_location_api()
        self._patch_subnet_rex_api()

        self.check_required_plugins()

    @_exception2fail_json(msg="Failed to connect to Foreman server: {0}")
    def ping(self):
        return self.foremanapi.resource('home').call('status')

    def _resource(self, resource):
        if resource not in self.foremanapi.resources:
            raise Exception("The server doesn't know about {0}, is the right plugin installed?".format(resource))
        return self.foremanapi.resource(resource)

    def _resource_call(self, resource, *args, **kwargs):
        return self._resource(resource).call(*args, **kwargs)

    def _resource_prepare_params(self, resource, action, params):
        return self._resource(resource).action(action).prepare_params(params)

    @_exception2fail_json(msg='Failed to show resource: {0}')
    def show_resource(self, resource, resource_id, params=None):
        if params is None:
            params = {}
        else:
            params = params.copy()

        params['id'] = resource_id

        params = self._resource_prepare_params(resource, 'show', params)

        return self._resource_call(resource, 'show', params)

    @_exception2fail_json(msg='Failed to list resource: {0}')
    def list_resource(self, resource, search=None, params=None):
        if params is None:
            params = {}
        else:
            params = params.copy()

        if search is not None:
            params['search'] = search
        params['per_page'] = 2 << 31

        params = self._resource_prepare_params(resource, 'index', params)

        return self._resource_call(resource, 'index', params)['results']

    def find_resource(self, resource, search, params=None, failsafe=False, thin=None):
        list_params = {}
        if params is not None:
            list_params.update(params)
        if thin is None:
            thin = self._thin_default
        list_params['thin'] = thin
        results = self.list_resource(resource, search, list_params)
        if len(results) == 1:
            result = results[0]
        elif failsafe:
            result = None
        else:
            if len(results) > 1:
                error_msg = "too many ({0})".format(len(results))
            else:
                error_msg = "no"
            self.fail_json(msg="Found {0} results while searching for {1} with {2}".format(error_msg, resource, search))
        if result:
            if thin:
                result = {'id': result['id']}
            else:
                result = self.show_resource(resource, result['id'], params=params)
        return result

    def find_resource_by(self, resource, search_field, value, **kwargs):
        search = '{0}{1}"{2}"'.format(search_field, kwargs.pop('search_operator', '='), value)
        return self.find_resource(resource, search, **kwargs)

    def find_resource_by_name(self, resource, name, **kwargs):
        return self.find_resource_by(resource, 'name', name, **kwargs)

    def find_resource_by_title(self, resource, title, **kwargs):
        return self.find_resource_by(resource, 'title', title, **kwargs)

    def find_resource_by_id(self, resource, obj_id, **kwargs):
        return self.find_resource_by(resource, 'id', obj_id, **kwargs)

    def find_resources_by_name(self, resource, names, **kwargs):
        return [self.find_resource_by_name(resource, name, **kwargs) for name in names]

    def find_operatingsystem(self, name, failsafe=False, **kwargs):
        result = self.find_resource_by_title('operatingsystems', name, failsafe=True, **kwargs)
        if not result:
            result = self.find_resource_by('operatingsystems', 'title', name, search_operator='~', failsafe=failsafe, **kwargs)
        return result

    def find_puppetclass(self, name, environment=None, params=None, failsafe=False, thin=None):
        if thin is None:
            thin = self._thin_default
        if environment:
            scope = {'environment_id': environment}
        else:
            scope = {}
        if params is not None:
            scope.update(params)
        search = 'name="{0}"'.format(name)
        results = self.list_resource('puppetclasses', search, params=scope)

        # verify that only one puppet module is returned with only one puppet class inside
        # as provided search results have to be like "results": { "ntp": [{"id": 1, "name": "ntp" ...}]}
        # and get the puppet class id
        if len(results) == 1 and len(list(results.values())[0]) == 1:
            result = list(results.values())[0][0]
            if thin:
                return {'id': result['id']}
            else:
                return result

        if failsafe:
            return None
        else:
            self.fail_json(msg='No data found for name="%s"' % search)

    def find_puppetclasses(self, names, **kwargs):
        return [self.find_puppetclass(name, **kwargs) for name in names]

    def scope_for(self, key):
        return {'{0}_id'.format(key): self.lookup_entity(key)['id']}

    def set_entity(self, key, entity):
        self.foreman_params[key] = entity
        self.foreman_spec[key]['resolved'] = True

    def lookup_entity(self, key):
        if key not in self.foreman_params:
            return None

        entity_spec = self.foreman_spec[key]
        if entity_spec.get('resolved') or entity_spec.get('type') not in ('entity', 'entity_list'):
            # Already looked up or not an entity(_list) so nothing to do
            return self.foreman_params[key]

        resource_type = entity_spec['resource_type']
        failsafe = entity_spec.get('failsafe', False)
        thin = entity_spec.get('thin', True)
        params = {}
        try:
            if 'scope' in entity_spec:
                for scope in entity_spec['scope']:
                    params.update(self.scope_for(scope))
        except TypeError:
            if failsafe:
                if entity_spec.get('type') == 'entity':
                    result = None
                else:
                    result = [None for value in self.foreman_params[key]]
            else:
                self.fail_json(msg="Failed to lookup scope {0} while searching for {1}.".format(entity_spec['scope'], resource_type))
        else:
            # No exception happend => scope is in place
            if resource_type == 'operatingsystems':
                if entity_spec.get('type') == 'entity':
                    result = self.find_operatingsystem(self.foreman_params[key], params=params, failsafe=failsafe, thin=thin)
                else:
                    result = [self.find_operatingsystem(value, params=params, failsafe=failsafe, thin=thin) for value in self.foreman_params[key]]
            elif resource_type == 'puppetclasses':
                if entity_spec.get('type') == 'entity':
                    result = self.find_puppetclass(self.foreman_params[key], params=params, failsafe=failsafe, thin=thin)
                else:
                    result = [self.find_puppetclass(value, params=params, failsafe=failsafe, thin=thin) for value in self.foreman_params[key]]
            else:
                if entity_spec.get('type') == 'entity':
                    result = self.find_resource_by(
                        resource=resource_type,
                        value=self.foreman_params[key],
                        search_field=entity_spec.get('search_by', ENTITY_KEYS.get(resource_type, 'name')),
                        search_operator=entity_spec.get('search_operator', '='),
                        failsafe=failsafe, thin=thin, params=params,
                    )
                else:
                    result = [self.find_resource_by(
                        resource=resource_type,
                        value=value,
                        search_field=entity_spec.get('search_by', ENTITY_KEYS.get(resource_type, 'name')),
                        search_operator=entity_spec.get('search_operator', '='),
                        failsafe=failsafe, thin=thin, params=params,
                    ) for value in self.foreman_params[key]]
        self.set_entity(key, result)
        return result

    def auto_lookup_entities(self):
        return [
            self.lookup_entity(key)
            for key, entity_spec in self.foreman_spec.items()
            if entity_spec.get('resolve', True) and entity_spec.get('type') in {'entity', 'entity_list'}
        ]

    def record_before(self, resource, entity):
        self._before[resource].append(entity)

    def record_after(self, resource, entity):
        self._after[resource].append(entity)

    def record_after_full(self, resource, entity):
        self._after_full[resource].append(entity)

    @_exception2fail_json(msg='Failed to ensure entity state: {0}')
    def ensure_entity(self, resource, desired_entity, current_entity, params=None, state=None, foreman_spec=None):
        """Ensure that a given entity has a certain state

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                desired_entity (dict): Desired properties of the entity
                current_entity (dict, None): Current properties of the entity or None if nonexistent
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
                state (dict): Desired state of the entity (optionally taken from the module)
                foreman_spec (dict): Description of the entity structure (optionally taken from module)
            Return value:
                The new current state of the entity
        """
        if state is None:
            state = self.state
        if foreman_spec is None:
            foreman_spec = self.foreman_spec
        else:
            foreman_spec, _dummy = _foreman_spec_helper(foreman_spec)

        updated_entity = None

        self.record_before(resource, _flatten_entity(current_entity, foreman_spec))

        if state == 'present_with_defaults':
            if current_entity is None:
                updated_entity = self._create_entity(resource, desired_entity, params, foreman_spec)
        elif state == 'present':
            if current_entity is None:
                updated_entity = self._create_entity(resource, desired_entity, params, foreman_spec)
            else:
                updated_entity = self._update_entity(resource, desired_entity, current_entity, params, foreman_spec)
        elif state == 'copied':
            if current_entity is not None:
                updated_entity = self._copy_entity(resource, desired_entity, current_entity, params)
        elif state == 'reverted':
            if current_entity is not None:
                updated_entity = self._revert_entity(resource, current_entity, params)
        elif state == 'absent':
            if current_entity is not None:
                updated_entity = self._delete_entity(resource, current_entity, params)
        else:
            self.fail_json(msg='Not a valid state: {0}'.format(state))

        self.record_after(resource, _flatten_entity(updated_entity, foreman_spec))
        self.record_after_full(resource, updated_entity)

        return updated_entity

    def _create_entity(self, resource, desired_entity, params, foreman_spec):
        """Create entity with given properties

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                desired_entity (dict): Desired properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
                foreman_spec (dict): Description of the entity structure
            Return value:
                The new current state if the entity
        """
        payload = _flatten_entity(desired_entity, foreman_spec)
        if not self.check_mode:
            if params:
                payload.update(params)
            return self.resource_action(resource, 'create', payload)
        else:
            fake_entity = desired_entity.copy()
            fake_entity['id'] = -1
            self.set_changed()
            return fake_entity

    def _update_entity(self, resource, desired_entity, current_entity, params, foreman_spec):
        """Update a given entity with given properties if any diverge

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                desired_entity (dict): Desired properties of the entity
                current_entity (dict): Current properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
                foreman_spec (dict): Description of the entity structure
            Return value:
                The new current state if the entity
        """
        payload = {}
        desired_entity = _flatten_entity(desired_entity, foreman_spec)
        current_entity = _flatten_entity(current_entity, foreman_spec)
        for key, value in desired_entity.items():
            foreman_type = foreman_spec[key].get('type', 'str')
            new_value = value
            old_value = current_entity.get(key)
            # String comparison needs extra care in face of unicode
            if foreman_type == 'str':
                old_value = to_native(old_value)
                new_value = to_native(new_value)
            # ideally the type check would happen via foreman_spec.elements
            # however this is not set for flattened entries and setting it
            # confuses _flatten_entity
            elif foreman_type == 'list' and value and isinstance(value[0], dict):
                if 'name' in value[0]:
                    sort_key = 'name'
                else:
                    sort_key = list(value[0].keys())[0]
                new_value = sorted(new_value, key=operator.itemgetter(sort_key))
                old_value = sorted(old_value, key=operator.itemgetter(sort_key))
            if new_value != old_value:
                payload[key] = value
        if payload:
            payload['id'] = current_entity['id']
            if not self.check_mode:
                if params:
                    payload.update(params)
                return self.resource_action(resource, 'update', payload)
            else:
                # In check_mode we emulate the server updating the entity
                fake_entity = current_entity.copy()
                fake_entity.update(payload)
                self.set_changed()
                return fake_entity
        else:
            # Nothing needs changing
            return current_entity

    def _copy_entity(self, resource, desired_entity, current_entity, params):
        """Copy a given entity

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                current_entity (dict): Current properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
            Return value:
                The new current state of the entity
        """
        payload = {
            'id': current_entity['id'],
            'new_name': desired_entity['new_name'],
        }
        if params:
            payload.update(params)
        return self.resource_action(resource, 'copy', payload)

    def _revert_entity(self, resource, current_entity, params):
        """Revert a given entity

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                current_entity (dict): Current properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
            Return value:
                The new current state of the entity
        """
        payload = {'id': current_entity['id']}
        if params:
            payload.update(params)
        return self.resource_action(resource, 'revert', payload)

    def _delete_entity(self, resource, current_entity, params):
        """Delete a given entity

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                current_entity (dict): Current properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
            Return value:
                The new current state of the entity
        """
        payload = {'id': current_entity['id']}
        if params:
            payload.update(params)
        entity = self.resource_action(resource, 'destroy', payload)

        # this is a workaround for https://projects.theforeman.org/issues/26937
        if entity and isinstance(entity, dict) and 'error' in entity and 'message' in entity['error']:
            self.fail_json(msg=entity['error']['message'])

        return None

    def resource_action(self, resource, action, params, options=None, data=None, files=None,
                        ignore_check_mode=False, record_change=True, ignore_task_errors=False):
        resource_payload = self._resource_prepare_params(resource, action, params)
        if options is None:
            options = {}
        try:
            result = None
            if ignore_check_mode or not self.check_mode:
                result = self._resource_call(resource, action, resource_payload, options=options, data=data, files=files)
                is_foreman_task = isinstance(result, dict) and 'action' in result and 'state' in result and 'started_at' in result
                if is_foreman_task:
                    result = self.wait_for_task(result, ignore_errors=ignore_task_errors)
        except Exception as e:
            msg = 'Error while performing {0} on {1}: {2}'.format(
                action, resource, to_native(e))
            self.fail_from_exception(e, msg)
        if record_change and not ignore_check_mode:
            # If we were supposed to ignore check_mode we can assume this action was not a changing one.
            self.set_changed()
        return result

    def wait_for_task(self, task, ignore_errors=False):
        duration = self.task_timeout
        while task['state'] not in ['paused', 'stopped']:
            duration -= self.task_poll
            if duration <= 0:
                self.fail_json(msg="Timout waiting for Task {0}".format(task['id']))
            time.sleep(self.task_poll)

            resource_payload = self._resource_prepare_params('foreman_tasks', 'show', {'id': task['id']})
            task = self._resource_call('foreman_tasks', 'show', resource_payload)
        if not ignore_errors and task['result'] != 'success':
            self.fail_json(msg='Task {0}({1}) did not succeed. Task information: {2}'.format(task['action'], task['id'], task['humanized']['errors']))
        return task

    def fail_from_exception(self, exc, msg):
        fail = {'msg': msg}
        if isinstance(exc, requests.exceptions.HTTPError):
            try:
                response = exc.response.json()
                if 'error' in response:
                    fail['error'] = response['error']
                else:
                    fail['error'] = response
            except Exception:
                fail['error'] = exc.response.text
        self.fail_json(**fail)

    def exit_json(self, changed=False, **kwargs):
        kwargs['changed'] = changed or self.changed
        super(ForemanAnsibleModule, self).exit_json(**kwargs)

    def has_plugin(self, plugin_name):
        try:
            resource_name = _PLUGIN_RESOURCES[plugin_name]
        except KeyError:
            raise Exception("Unknown plugin: {0}".format(plugin_name))
        return resource_name in self.foremanapi.resources

    def check_required_plugins(self):
        missing_plugins = []
        for (plugin, params) in self.required_plugins:
            for param in params:
                if (param in self.foreman_params or param == '*') and not self.has_plugin(plugin):
                    if param == '*':
                        param = 'the whole module'
                    missing_plugins.append("{0} (for {1})".format(plugin, param))
        if missing_plugins:
            missing_msg = "The server is missing required plugins: {0}.".format(', '.join(missing_plugins))
            self.fail_json(msg=missing_msg)


class ForemanStatelessEntityAnsibleModule(ForemanAnsibleModule):
    """ Base class for Foreman entities without a state. To use it, subclass it with the following convention:
        To manage my_entity entity, create the following sub class:

        ```
        class ForemanMyEntityModule(ForemanStatelessEntityAnsibleModule):
            pass
        ```

        and use that class to instanciate module:

        ```
        module = ForemanMyEntityModule(
            argument_spec=dict(
                [...]
            ),
            foreman_spec=dict(
                [...]
            ),
        )
        ```

        It adds the following attributes:
        * entity_key (str): field used to search current entity. Defaults to value provided by `ENTITY_KEYS` or 'name' if no value found.
        * entity_name (str): name of the current entity.
          By default deduce the entity name from the class name (eg: 'ForemanProvisioningTemplateModule' class will produce 'provisioning_template').
        * entity_opts (dict): Dict of options for base entity. Same options can be provided for subentities described in foreman_spec.
        The main entity is referenced with the key `entity` in the `foreman_spec`.
    """

    def __init__(self, **kwargs):
        self.entity_key = kwargs.pop('entity_key', 'name')
        self.entity_name = kwargs.pop('entity_name', self.entity_name_from_class)
        entity_opts = kwargs.pop('entity_opts', {})

        super(ForemanStatelessEntityAnsibleModule, self).__init__(**kwargs)

        if 'resource_type' not in entity_opts:
            entity_opts['resource_type'] = inflector.pluralize(self.entity_name)
        if 'thin' not in entity_opts:
            # Explicit None to trigger the _thin_default mechanism lazily
            entity_opts['thin'] = None
        if 'failsafe' not in entity_opts:
            entity_opts['failsafe'] = True
        if 'search_operator' not in entity_opts:
            entity_opts['search_operator'] = '='
        if 'search_by' not in entity_opts:
            entity_opts['search_by'] = ENTITY_KEYS.get(entity_opts['resource_type'], 'name')

        self.foreman_spec.update(_foreman_spec_helper(dict(
            entity=dict(
                type='entity',
                flat_name='id',
                ensure=False,
                **entity_opts
            ),
        ))[0])

        if 'parent' in self.foreman_spec and self.foreman_spec['parent'].get('type') == 'entity':
            if 'resouce_type' not in self.foreman_spec['parent']:
                self.foreman_spec['parent']['resource_type'] = self.foreman_spec['entity']['resource_type']
            current, parent = split_fqn(self.foreman_params[self.entity_key])
            if isinstance(self.foreman_params.get('parent'), six.string_types):
                if parent:
                    self.fail_json(msg="Please specify the parent either separately, or as part of the title.")
                parent = self.foreman_params['parent']
            elif parent:
                self.foreman_params['parent'] = parent
            self.foreman_params[self.entity_key] = current
            self.foreman_params['entity'] = build_fqn(current, parent)
        else:
            self.foreman_params['entity'] = self.foreman_params.get(self.entity_key)

    @property
    def entity_name_from_class(self):
        """ Convert class name to entity name. The class name must follow folowing name convention:
            * Starts with Foreman or Katello
            * Ends with Module

            This will concert ForemanMyEntityModule class name to my_entity entity name.
            eg:
            * ForemanArchitectureModule => architecture
            * ForemanProvisioningTemplateModule => provisioning_template
            * KatelloProductMudule => product
            * ...
        """
        # Convert current class name from CamelCase to snake_case
        class_name = re.sub(r'(?<=[a-z])[A-Z]|[A-Z](?=[^A-Z])', r'_\g<0>', self.__class__.__name__).lower().strip('_')
        # Get entity name from snake case class name
        return '_'.join(class_name.split('_')[1:-1])


class ForemanEntityAnsibleModule(ForemanStatelessEntityAnsibleModule):
    """ Base class for Foreman entities. To use it, subclass it with the following convention:
        To manage my_entity entity, create the following sub class:

        ```
        class ForemanMyEntityModule(ForemanEntityAnsibleModule):
            pass
        ```

        and use that class to instanciate module:

        ```
        module = ForemanMyEntityModule(
            argument_spec=dict(
                [...]
            ),
            foreman_spec=dict(
                [...]
            ),
        )
        ```

        This adds a `state` parameter to the module and provides the `run` method for the most
        common usecases.
    """

    def __init__(self, **kwargs):
        argument_spec = dict(
            state=dict(choices=['present', 'absent'], default='present'),
        )
        argument_spec.update(kwargs.pop('argument_spec', {}))
        super(ForemanEntityAnsibleModule, self).__init__(argument_spec=argument_spec, **kwargs)

        self.state = self.foreman_params.pop('state')
        self.desired_absent = self.state == 'absent'
        self._thin_default = self.desired_absent

    def run(self, **kwargs):
        """ lookup entities, ensure entity, remove sensitive data, manage parameters.
        """
        if ('parent' in self.foreman_spec and self.foreman_spec['parent'].get('type') == 'entity'
                and self.desired_absent and 'parent' in self.foreman_params and self.lookup_entity('parent') is None):
            # Parent does not exist so just exit here
            return None
        if not self.desired_absent:
            self.auto_lookup_entities()
        entity = self.lookup_entity('entity')

        if not self.desired_absent:
            updated_key = "updated_" + self.entity_key
            if entity and updated_key in self.foreman_params:
                self.foreman_params[self.entity_key] = self.foreman_params.pop(updated_key)

        params = kwargs.get('params', {})
        entity_scope = self.foreman_spec['entity'].get('scope')
        if entity_scope:
            for scope in entity_scope:
                params.update(self.scope_for(scope))
        new_entity = self.ensure_entity(self.foreman_spec['entity']['resource_type'], self.foreman_params, entity, params=params)
        new_entity = self.remove_sensitive_fields(new_entity)

        return new_entity

    def remove_sensitive_fields(self, entity):
        """ Set fields with 'no_log' option to None """
        if entity:
            for blacklisted_field in self.blacklisted_fields:
                entity[blacklisted_field] = None
        return entity

    def exit_json(self, **kwargs):
        if 'diff' not in kwargs and (self._before or self._after):
            kwargs['diff'] = {'before': self._before,
                              'after': self._after}
        if 'entity' not in kwargs and self._after_full:
            kwargs['entity'] = self._after_full
        super(ForemanEntityAnsibleModule, self).exit_json(**kwargs)

    @property
    def blacklisted_fields(self):
        return [key for key, value in self.foreman_spec.items() if value.get('no_log', False)]


class ForemanTaxonomicAnsibleModule(TaxonomyMixin, ForemanAnsibleModule):
    pass


class ForemanTaxonomicEntityAnsibleModule(TaxonomyMixin, ForemanEntityAnsibleModule):
    pass


class ForemanScapDataStreamModule(ForemanTaxonomicEntityAnsibleModule):
    def __init__(self, **kwargs):
        foreman_spec = dict(
            original_filename=dict(type='str'),
            scap_file=dict(type='path'),
        )
        foreman_spec.update(kwargs.pop('foreman_spec', {}))
        super(ForemanScapDataStreamModule, self).__init__(foreman_spec=foreman_spec, **kwargs)

    def run(self, **kwargs):
        entity = self.lookup_entity('entity')

        if not self.desired_absent:
            if not entity and 'scap_file' not in self.foreman_params:
                self.fail_json(msg="Content of scap_file not provided. XML containing SCAP content is required.")

            if 'scap_file' in self.foreman_params and 'original_filename' not in self.foreman_params:
                self.foreman_params['original_filename'] = os.path.basename(self.foreman_params['scap_file'])

            if 'scap_file' in self.foreman_params:
                with open(self.foreman_params['scap_file']) as input_file:
                    self.foreman_params['scap_file'] = input_file.read()

            if entity and 'scap_file' in self.foreman_params:
                digest = hashlib.sha256(self.foreman_params['scap_file'].encode("utf-8")).hexdigest()
                # workaround for https://projects.theforeman.org/issues/29409
                digest_stripped = hashlib.sha256(self.foreman_params['scap_file'].strip().encode("utf-8")).hexdigest()
                if entity['digest'] in [digest, digest_stripped]:
                    self.foreman_params.pop('scap_file')

        super(ForemanScapDataStreamModule, self).run(**kwargs)


class KatelloAnsibleModule(KatelloMixin, ForemanAnsibleModule):
    pass


class KatelloEntityAnsibleModule(KatelloMixin, ForemanEntityAnsibleModule):
    def __init__(self, **kwargs):
        entity_opts = kwargs.pop('entity_opts', {})
        if 'scope' not in entity_opts:
            entity_opts['scope'] = ['organization']
        elif 'organization' not in entity_opts['scope']:
            entity_opts['scope'].append('organization')
        super(KatelloEntityAnsibleModule, self).__init__(entity_opts=entity_opts, **kwargs)


def _foreman_spec_helper(spec):
    """Extend an entity spec by adding entries for all flat_names.
    Extract ansible compatible argument_spec on the way.
    """
    foreman_spec = {}
    argument_spec = {}

    _FILTER_SPEC_KEYS = {
        'ensure',
        'failsafe',
        'flat_name',
        'foreman_spec',
        'resolve',
        'resource_type',
        'scope',
        'search_by',
        'search_operator',
        'thin',
        'type',
    }
    _VALUE_SPEC_KEYS = {
        'ensure',
        'type',
    }
    _ENTITY_SPEC_KEYS = {
        'failsafe',
        'resolve',
        'resource_type',
        'scope',
        'search_by',
        'search_operator',
        'thin',
    }

    # _foreman_spec_helper() is called before we call check_requirements() in the __init__ of ForemanAnsibleModule
    # and thus before the if HAS APYPIE check happens.
    # We have to ensure that apypie is available before using it.
    # There is two cases where we can call _foreman_spec_helper() without apypie available:
    # * When the user calls the module but doesn't have the right Python libraries installed.
    #   In this case nothing will works and the module will warn teh user to install the required library.
    # * When Ansible generates docs from the argument_spec. As the inflector is only used to build foreman_spec and not argument_spec,
    #   This is not a problem.
    #
    # So in conclusion, we only have to verify that apypie is available before using it.
    # Lazy evaluation helps there.
    for key, value in spec.items():
        foreman_value = {k: v for (k, v) in value.items() if k in _VALUE_SPEC_KEYS}
        argument_value = {k: v for (k, v) in value.items() if k not in _FILTER_SPEC_KEYS}

        foreman_type = value.get('type')
        flat_name = value.get('flat_name')

        if foreman_type == 'entity':
            if not flat_name:
                flat_name = '{0}_id'.format(key)
            foreman_value['resource_type'] = HAS_APYPIE and inflector.pluralize(key)
            foreman_value.update({k: v for (k, v) in value.items() if k in _ENTITY_SPEC_KEYS})
        elif foreman_type == 'entity_list':
            argument_value['type'] = 'list'
            argument_value['elements'] = value.get('elements', 'str')
            if not flat_name:
                flat_name = '{0}_ids'.format(HAS_APYPIE and inflector.singularize(key))
            foreman_value['resource_type'] = key
            foreman_value.update({k: v for (k, v) in value.items() if k in _ENTITY_SPEC_KEYS})
        elif foreman_type == 'nested_list':
            argument_value['type'] = 'list'
            argument_value['elements'] = 'dict'
            _dummy, argument_value['options'] = _foreman_spec_helper(value['foreman_spec'])
            foreman_value['ensure'] = value.get('ensure', False)
        elif foreman_type:
            argument_value['type'] = foreman_type

        if flat_name:
            foreman_value['flat_name'] = flat_name
            foreman_spec[flat_name] = {}
            # When translating to a flat name, the flattened entry should get the same "type"
            # as Ansible expects so that comparison still works for non-strings
            if argument_value.get('type') is not None:
                foreman_spec[flat_name]['type'] = argument_value['type']

        foreman_spec[key] = foreman_value

        if foreman_type != 'invisible':
            argument_spec[key] = argument_value

    return foreman_spec, argument_spec


def _flatten_entity(entity, foreman_spec):
    """Flatten entity according to spec"""
    result = {}
    if entity is None:
        entity = {}
    for key, value in entity.items():
        if key in foreman_spec and foreman_spec[key].get('ensure', True) and value is not None:
            spec = foreman_spec[key]
            flat_name = spec.get('flat_name', key)
            property_type = spec.get('type', 'str')
            if property_type == 'entity':
                result[flat_name] = value['id']
            elif property_type == 'entity_list':
                result[flat_name] = sorted(val['id'] for val in value)
            else:
                result[flat_name] = value
    return result


# Helper for (global, operatingsystem, ...) parameters
def parameter_value_to_str(value, parameter_type):
    """Helper to convert the value of parameters to string according to their parameter_type."""
    if parameter_type in ['real', 'integer']:
        parameter_string = str(value)
    elif parameter_type in ['array', 'hash', 'yaml', 'json']:
        parameter_string = json.dumps(value, sort_keys=True)
    else:
        parameter_string = value
    return parameter_string


# Helper for converting lists of parameters
def parameters_list_to_str_list(parameters):
    filtered_params = []
    for param in parameters:
        new_param = {k: v for (k, v) in param.items() if k in parameter_ansible_spec.keys()}
        new_param['value'] = parameter_value_to_str(new_param['value'], new_param['parameter_type'])
        filtered_params.append(new_param)
    return filtered_params


# Helper for templates
def parse_template(template_content, module):
    if not HAS_PYYAML:
        module.fail_json(msg=missing_required_lib("PyYAML"), exception=PYYAML_IMP_ERR)

    try:
        template_dict = {}
        data = re.search(
            r'<%#([^%]*([^%]*%*[^>%])*%*)%>', template_content)
        if data:
            datalist = data.group(1)
            if datalist[-1] == '-':
                datalist = datalist[:-1]
            template_dict = yaml.safe_load(datalist)
        # No metadata, import template anyway
        template_dict['template'] = template_content
    except Exception as e:
        module.fail_json(msg='Error while parsing template: ' + to_native(e))
    return template_dict


def parse_template_from_file(file_name, module):
    try:
        with open(file_name) as input_file:
            template_content = input_file.read()
            template_dict = parse_template(template_content, module)
    except Exception as e:
        module.fail_json(msg='Error while reading template file: ' + to_native(e))
    return template_dict


# Helper for titles
def split_fqn(title):
    """ Split fully qualified name (title) in name and parent title """
    fqn = title.split('/')
    if len(fqn) > 1:
        name = fqn.pop()
        return (name, '/'.join(fqn))
    else:
        return (title, None)


def build_fqn(name, parent=None):
    if parent:
        return "%s/%s" % (parent, name)
    else:
        return name


# Helper for puppetclasses
def ensure_puppetclasses(module, entity_type, entity, expected_puppetclasses=None):
    puppetclasses_resource = '{0}_classes'.format(entity_type)
    if expected_puppetclasses:
        expected_puppetclasses = module.find_puppetclasses(expected_puppetclasses, environment=entity['environment_id'], thin=True)
    current_puppetclasses = entity.pop('puppetclass_ids', [])
    if expected_puppetclasses:
        for puppetclass in expected_puppetclasses:
            if puppetclass['id'] in current_puppetclasses:
                current_puppetclasses.remove(puppetclass['id'])
            else:
                payload = {'{0}_id'.format(entity_type): entity['id'], 'puppetclass_id': puppetclass['id']}
                module.ensure_entity(puppetclasses_resource, {}, None, params=payload, state='present', foreman_spec={})
        if len(current_puppetclasses) > 0:
            for leftover_puppetclass in current_puppetclasses:
                module.ensure_entity(puppetclasses_resource, {}, {'id': leftover_puppetclass}, {'hostgroup_id': entity['id']}, state='absent', foreman_spec={})


# Helper constants
OS_LIST = ['AIX',
           'Altlinux',
           'Archlinux',
           'Coreos',
           'Debian',
           'Freebsd',
           'Gentoo',
           'Junos',
           'NXOS',
           'Rancheros',
           'Redhat',
           'Solaris',
           'Suse',
           'Windows',
           'Xenserver',
           ]
