#!/bin/bash

set -ue -o pipefail

: "${credentials:?"credentials not defined"}"

[ -n "${1}" ]
[ -n "${2}" ]

username=$(echo "$credentials" | cut -d: -f1)
export username
password=$(echo "$credentials" | cut -d: -f2)
export password
guid="${2}"
export guid


config=${username}.${RANDOM}.config
OC="oc --config $config --insecure-skip-tls-verify=true"

$OC login "${1}" --username="${username}" --password="${password}"

set +e
n_projects=$($OC get projects --no-headers|grep "${guid}"|wc -l)

if [ "$n_projects" -gt 0 ]; then
    # wait a little longer before retrying
    sleep 120
    n_projects=$($OC get projects --no-headers|grep "${guid}"|wc -l)
fi
set -e
# ensure it's 0
[ "${n_projects}" -lt 1 ]
