#!/bin/bash

set -xue -o pipefail

: "${credentials:?"credentials not defined"}"

[ -n "${1}" ]
[ -n "${2}" ]

username=$(echo "$credentials" | cut -d: -f1)
export username
password=$(echo "$credentials" | cut -d: -f2)
export password


config=${username}.${RANDOM}.config
OC="oc --config $config --insecure-skip-tls-verify=true --request-timeout=0"

$OC login "${1}" --username="${username}" --password="${password}"

GUID="${2}"
project="test-${GUID}-${RANDOM}"

$OC new-project "${project}"

$OC new-app cakephp-mysql-persistent -n "${project}"

sleep 120

$OC rollout status dc/cakephp-mysql-persistent -w -n "${project}"
$OC rollout status dc/mysql -w -n "${project}"

route=$($OC get route -l template=cakephp-mysql-persistent  --no-headers -n "${project}"\
            |awk '{print $2}')

sleep 5
curl -k -s "http://${route}" \
    |grep 'Welcome to your CakePHP application on OpenShift'
