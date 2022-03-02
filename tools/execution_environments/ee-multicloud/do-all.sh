#!/usr/bin/env bash
set -eu
name=ee-multi-cloud
tag=$1

if [ -z "${tag}" ]; then
    echo "tag is missing"
    exit 2
fi


echo "${name}:${tag} Private"

# Private (subscriptions)
ansible-builder build -v 3 -c . \
    --tag ${name}:${tag}

echo "Pushing ${name}:${tag}"
REPO=image-registry.apps-dev.open.redhat.com
#podman push ${name}-supported:${tag} $REPO/agnosticd/${name}:${tag}
