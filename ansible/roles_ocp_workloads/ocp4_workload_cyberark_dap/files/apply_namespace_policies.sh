#!/bin/bash
exec 1>>cyberark_setup/apply-policy.log 2>&1

cd cyberark_setup

export CYBERARK_NAMESPACE_NAME=$1
export DAP_ADMIN_PASSWORD=$2
export CONJUR_AUTHN_LOGIN=admin
export CONJUR_AUTHN_API_KEY=$DAP_ADMIN_PASSWORD

source ./dap_service_rhpds.config
source ./conjur_utils.sh

uname=$(echo user${3})

cat ./templates/user-namespace-policy.template				\
| sed -e "s#{{ APP_NAMESPACE_NAME }}#$uname#g"				\
| sed -e "s#{{ CYBERARK_NAMESPACE_NAME }}#$CYBERARK_NAMESPACE_NAME#g"	\
> ./$uname-policy.yaml

conjur_append_policy root ./$uname-policy.yaml
api_key=$(conjur_rotate_api_key user $uname)
conjur_set_user_password $uname $api_key ${uname}CYBR2@2@
