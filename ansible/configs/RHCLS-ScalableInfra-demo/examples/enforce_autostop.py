# A Ravello SDK example for enforcing a short auto-stop for all published applications 
# in the account
# 
# To use, edit the relevant variables (or extract them to command line param),
# and run enforce_autostop()
#
# Copyright 2011-2015 Ravello Systems, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

from ravello_sdk import *
import datetime

MAX_ALLOWED_EXPIRATION_PERIOD_IN_SEC = 60*60*2 # 2 hours
USERNAME = 'wile.e.coyote@acme.com'
PASSWORD = 'PA$$W0RD'

def enforce_autostop():
    client = RavelloClient()
    client.login(USERNAME, PASSWORD)
    
    apps = client.get_applications()
    for app in apps:
        if app['published'] == False:
            continue
        deployment = app['deployment']
        if deployment['totalActiveVms'] == 0:
            continue
        if not app.has_key('nextStopTime'):
            # no expiration set for this application, set it
            set_expiration(client, app)
        else:
            expiration_time = datetime.datetime.utcfromtimestamp(app['nextStopTime'] / 1e3)
            # if expiration_time (utc) is too long into the future, set_expiration correctly
            if should_expire_app(expiration_time, app):
                set_expiration(client, app)

def should_expire_app(current_expiration_time_utc, app):
    now = datetime.datetime.utcnow()
    delta = current_expiration_time_utc - now
    if delta.total_seconds() > MAX_ALLOWED_EXPIRATION_PERIOD_IN_SEC:
        return True
    return False

def set_expiration(client, app):
    print "setting expiration for ", app['name']
    client.set_application_expiration(app, {'expirationFromNowSeconds': MAX_ALLOWED_EXPIRATION_PERIOD_IN_SEC})