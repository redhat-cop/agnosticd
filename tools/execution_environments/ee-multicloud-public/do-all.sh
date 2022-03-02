#!/usr/bin/env bash
set -eu
name=ee-multicloud
tag=$1

if [ -z "${tag}" ]; then
    echo "tag is missing"
    exit 2
fi


echo "${name}:${tag} Public"

# Private (subscriptions)
ansible-builder build -v 3 -c . \
    --tag ${name}-public:${tag}

echo "Pushing ${name}:${tag}"
REPO=quay.io
podman push ${name}-public:${tag} $REPO/agnosticd/${name}:${tag}
