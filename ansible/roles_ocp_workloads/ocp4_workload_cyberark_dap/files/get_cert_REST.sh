#!/bin/bash

if [[ "$(which openssl)" == "" ]]; then
  echo "OpenSSL not installed."
  exit -1
fi
if [[ $# != 2 ]]; then
  echo "Usage: $0 <hostname> <port>"
  exit -1
fi
CONJUR_HOST=$1
CONJUR_PORT=$2

openssl s_client -showcerts -servername $CONJUR_HOST \
    -connect $CONJUR_HOST:$CONJUR_PORT < /dev/null 2> /dev/null \
    | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p'
