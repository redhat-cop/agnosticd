#!/usr/bin/env bash
set -eu
name=ee-multicloud
tag=$1

if [ -z "${tag}" ]; then
    echo "tag is missing"
    exit 2
fi


echo "${name}:${tag} Public"

# Public
ansible-builder build -v 3 -c . \
    --tag ${name}-public:${tag}

echo "Pushing ${name}:${tag}"
REPO=quay.io
echo -n "Push to registry $REPO ? [press enter to continue]"
read
podman login $REPO
podman push ${name}-public:${tag} $REPO/agnosticd/${name}:${tag}
