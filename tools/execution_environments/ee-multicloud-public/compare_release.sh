#!/usr/bin/env bash

set -ex

v1=$1
v2=$2

if [ -z "${v1}" ] || [ -z "${v2}" ]; then
	echo "$0 [v1] [v2]"
	echo "ex:  $0 v0.0.9 v0.0.10"
	exit 1
fi

v1out=$(mktemp)
v2out=$(mktemp)
podman run  -v ./:/tmp/a --entrypoint=/tmp/a/ee-report.sh quay.io/agnosticd/ee-multicloud:$v1 > $v1out
podman run  -v ./:/tmp/a --entrypoint=/tmp/a/ee-report.sh quay.io/agnosticd/ee-multicloud:$v2 > $v2out

podman images quay.io/agnosticd/ee-multicloud:$v1 --format "* ${v1} size: {{ .Size }}"
podman images quay.io/agnosticd/ee-multicloud:$v2 --format "* ${v2} size: {{ .Size }}"

diff -u $v1out $v2out \
    | gh gist create --public - \
    -d "ee-report diff of $v1 and $v2" -f "ee-report-$v1-$v2.diff"

rm $v1out $v2out

podman run  -v ./:/tmp/a --entrypoint=/tmp/a/ee-report.sh quay.io/agnosticd/ee-multicloud:$v2 \
    | gh gist create --public - \
    -d "ee-report ee-multicloud:$v2" -f "ee-report-$v2.txt"
