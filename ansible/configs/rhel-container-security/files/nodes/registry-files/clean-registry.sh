#!/bin/bash
#
# Clean the registry in a rootless container on RHEL8.1
#

ENGINE=podman
STORAGE_DIR=${HOME}/storage/registry
NAME=registry
IMAGE=docker.io/library/registry:2
TLS_CERT=myserver.cert 
TLS_KEY=myserver.key 

podman stop ${NAME}
podman rm ${NAME}
podman rmi ${IMAGE}:latest
rm -rf ${STORAGE_DIR}

#
# Update the CA trust store.
#
sudo rm /etc/pki/ca-trust/source/anchors/${TLS_CERT}
sudo update-ca-trust
