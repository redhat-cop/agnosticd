#!/bin/bash

# Authenticates as admin user and loads policy file.
# If you set the environment variables AUTHN_USERNAME and AUTHN_PASSWORD
# to appropriate values, you can avoid having to enter the admin username
# and password every time this script runs. UNSET THEM WHEN FINISHED.

if [ -z "${CONJUR_APPLIANCE_URL}" ]; then
  echo "You must set values for env vars CONJUR_APPLIANCE_URL and CONJUR_ACCOUNT."
  exit -1
fi

if [ -z "${AUTHN_USERNAME}" ]; then
  echo "You must set values for env vars AUTHN_USERNAME and AUTHN_PASSWORD."
  exit -1
fi

################  MAIN   ################
# $1 - name of policy file to load
main() {

  if [[ $# < 2 ]] ; then
    printf "\nUsage: %s <policy-branch-id> <policy-filename> [ delete | replace ]\n" $0
    printf "\nExamples:\n"
    printf "\t$> %s root /tmp/policy.yml\n" $0
    printf "\t$> %s dev/my-app /tmp/policy.yml\n" $0
    printf "\nDefault is append mode, unless 'delete' or 'replace' is specified\n"
    exit -1
  fi
  local policy_branch=$1
  local policy_file=$2

  local LOAD_MODE="POST"
  if [[ $# == 3 ]]; then
    case $3 in
      delete)   LOAD_MODE="PATCH"
		;;
      replace)  LOAD_MODE="PUT"
		;;
      *)	printf "\nSpecify 'delete' or 'replace' as load mode options.\n\n"
		exit -1
    esac
  fi

  authn_user   # authenticate user
  if [[ "$AUTHN_TOKEN" == "" ]]; then
    echo "Authentication failed..."
    exit -1
  fi

  curl -sk \
     -H "Content-Type: application/json" \
     -H "Authorization: Token token=\"$AUTHN_TOKEN\"" \
     -X $LOAD_MODE -d "$(< $policy_file)" \
     $CONJUR_APPLIANCE_URL/policies/$CONJUR_ACCOUNT/policy/$policy_branch
  echo
}

##################
# AUTHN USER - sets AUTHN_TOKEN globally
# - no arguments
authn_user() {
  if [ -z ${AUTHN_USERNAME+x} ]; then
    echo
    echo -n Enter admin user name:
    read admin_uname
    echo -n Enter the admin password \(it will not be echoed\):
    read -s admin_pwd
    echo
    export AUTHN_USERNAME=$admin_uname
    export AUTHN_PASSWORD=$admin_pwd
  fi
  # Login user, authenticate and get API key for session
  local api_key=$(curl \
                    -sk \
                    --user $AUTHN_USERNAME:$AUTHN_PASSWORD \
                    $CONJUR_APPLIANCE_URL/authn/$CONJUR_ACCOUNT/login)

  local response=$(curl -sk \
                     --data $api_key \
                     $CONJUR_APPLIANCE_URL/authn/$CONJUR_ACCOUNT/$AUTHN_USERNAME/authenticate)
  AUTHN_TOKEN=$(echo -n $response| base64 | tr -d '\r\n')
}

main "$@"
