# (c) 2022 Guillaume Core (fridim)

# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import packet

from time import sleep
from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

DOCUMENTATION = """
  name: equinix_api
  author: Guillaume Core (@fridim) <gucore@redhat.com>
  version_added: "2.11"
  short_description: Interact with Equinix Metal API
  description:
    - This lookup interacts with the Equinix Metal API.
  options:
    _terms:
      description: endpoint of API to call
      required: True
    api_token:
      description:
        - API Token to interact with the Equinix Metal API
      type: string
    params:
      description:
        - payload to pass with the call
      type: object
      default: {}
    verb:
      description:
        - HTTP verb (GET, POST, ...)
      type: string
      default: GET
      choices:
        - GET
        - POST

    retries:
      description:
        - number of time to retry if the call fails
      type: number
      default: 5

  notes:
    - Returns API call
"""

display = Display()

class LookupModule(LookupBase):
    """
    Lookup module to interact with the Equinix Metal API
    """

    def run(self, terms, variables=None, **kwargs):

        # First of all populate options,
        # this will already take into account env vars and ini config
        self.set_options(var_options=variables, direct=kwargs)

        token = self.get_option('api_token')
        if not token:
            if 'equinix_metal_api_token' in variables:
                token = variables['equinix_metal_api_token']
                display.v("equinix_api: use variable variable equinix_metal_api_token as the token")
            else:
                raise AnsibleLookupError("API token must be provided")

        verb = self.get_option('verb')
        if not verb:
            verb = 'GET'

        params = self.get_option('params')
        if not params:
            params = {}

        retries = self.get_option('retries')
        if not retries:
            retries = 5

        delay = 2
        # lookups in general are expected to both take a list as input and output a list
        # this is done so they work with the looping construct 'with_'.
        ret = []
        for term in terms:
            if term:
                while retries > 0:
                    try:
                        manager = packet.Manager(auth_token=token)
                        resp = manager.call_api(term, type=verb, params=params)
                        if 'capacity' in resp:
                            ret.append(resp['capacity'])
                        else:
                            raise AnsibleLookupError(
                                "equinix_api: Bad response from Equinix Metal API, 'capacity' expected in response."
                            )

                        break
                    except packet.Error as packet_error:
                        display.display(repr(packet_error))
                        retries = retries - 1
                        display.display("equinix_api lookup: %d retries left" %(retries))
                        if retries > 0:
                            delay = delay * 2
                            sleep(delay)

        return ret
