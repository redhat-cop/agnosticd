#!/usr/bin/env bash

# example ❯ ./compare.sh quay.io/agnosticd/ee-multicloud:v0.0.10 ee-multicloud:v0.0.11

v1=$1
v2=$2

if [ -z "${v1}" ] || [ -z "${v2}" ]; then
	echo "$0 [v1] [v2]"
	echo "ex:  $0 quay.io/agnosticd/ee-multicloud:v0.0.9 quay.io/agnosticd/ee-multicloud:latest"
	exit 1
fi

diff -u \
    <(podman run  -v ./:/tmp/a \
    --entrypoint=/tmp/a/ee-report.sh $v1) \
    <(podman run  -v ./:/tmp/a \
    --entrypoint=/tmp/a/ee-report.sh $v2) \
    | gh gist create --public -f "ee-report.diff" -d "ee-report ee-multicloud ${v1} to ${v2}"
