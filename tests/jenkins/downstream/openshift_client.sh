#!/bin/bash

set -xue -o pipefail

: "${credentials:?"credentials not defined"}"

username=$(echo "$credentials" | cut -d: -f1)
export username
password=$(echo "$credentials" | cut -d: -f2)
export password


config=${username}.${RANDOM}.config
OC="oc --config $config --insecure-skip-tls-verify=true"

$OC login "${1}" --username="${username}" --password="${password}"

$OC get projects
