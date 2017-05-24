#!/usr/bin/env python
# A Ravello SDK example for creating and publishing applications from a blueprint
# 
# Copyright 2011-2016 Ravello Systems, Inc.
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

import os
import base64
import getpass
import logging
import logging.handlers
from ravello_sdk import *

def get_credentials():
	with open(os.path.expanduser("~/.ravello_login"),"r") as pf:
		username = pf.readline().strip()
		encrypted_password = pf.readline().strip()
	password = base64.b64decode(encrypted_password).decode()
	return username,password

def get_user_credentials(username):
 
	password = None

	if username:
		password = getpass.getpass('Enter a Password: ')
	else:
		#read user credentials from .ravello_login file in user HOMEDIR
		username,password = get_credentials()

	if not username or not password:
		log.error('User credentials are not set')
		print('Error: User credentials are not set')
		return None,None

	return username,password

def initlog(log_file):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logpath=os.path.join(os.getcwd(),log_file)
        handler = logging.handlers.RotatingFileHandler(logpath, maxBytes=1048576, backupCount=10)
        fmt = '%(asctime)s: %(filename)-20s %(levelname)-8s %(message)s'
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)

def connect(username, password):
        client = RavelloClient()
        try:
                client.login(username, password)
        except Exception as e:
                sys.stderr.write('Error: {!s}\n'.format(e))
                log.error('Invalid user credentials, username {0}'.format(username))
                print('Error: Invalid user credentials, username {0}'.format(username))
                return None
        return client

def get_app_id(app_name,client):
        app_id=0
        for app in client.get_applications():
                if app['name'].lower() == app_name.lower():
                        app_id = app['id']
                        break
        return app_id

