#!/usr/bin/env bash
set -eu
name=ee-multicloud
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
echo -n "Push to registry? [press enter to continue]"
read
podman push ${name}:${tag} $REPO/agnosticd/${name}:${tag}
