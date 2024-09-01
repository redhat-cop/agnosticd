#!/bin/bash

# Define the namespace and resource names
NAMESPACE="openshift-operators"
CSV_NAME="devworkspace-operator.v0.30.0"
DEPLOYMENT_NAME="devworkspace-webhook-server"

# Define the old and new image references
OLD_IMAGE="registry.redhat.io/openshift4/ose-kube-rbac-proxy@sha256:fde6314359436241171f6361f9a1e23c60bdf2d421c0c5740734d1dcf5f01ac2"
NEW_IMAGE="registry.redhat.io/openshift4/ose-kube-rbac-proxy@sha256:514e9e03f1d96046ff819798e54aa5672621c15805d61fb6137283f83f57a1e3"

# Function to update image in a YAML file
update_image() {
    local resource_type=$1
    local resource_name=$2
    local namespace=$3
    local old_image=$4
    local new_image=$5

    # Temporarily store the resource definition in a YAML file
    local temp_file=$(mktemp)

    # Get the current resource definition and store it in a temp file
    oc get $resource_type $resource_name -n $namespace -o yaml > $temp_file

    # Replace the old image with the new image
    sed -i "s|$old_image|$new_image|g" $temp_file

    # Apply the updated resource definition
    oc apply -f $temp_file -n $namespace

    # Clean up
    rm $temp_file

    echo "Image updated from $old_image to $new_image in $resource_type $resource_name."
}

# Update the image in the CSV
update_image "csv" "$CSV_NAME" "$NAMESPACE" "$OLD_IMAGE" "$NEW_IMAGE"

# Update the image in the Deployment
update_image "deployment" "$DEPLOYMENT_NAME" "$NAMESPACE" "$OLD_IMAGE" "$NEW_IMAGE"

