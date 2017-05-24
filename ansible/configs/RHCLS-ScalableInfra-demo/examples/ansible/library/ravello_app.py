#!/usr/bin/python
#test
# (c) 2015, ravellosystems
# 
# author zoza
#
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

######################################################################


try:
    from ravello_sdk import *

except ImportError:
    print "failed=True msg='ravello sdk required for this module'"
    sys.exit(1)



DOCUMENTATION = '''
---
module: ravello_app
short_description: Create/delete/start/stop an application in ravellosystems
description:
     - Create/delete/start/stop an application in ravellosystems and wait for it (optionally) to be 'running'
     - list state will return a fqdn list of exist application hosts with their external services
options:
  state:
    description:
     - Indicate desired state of the target.
    default: present
    choices: ['present', 'started', 'absent', 'stopped','list']
  username:
     description:
      - ravello username
  password:
    description:
     - ravello password

  service_name: 
    description:
     - Supplied Service name for list state 
    default: ssh

  name:
    description:
     - application name
  description:
    description:
     - application description
  blueprint_id:
    description:
     - create app, based on this blueprint

  #publish options
  cloud:
    description:
     - cloud to publish
  region:
    description:
     - region to publish
  publish_optimization:
    default: cost
    choices: ['cost', 'performance']

  application_ttl:
    description:
     - application autostop in mins
    default: -1 # never
  wait
    description:
     - Wait for the app to be in state 'running' before returning.
    default: True
    choices: [ True, False ]
  wait_timeout:
    description:
     - How long before wait gives up, in seconds.
    default: 600
'''

EXAMPLES = '''
# Create app, based on blueprint, start it and wait for started
- local_action:
    module: ravello_app
    username: user@ravello.com
    password: password
    name: 'my-application-name'
    description: 'app desc'
    blueprint_id: '2452'
    wait: True
    wait_timeout: 600
    state: present

# Create app, based on blueprint
- local_action:
    module: ravello_app
    username: user@ravello.com
    password: password
    name: 'my-application-name'
    description: 'app desc'
    publish_optimization: performance
    cloud:AMAZON
    region: Oregon
    state: present

# List application example
- local_action:
    module: ravello_app
    name: 'my-application-name'
    service_name: 'ssh'
    state: list

# Delete application example
- local_action:
    module: ravello_app
    name: 'my-application-name'
    state: absent

# Delete application example from matryoshka (nested)
- local_action:
    module: ravello_app
    url: 'https://matryoshka.com/api/v1' or https://matryoshka.com/services
    name: 'my-application-name'
    state: absent
'''

# import module snippets
from ansible.module_utils.basic import *
import ansible
import os
import functools
import logging
import io
import datetime
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
log_capture_string = io.BytesIO()

def main():

    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.DEBUG)
    ### Optionally add a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    ### Add the console handler to the logger
    logger.addHandler(ch)    
    module = AnsibleModule(
        argument_spec=dict(
            # for nested babu only
            url=dict(required=False, type='str'),

            state=dict(default='present', choices=['present', 'started', 'absent', 'stopped', 'list', 'blueprint']),

            username=dict(required=False, type='str'),
            password=dict(required=False, type='str'),

            name=dict(required=True, type='str'),
            description=dict(required=False, type='str'),
            blueprint_id=dict(required=False, type='str'),

            cloud=dict(required=False, type='str'),
            region=dict(required=False, type='str'),
            publish_optimization=dict(default='cost', choices=['cost', 'performance']),
            application_ttl=dict(default='-1', type='int'),
            
            service_name=dict(default='ssh', type='str'),

            blueprint_description=dict(required=False, type='str'),
            blueprint_name=dict(required=False, type='str'),
            
            wait=dict(type='bool', default=True ,choices=BOOLEANS),
            wait_timeout=dict(default=1200, type='int')
        )
    )
    try:
        username = module.params.get('username', os.environ.get('RAVELLO_USERNAME', None)) 
        password = module.params.get('password', os.environ.get('RAVELLO_PASSWORD', None))
        
        client = RavelloClient(username, password, module.params.get('url'))
        
        if module.params.get('state') == 'present':
          create_app_and_publish(client, module)
        elif module.params.get('state') == 'absent':
          action_on_app(module, client, client.delete_application, lambda: None, 'Deleted')
        elif module.params.get('state') == 'started':
          action_on_app(module, client, client.start_application, functools.partial(_wait_for_state,client,'STARTED',module), 'Started')
        elif module.params.get('state') == 'stopped':
          action_on_app(module, client, client.stop_application, functools.partial(_wait_for_state,client,'STOPPED',module), 'Stopped')
        elif module.params.get('state') == 'list':
          list_app(client, module)
        elif module.params.get('state') == 'blueprint':
          action_on_blueprint(module, client, client.create_blueprint)
    except Exception, e:
        log_contents = log_capture_string.getvalue()
        log_capture_string.close()
        module.fail_json(msg = '%s' % e,stdout='%s' % log_contents)

def _wait_for_state(client, state, module):

    if module.params.get('wait') == False:
        return
    
    wait_timeout = module.params.get('wait_timeout')
    app_id = 0
    wait_till = time.time() + wait_timeout
    while wait_till > time.time():
        if app_id > 0:
            app = client.get_application(app_id)
        else:
            app =  client.get_application_by_name(module.params.get('name'))
            app_id = app['id']

        states = list(set((vm['state'] for vm in app.get('deployment', {}).get('vms', []))))
        if "ERROR" in states:
            log_contents = log_capture_string.getvalue()
            log_capture_string.close()
            module.fail_json(msg = 'Vm got ERROR state',stdout='%s' % log_contents)
        if len(states) == 1 and states[0] == state:
            return
        time.sleep(10)
        
    log_contents = log_capture_string.getvalue()
    log_capture_string.close()
    module.fail_json(msg = 'Timed out waiting for async operation to complete.',  stdout='%s' % log_contents)

def is_wait_for_external_service(supplied_service,module):
    return supplied_service['name'].lower() == module.params.get('service_name').lower() and supplied_service['external'] == True

def get_list_app_vm_result(app, vm, module):
   
    for supplied_service in vm['suppliedServices']:            
        if is_wait_for_external_service(supplied_service, module):
            for network_connection in vm['networkConnections']:
                if network_connection['ipConfig']['id'] == supplied_service['ipConfigLuid']:
                    dest = network_connection['ipConfig'].get('fqdn')
                    port = int(supplied_service['externalPort'].split(",")[0].split("-")[0])
                    return (dest,port)
                
def list_app(client, module):
    try:
        app_name = module.params.get("name")
        app = client.get_application_by_name(app_name)
        
        results = []
        
        for vm in app['deployment']['vms']:
            if vm['state'] != "STARTED":
                continue
            (dest,port) = get_list_app_vm_result(app, vm, module)
            results.append({'host': dest, 'port': port})
        log_contents = log_capture_string.getvalue()
        log_capture_string.close()
        module.exit_json(changed=True, name='%s' % app_name, results='%s' % results,stdout='%s' % log_contents)
    except Exception, e:
        log_contents = log_capture_string.getvalue()
        log_capture_string.close()
        module.fail_json(msg = '%s' % e,stdout='%s' % log_contents)

def action_on_blueprint(module, client, runner_func):
    try:
        app_name = module.params.get("name")
        app = client.get_application_by_name(app_name)
        blueprint_name = module.params.get("blueprint_name")
        blueprint_description = module.params.get("blueprint_description")
        blueprint_dict = {"applicationId":app['id'], "blueprintName":blueprint_name, "offline": True,  "description":blueprint_description }
        blueprint_id=((runner_func(blueprint_dict))['_href'].split('/'))[2]
        log_contents = log_capture_string.getvalue()
        log_capture_string.close()
        module.exit_json(changed=True, name='%s' % app_name, blueprint_id='%s' % blueprint_id)

    except Exception, e:
        log_contents = log_capture_string.getvalue()
        log_capture_string.close()
        module.fail_json(msg = '%s' % e,stdout='%s' % log_contents)        
     
def action_on_app(module, client, runner_func, waiter_func, action):
    try:
        app_name = module.params.get("name")
        app = client.get_application_by_name(app_name)
        runner_func(app['id'])
        waiter_func()
        log_contents = log_capture_string.getvalue()
        log_capture_string.close()
        module.exit_json(changed=True, name='%s application: %s' %(action, app_name),stdout='%s' % log_contents)
    except Exception, e:
        log_contents = log_capture_string.getvalue()
        log_capture_string.close()
        module.fail_json(msg = '%s' % e,stdout='%s' % log_contents)
    
def create_app_and_publish(client, module):
    #validation
    if not module.params.get("blueprint_id"):
            module.fail_json(msg='Must supply a blueprint_id', changed=False)
    if 'performance' == module.params.get("publish_optimization"):
        if not module.params.get("cloud"):
            module.fail_json(msg='Must supply a cloud when publish optimization is performance', changed=False)
        if not module.params.get("region"):
            module.fail_json(msg='Must supply a region when publish optimization is performance', changed=False)
        
    app = {'name': module.params.get("name"), 'description': module.params.get("description",''), 'baseBlueprintId': module.params.get("blueprint_id")}    
    app = client.create_application(app)
    
    req = {}
    if 'performance' == module.params.get("publish_optimization"):
        req = {'id': app['id'] ,'preferredCloud': module.params.get("cloud"),'preferredRegion': module.params.get("region"), 'optimizationLevel': 'PERFORMANCE_OPTIMIZED'}
    
    ttl=module.params.get("application_ttl")
    if ttl != -1:
        ttl =ttl * 60
        exp_req = {'expirationFromNowSeconds': ttl}
        client.set_application_expiration(app,exp_req)
        
    client.publish_application(app, req)

    _wait_for_state(client,'STARTED',module)
    log_contents = log_capture_string.getvalue()
    log_capture_string.close()
    module.exit_json(changed=True, name='Created and published application: %s .' % module.params.get("name"),stdout='%s' % log_contents)

main()
