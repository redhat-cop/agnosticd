#!/bin/bash
#
# Run the registry in a rootless container on RHEL8.1
#
# Before running this script, generate SSL certificates (see gen-certs/gen-cert.sh).
#

ENGINE=podman
LOCAL_PORT=5000
STORAGE_DIR=${HOME}/storage/registry
DATA_DIR=${STORAGE_DIR}/data
AUTH_DIR=${STORAGE_DIR}/auth
CERTS_DIR=${STORAGE_DIR}/certs
NAME=registry
IMAGE=docker.io/library/registry:2
TLS_CERT=myserver.cert 
TLS_KEY=myserver.key 

mkdir -p ${STORAGE_DIR} ${DATA_DIR} ${AUTH_DIR} ${CERTS_DIR}

# 
# Copy the certs to the registry directory.
#
cp gen-certs/${TLS_CERT} ${CERTS_DIR}
cp gen-certs/${TLS_KEY} ${CERTS_DIR}

#
# Update the CA trust store.
#
sudo cp gen-certs/${TLS_CERT} /etc/pki/ca-trust/source/anchors
sudo update-ca-trust

#
# Load the registry container 
#
# ${ENGINE} load -i registry.tar.gz
#

#
# SSL with authentication
# 
# Create users/passwords:
#
htpasswd -bBc ${AUTH_DIR}/htpasswd redhat redhat
cp htpasswd ${AUTH_DIR}
#

#
# SELinux context for /storage
#
chcon -R system_u:object_r:container_var_run_t:s0 ${STORAGE_DIR}
#

#
# Optional: authfile for podman login
#
# echo -n '<user_name>:<password>' | base64 -w0
#

#
# If a registry is running, stop it.
#
r=$(podman container ls --filter=name=${NAME} --quiet)

if [ $r ]; then
    echo "Registry is running so I'll stop it!"
    echo "Stopping and removing: " ${NAME} "container."
    ${ENGINE} rm -f ${NAME}
fi

# Insecure version

# ${ENGINE} run --name ${NAME} -p ${LOCAL_PORT}:5000 -v ${DATA_DIR}:/var/lib/registry:z -d --restart=always registry

# Secure version

${ENGINE} run --name ${NAME} -p ${LOCAL_PORT}:5000 -v ${DATA_DIR}:/var/lib/registry:z -d \
--restart=always -v ${AUTH_DIR}:/auth:z -e "REGISTRY_AUTH=htpasswd" -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" \
-e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd -v ${CERTS_DIR}:/certs:z \
-e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/${TLS_CERT} \
-e REGISTRY_HTTP_TLS_KEY=/certs/${TLS_KEY} ${IMAGE}

echo 
echo
echo "Give the registry a minute or so to start then ..."
echo "curl  --user user:password -k https://localhost:${LOCAL_PORT}/v2/_catalog"
echo

#
# Helpful commands for debugging.
#
# echo "curl --cacert /storage/registry/certs/domain.crt --user redhat https://ip-172-31-40-75.ec2.internal:5000/v2/_catalog"
# echo "curl localhost:${LOCAL_PORT}/v2/_catalog"
# echo "Edit /etc/containers/registries.conf, restart docker then login"
# echo "podman login https://`hostname`:5000"
#login -u redhat -p redhat ip-172-31-38-186.ec2.internal:5000
#podman login -u redhat -p redhat --cert-dir=/home/ec2-user/storage/registry/certs ip-172-31-38-186.ec2.internal:5000
#podman push ip-172-31-38-186.ec2.internal:5000/registry
#podman push --cert-dir=/home/ec2-user/storage/registry/certs ip-172-31-38-186.ec2.internal:5000/registry
# echo "podman login -u user -p password https://<hostname>:5000"
