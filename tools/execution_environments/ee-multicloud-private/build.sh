#!/usr/bin/env bash
set -eu
name=ee-multicloud
tag=$1


echo "${name}:${tag} Private"

echo "Login to registry.redhat.io:"
podman login registry.redhat.io

# Private (subscriptions)
ansible-builder build -v 3 -c . \
    --tag ${name}:${tag}

echo "Pushing ${name}:${tag}"
echo -n "Push to registries? [press enter to continue]"
read

# Private
# image-registry.apps.open.redhat.com
# Push to both active and passive cluster
for REPO in \
    default-route-openshift-image-registry.apps.ocp-us-west-2.infra.open.redhat.com \
    default-route-openshift-image-registry.apps.ocp-us-east-1.infra.open.redhat.com
do
    echo
    echo "Please login to $REPO"
    podman login $REPO
    podman push ${name}:${tag} $REPO/agnosticd/${name}:${tag}
done
