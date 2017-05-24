#!/usr/bin/env python3
#
# startstop.py: example program that start and stops applications that do not
# need to run all the time. The program needs to be run from cron, and expects
# a configuration file in ~/.startstop/config.js.
#
# Copyright 2012-2014 Ravello Systems, Inc.
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

from __future__ import absolute_import, print_function

import os
import sys
import logging
import logging.handlers
import errno
import json
import textwrap

from argparse import ArgumentParser
from datetime import datetime
from contextlib import closing
from ravello_sdk import *

log = logging.getLogger('main')
example_cfg = textwrap.dedent("""\
    {
      "expire": 1440,
      "applications": [
        {
          "id": 1234,
          "name": "My Application",
          "username": "user@example.com",
          "password": "Passw0rd",
          "active": [[0, 1440]]
        }
      ]
    }
""")

def homedir():
    """Return the user's home directory."""
    home = os.environ.get('HOME')
    if home is None:
        pw = pwd.getpwuid(os.getuid())
        home = pw.pw_dir
    return home

def appdir():
    """Return our application directory."""
    return os.path.join(homedir(), '.startstop')

def appfile(name):
    """Return the path to a file in the application directory."""
    return os.path.join(appdir(), name)

def mkparser():
    """Create the command-line parser."""
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-l', '--log-file', action='store_true')
    parser.add_argument('-n', '--dry-run', action='store_true')
    return parser

def initapp(args):
    """Initialize the application directory."""
    dirname = appdir()
    try:
        st = os.stat(dirname)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
        os.mkdir(dirname)
        print('Created: {}'.format(dirname))
    cfgname = appfile('config.js.example')
    try:
        st = os.stat(cfgname)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
        with open(cfgname, 'w') as fout:
            fout.write(example_cfg)
        print('Created: {}'.format(cfgname))

def initlog(args):
    """Initialize the logger."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
    if args.log_file or not sys.stdout.isatty():
        logname = os.path.join(appdir(), 'logfile.txt')
        handler = logging.handlers.RotatingFileHandler(logname)
        fmt = '%(asctime)s: %(levelname)s %(message)s'
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
    fmt = '%(levelname)s %(message)s'
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)

def readcfg():
    """Read our configuration file."""
    cfgname = appfile('config.js')
    with open(cfgname) as fin:
        cfg = json.load(fin)
    return cfg

def active(intervals, now):
    """Return True if the minute of the week of *dt* is in *intervals*."""
    mow = now.weekday() * 24 * 60 + now.hour * 60 + now.minute
    for start,end in intervals:
        if start <= mow < end:
            return True
    return False

def connect(username, password):
    """Connect to the API, return a `RavelloClient` instance."""
    client = RavelloClient()
    client.connect()
    client.login(username, password)
    return client

def startstop(cfg, req, now, dry_run):
    """Start or stop an application, if needed."""
    client = connect(req['username'], req['password'])
    with closing(client):
        app = client.get_application(req['id'])
        if app is None:
            log.error('no such application: {}'.format(app['id']))
            return False
        status = application_state(app)
        target = 'STARTED' if active(req['active'], now) else 'STOPPED'
        log.info('need transition from {} => {}'.format(status, target))
        if not isinstance(status, list):
            status = [status] 
        if status == [target]:
            log.info('no action needed')
        elif dry_run:
            log.info('dry-run, not making any changes')
        elif 'STARTING' in status or 'STOPPING' in status:
            log.info('action in progress, not making any changes')
        elif target == 'STARTED' and 'STOPPED' in status:
            exp = {'expirationFromNowSeconds': 60*cfg['expire']}
            client.set_application_expiration(app['id'], exp)
            client.start_application(app['id'])
            log.info('application started')
        elif target == 'STOPPED' and 'STARTED' in status:
            client.stop_application(app['id'])
            log.info('application stopped')
        else:
            log.error('don\'t know how to get from {} to {}'.format(status, target))
            return False
    return True

def main():
    parser = mkparser()
    args = parser.parse_args()
    initapp(args)
    initlog(args)
    cfg = readcfg()
    now = datetime.utcnow()
    for req in cfg['applications']:
        log.info('processing: {} (id = {})'.format(req['name'], req['id']))
        try:
            success = startstop(cfg, req, now, args.dry_run)
        except Exception as e:
            if args.debug:
                log.exception('uncaught exception')
            else:
                log.error(str(e))
            success = False
        if success:
            log.info('success: {}'.format(req['name']))
        else:
            log.error('failure: {}'.format(req['name']))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        sys.stderr.write('Error: {!s}\n'.format(e))
