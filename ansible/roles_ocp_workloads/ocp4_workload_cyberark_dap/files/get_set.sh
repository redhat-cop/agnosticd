#!/bin/bash

# Authenticates as a user and gets or sets value of a specified variable.
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
# $1 - command (get or set)
# $2 - name of variable
# $3 - value to set
main() {
  case $1 in
    get)  local command=get
	local variable_name=$2
	;;
    set)  local command=set
	local variable_name=$2
	local variable_value="$3"
	;;
    *)  printf "\nUsage: %s [ get | set ] <variable-name> [ <variable-value> ]\n" $0
	exit -1
  esac

  authn_user   # authenticate user
  if [[ "$AUTHN_TOKEN" == "" ]]; then
    echo "Authentication failed..."
    exit -1
  fi

  variable_name=$(urlify "$variable_name")

  case $command in
    get)
	curl -sk -H "Content-Type: application/json" \
	-H "Authorization: Token token=\"$AUTHN_TOKEN\"" \
	$CONJUR_APPLIANCE_URL/secrets/$CONJUR_ACCOUNT/variable/$variable_name
	;;
    set)
	curl -sk -H "Content-Type: application/json" \
	-H "Authorization: Token token=\"$AUTHN_TOKEN\"" \
	--data "$variable_value" \
	$CONJUR_APPLIANCE_URL/secrets/$CONJUR_ACCOUNT/variable/$variable_name
	;;
  esac
}

##################
# AUTHN USER - sets AUTHN_TOKEN globally
# - no arguments
authn_user() {
  if [ -z ${AUTHN_USERNAME+x} ]; then
    >&2 echo
    >&2 echo -n Enter admin user name:
    read admin_uname
    >&2 echo -n Enter the admin password \(it will not be echoed\):
    read -s admin_pwd
    export AUTHN_USERNAME=$admin_uname
    export AUTHN_PASSWORD=$admin_pwd
  fi

  # Login user, authenticate and set authn token
  local api_key=$(curl -sk \
                    --user $AUTHN_USERNAME:$AUTHN_PASSWORD \
                    $CONJUR_APPLIANCE_URL/authn/$CONJUR_ACCOUNT/login)
  local response=$(curl -sk --data $api_key \
                     $CONJUR_APPLIANCE_URL/authn/$CONJUR_ACCOUNT/$AUTHN_USERNAME/authenticate)
  AUTHN_TOKEN=$(echo -n $response| base64 | tr -d '\r\n')
}

################
# URLIFY - url encodes input string
# in: $1 - string to encode
# out: encoded string on stdout
urlify() {
        local str=$1; shift
        str=$(echo $str | sed 's= =%20=g')
        str=$(echo $str | sed 's=/=%2F=g')
        str=$(echo $str | sed 's=:=%3A=g')
        str=$(echo $str | sed 's=+=%2B=g')
        str=$(echo $str | sed 's=&=%26=g')
        str=$(echo $str | sed 's=@=%40=g')
        echo $str
}

main "$@"
