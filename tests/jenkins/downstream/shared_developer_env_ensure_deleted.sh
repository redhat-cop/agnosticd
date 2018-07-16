#!/bin/bash

set -xue -o pipefail

: "${credentials:?"credentials not defined"}"

[ -n "${1}" ]

username=$(echo "$credentials" | cut -d: -f1)
export username
password=$(echo "$credentials" | cut -d: -f2)
export password


config=${username}.${RANDOM}.config
OC="oc --config $config --insecure-skip-tls-verify=true"

$OC login "${1}" --username="${username}" --password="${password}"

n_projects=$($OC get projects --no-headers|wc -l)

[ "${n_projects}" -lt 1 ]
