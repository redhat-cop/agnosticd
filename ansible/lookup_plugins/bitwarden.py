# (c) 2022 Johnathan Kupferer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
  lookup: bitwarden
  author: Johnathan Kupferer <jkupfere@redhat.com>
  version_added: "2.9"
  short_description: Read items from Bitwarden
  description:
  - This lookup returns items fetched from Bitwarden.
  - This lookup my be called either with bitwarden already authenticated and the BW_SESSION environment variable set or by passing client_id, client_secret, and master_password to open a temporary session.
  options:
    _terms:
      description: Item ids to fetch
      required: True
    bitwardencli_appdata_dir:
      description:
      - BITWARDENCLI_APPDATA_DIR value to use with bitwarden cli.
      type: string
      env:
      - name: BITWARDENCLI_APPDATA_DIR
      ini:
      - section: bitwarden
        key: bitwardencli_appdata_dir
    bw_cli:
      description:
      - Path for bitwarden cli command.
      - If not provided then the environment PATH will be used to find `bw`.
      type: string
      ini:
      - section: bitwarden
        key: cli
    bw_session:
      description:
      - Bitwarden session
      type: string
      env:
      - name: BW_SESSION
      ini:
      - section: bitwarden
        key: cli
    client_id:
      description:
      - Client ID for Bitwarden API access.
      type: string
      env:
      - name: BW_CLIENTID
      ini:
      - section: bitwarden
        key: client_id
    client_secret:
      description:
      - Client Secret for Bitwarden API access.
      type: string
      env:
      - name: BW_CLIENTSECRET
      ini:
      - section: bitwarden
        key: client_secret
    master_password:
      description:
      - Master password for Bitwarden user.
      type: string
      env:
      - name: BW_PASSWORD
      ini:
      - section: bitwarden
        key: master_password
  notes:
  - Returns ...
"""

EXAMPLES="""
- name: Set api_access from Bitwarden when CLI is already unlocked
  set_fact:
    api_access: "{{ lookup('bitwarden', 'api-access-credentials') }}.login"

- name: Set api_access from Bitwarden including Bitwarden login and unlock
  set_fact:
    api_access: >-
      {{
        lookup(
          'bitwarden', 'api-access-credentials',
           client_id = bitwarden_client_id,
           client_secret = bitwarden_client_secret,
           master_password = bitwarden_master_password
        ).login
      }}
"""

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
import json
import os
import requests
import shutil
import subprocess
import tempfile

display = Display()

class BitwardenCLI:
    def __init__(
        self,
        bitwardencli_appdata_dir = None,
        bw_cli = None,
        bw_session = None,
        client_id = None,
        client_secret = None,
        master_password = None,
    ):
        if bw_cli:
            self.bw_cli = bw_cli,
        else:
            self.bw_cli = shutil.which('bw')

        self.bw_session = bw_session

        # If a directory is not specified, then create a temporary directory
        # that will be automatically cleaned up for security and to prevent
        # conflicts.
        if bitwardencli_appdata_dir:
            self.bitwardencli_appdata_dir = bitwardencli_appdata_dir
        elif not self.bw_session or (client_id and client_secret and master_password):
            display.vvv('Using temporary directory for BITWARDENCLI_APPDATA_DIR')
            self.tempdir = tempfile.TemporaryDirectory()
            self.bitwardencli_appdata_dir = self.tempdir.name
        else:
            self.bitwardencli_appdata_dir = None

        # Check Bitwarden status and login and unlock as needed
        status = self.status()
        if status['status'] == 'unauthenticated':
            if not client_id or not client_secret or not master_password:
                raise AnsibleLookupError("Bitwarden is unauthenticated. Bitwarden CLI must be either pre-authenticated with the BW_SESSION environment variable set and all of client_id, client_secret, or master_password must be provided")
            self.login(client_id=client_id, client_secret=client_secret)
            self.bw_session = self.unlock(master_password=master_password)
        elif status['status'] == 'locked':
            if not master_password:
                raise AnsibleLookupError("Bitwarden is locked. Bitwarden session in environment BW_SESSION must be unlocked or master_password must be provided.")
            self.bw_session = self.unlock(master_password=master_password)
        elif status['status'] != 'unlocked':
            raise AnsibleLookupError("Cannot handle Bitwarden status {}".format(status['status']))

    def make_bw_env(self, **setenv):
        bw_env = setenv.copy()
        if self.bitwardencli_appdata_dir:
            bw_env['BITWARDENCLI_APPDATA_DIR'] = self.bitwardencli_appdata_dir
        else:
            for envvar in ('HOME', 'APPDATA', 'XDG_CONFIG_HOME'):
                if envvar in os.environ:
                    bw_env[envvar] = os.environ[envvar]
        return bw_env

    def get_item(self, item_id):
        display.vvv('Bitwarden get item {}'.format(item_id))
        bw_env = self.make_bw_env(BW_SESSION=self.bw_session)
        bw_cmd = subprocess.run(
            [self.bw_cli, 'get', 'item', item_id],
            capture_output = True,
            env = bw_env,
        )
        if bw_cmd.returncode != 0:
            raise AnsibleLookupError("Failed to fetch item from Bitwarden: " + bw_cmd.stderr.decode('utf-8'))
        return json.loads(bw_cmd.stdout)

    def login(self, client_id, client_secret):
        display.vvv('Bitwarden login with client_id {}'.format(client_id))
        bw_env = self.make_bw_env(BW_CLIENTID=client_id, BW_CLIENTSECRET=client_secret)
        bw_cmd = subprocess.run(
            [self.bw_cli, 'login', '--apikey'],
            capture_output = True,
            env = bw_env,
        )
        if bw_cmd.returncode != 0:
            raise AnsibleLookupError("Bitwarden login failed: " + bw_cmd.stderr.decode('utf-8'))

    def status(self):
        bw_env = self.make_bw_env()
        if self.bw_session:
            bw_env['BW_SESSION'] = self.bw_session
        bw_cmd = subprocess.run(
            [self.bw_cli, 'status'],
            capture_output = True,
            env = bw_env,
        )
        if bw_cmd.returncode != 0:
            raise AnsibleLookupError("Bitwarden status failed: " + bw_cmd.stderr.decode('utf-8'))
        display.vvv('Bitwarden status: ' + bw_cmd.stdout.decode('utf-8'))
        return json.loads(bw_cmd.stdout)

    def unlock(self, master_password):
        display.vvv('Bitwarden unlock')
        bw_env = self.make_bw_env(BW_PASSWORD=master_password)
        bw_cmd = subprocess.run(
            [self.bw_cli, 'unlock', '--passwordenv', 'BW_PASSWORD', '--raw'],
            capture_output = True,
            env = bw_env,
        )
        if bw_cmd.returncode != 0:
            raise AnsibleLookupError("Bitwarden unlock failed: " + bw_cmd.stderr.decode('utf-8'))
        return bw_cmd.stdout.decode('utf-8')

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        # First of all populate options,
        # this will already take into account env vars and ini config
        self.set_options(var_options=variables, direct=kwargs)

        bw = BitwardenCLI(
            bitwardencli_appdata_dir = self.get_option('bitwardencli_appdata_dir'),
            bw_cli = self.get_option('bw_cli'),
            bw_session = self.get_option('bw_session'),
            client_id = self.get_option('client_id'),
            client_secret = self.get_option('client_secret'),
            master_password = self.get_option('master_password'),
        )

        ret = []
        for term in terms:
            ret.append(bw.get_item(term))
        return ret
