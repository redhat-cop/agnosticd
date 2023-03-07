#!/usr/bin/env bash

set -ex
# example ❯ ./compare.sh quay.io/agnosticd/ee-multicloud:v0.0.10 ee-multicloud:v0.0.11

v1=$1
v2=$2

if [ -z "${v1}" ] || [ -z "${v2}" ]; then
	echo "$0 [v1] [v2]"
	echo "ex:  $0 quay.io/agnosticd/ee-multicloud:v0.0.9 quay.io/agnosticd/ee-multicloud:latest"
	exit 1
fi

v1out=$(mktemp)
v2out=$(mktemp)
podman run  -v ./:/tmp/a --entrypoint=/tmp/a/ee-report.sh $v1 > $v1out
podman run  -v ./:/tmp/a --entrypoint=/tmp/a/ee-report.sh $v2 > $v2out

podman images $v1 --format "* ${v1} size: {{ .Size }}"
podman images $v2 --format "* ${v2} size: {{ .Size }}"
echo
echo "diff between ${v1} and ${v2}:"
echo
echo '```diff'
diff -u $v1out $v2out
echo '```'
