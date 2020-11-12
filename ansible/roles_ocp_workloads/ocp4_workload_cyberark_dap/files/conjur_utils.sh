#!/bin/bash
util_defaults="set -u"

CONJUR_VERBOSE=${CONJUR_VERBOSE:-""}		# sets CONJUR_VERBOSE to "" if undefined

# this will return the authorization header used for api calls for other methods
function conjur_authenticate {
	$util_defaults
	api_key=$(curl $CONJUR_VERBOSE --fail -s -k 			\
		--user "$CONJUR_AUTHN_LOGIN:$CONJUR_AUTHN_API_KEY"	\
		$CONJUR_APPLIANCE_URL/authn/$CONJUR_ACCOUNT/login)
	urlLogin=$(echo "$CONJUR_AUTHN_LOGIN" | sed 's/\//%2F/g')
	session_token=$(curl $CONJUR_VERBOSE --fail -s -k 		\
		--data "$api_key" 					\
		$CONJUR_APPLIANCE_URL/authn/$CONJUR_ACCOUNT/$urlLogin/authenticate)
	token=$(echo -n $session_token | base64 | tr -d '\r\n')
	header="Authorization: Token token=\"$token\""
	echo "$header"
}

function conjur_info {
	$util_defaults
	curl $CONJUR_VERBOSE --fail -s -k "${CONJUR_APPLIANCE_URL}/info"
}

function conjur_health {
	$util_defaults
	curl $CONJUR_VERBOSE --fail -s -k "${CONJUR_APPLIANCE_URL}/health"
}

function conjur_enable_authn {
	$util_defaults
	serviceID=$1
	header=$(conjur_authenticate)
	response=$(curl -H "$header" -X PATCH -d "enabled=true" -s -k "${CONJUR_APPLIANCE_URL}/${serviceID}/${CONJUR_ACCOUNT}")
	echo "$response"
	conjur_info
}

function conjur_audit {
	$util_defaults
	header=$(conjur_authenticate)
	response=$(curl -H "$header" -s -k "${CONJUR_APPLIANCE_URL}/audit")
	echo "$response"
}

function conjur_append_policy {
	$util_defaults
	policy_branch=$1
	policy_name=$2
	header=$(conjur_authenticate)
	response=$(curl -H "$header" -X POST -d "$(< $policy_name)" -s -k $CONJUR_APPLIANCE_URL/policies/$CONJUR_ACCOUNT/policy/$policy_branch)
	echo "$response"
}

function conjur_update_policy {
	$util_defaults
	policy_branch=$1
	policy_name=$2
	header=$(conjur_authenticate)
	response=$(curl -H "$header" -X PATCH -d "$(< $policy_name)" -s -k $CONJUR_APPLIANCE_URL/policies/$CONJUR_ACCOUNT/policy/$policy_branch)
	echo "$response"
}

function conjur_set_variable {
	$util_defaults
	variable_name=$1
	variable_value=$2
	header=$(conjur_authenticate)
	curl -k -s -H "$header" --data "$variable_value" "$CONJUR_APPLIANCE_URL/secrets/$CONJUR_ACCOUNT/variable/$variable_name"
}

function conjur_get_variable {
	$util_defaults
	variable_name=$1
	header=$(conjur_authenticate)
	value=$(curl -k -s -H "$header" "$CONJUR_APPLIANCE_URL/secrets/$CONJUR_ACCOUNT/variable/$variable_name")
	echo "${value}"
}

function conjur_resources {
  	$util_defaults
	header=$(conjur_authenticate)
	curl -k -s -H "$header" "$CONJUR_APPLIANCE_URL/resources/$CONJUR_ACCOUNT" | jq
}

function conjur_list {
	$util_defaults
	resources=$(conjur_resources)
	echo "${resources}" | jq -r .[].id
}

function conjur_rotate_api_key {
	local kind=$1; shift
	local id=$1; shift
	$util_defaults
	header=$(conjur_authenticate)
	api_key=$(curl $CONJUR_VERBOSE -X PUT -sk 	\
		-H "$header"				\
		"$CONJUR_APPLIANCE_URL/authn/${CONJUR_ACCOUNT}/api_key?role=$CONJUR_ACCOUNT:${kind}:${id}")
	echo $api_key
}

function conjur_set_user_password() {
	local username=$1; shift
	local current_password="$1"; shift	# can be API key
	local new_password="$1"; shift
	$util_defaults
	curl $CONJUR_VERBOSE --fail -s -k 				\
		--user "$username:$current_password"			\
		$CONJUR_APPLIANCE_URL/authn/$CONJUR_ACCOUNT/login
	curl $CONJUR_VERBOSE -X PUT -s -k				\
		--data "$new_password"					\
		--user $username:"$current_password"			\
		"$CONJUR_APPLIANCE_URL/authn/${CONJUR_ACCOUNT}/password"
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
