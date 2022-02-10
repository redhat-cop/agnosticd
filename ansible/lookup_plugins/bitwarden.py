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
  - This lookup returns items fetched from Bitwarden
  options:
    _terms:
      description: Item ids to fetch
      required: True
    bw_cli:
      description:
      - Path for bitwarden cli command.
      - If not provided then the environment PATH will be used to find `bw`.
      type: string
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
- name: Set api_access fact
  set_fact:
    api_access: >-
      {{
        query(
          'bitwarden', 'api-access-credentials',
           client_id=bitwarden_client_id,
           client_secret=bitwarden_client_secret,
           master_password=bitwarden_master_password
        ).login
      }}
"""

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
import json
import requests
import shutil
import subprocess
import tempfile

display = Display()

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        # First of all populate options,
        # this will already take into account env vars and ini config
        self.set_options(var_options=variables, direct=kwargs)

        bw_cli = self.get_option('bw_cli')
        client_id = self.get_option('client_id')
        client_secret = self.get_option('client_secret')
        master_password = self.get_option('master_password')

        if not bw_cli:
            bw_cli = shutil.which('bw')

        if not client_id:
            raise AnsibleError('Bitwarden client_id is required.')
        elif not client_id.startswith('user.'):
            raise AnsibleError('Bitwarden client_id is invalid. Only user client ids are supported.')

        if not client_secret:
            raise AnsibleError('Bitwarden client_secret is required.')

        if not master_password:
            raise AnsibleError('Bitwarden master_password is required.')

        with tempfile.TemporaryDirectory() as bitwardencli_appdata_dir:
            ret = []
            bw_login_result = subprocess.run(
                [bw_cli, 'login', '--apikey'],
                capture_output = True,
                env = dict(
                    BITWARDENCLI_APPDATA_DIR = bitwardencli_appdata_dir,
                    BW_CLIENTID = client_id,
                    BW_CLIENTSECRET = client_secret,
                ),
            )
            if bw_login_result.returncode != 0:
                raise AnsibleError("Bitwarden login failed: " + bw_login_result.stderr.decode('utf-8'))

            bw_unlock_result = subprocess.run(
                [bw_cli, 'unlock', '--passwordenv', 'BW_PASSWORD', '--raw'],
                capture_output = True,
                env = dict(
                    BITWARDENCLI_APPDATA_DIR = bitwardencli_appdata_dir,
                    BW_PASSWORD = master_password,
                ),
            )
            if bw_unlock_result.returncode != 0:
                raise AnsibleError("Bitwarden unlock failed: " + bw_unlock_result.stderr.decode('utf-8'))

            bw_session = bw_unlock_result.stdout.decode('utf-8')

            for term in terms:
                bw_get_item_result = subprocess.run(
                    [bw_cli, 'get', 'item', term],
                    capture_output = True,
                    env = dict(
                        BITWARDENCLI_APPDATA_DIR = bitwardencli_appdata_dir,
                        BW_SESSION = bw_session,
                    ),
                )
                if bw_get_item_result.returncode != 0:
                    raise AnsibleError("Failed to fetch item from Bitwarden: " + bw_get_item_result.stderr.decode('utf-8'))
                ret.append(json.loads(bw_get_item_result.stdout))

            return ret
