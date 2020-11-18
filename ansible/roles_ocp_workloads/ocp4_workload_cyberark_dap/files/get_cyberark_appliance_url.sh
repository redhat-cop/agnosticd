#!/bin/bash

export CYBERARK_NAMESPACE_NAME=$1

source cyberark_setup/dap_service_rhpds.config

echo $CONJUR_APPLIANCE_URL