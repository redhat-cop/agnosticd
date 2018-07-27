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

if [ "$n_projects" -gt 0 ]; then
    # wait a little longer before retrying
    sleep ${2:-120}
    n_projects=$($OC get projects --no-headers|wc -l)
fi

# ensure it's 0
[ "${n_projects}" -lt 1 ]

# User should not be able to create projects at this point
set +e
p=test-failed-creation-${RANDOM}
$OC new-project ${p}
ret=$?
set -e

if [ "${ret}" = 0 ]; then
    $OC delete project ${p}
    echo "ERROR: user can still create projects" >&2
    exit 2
fi
