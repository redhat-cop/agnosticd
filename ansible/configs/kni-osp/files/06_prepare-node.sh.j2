#!/bin/bash
# Generate oc & openshift-baremetal-install binary
# Build registry & rhcos caching httpd

export VERSION=4.3.12
export RELEASE_IMAGE=$(curl -s https://mirror.openshift.com/pub/openshift-v4/clients/ocp/$VERSION/release.txt| grep 'Pull From: quay.io' | awk -F ' ' '{print $3}' | xargs)

export PATH=$PATH:/home/cloud-user
export CMD=openshift-baremetal-install
export EXTRACT_DIR=$(pwd)
export PULLSECRET=/home/cloud-user/pull-secret.json

curl -s https://mirror.openshift.com/pub/openshift-v4/clients/ocp/$VERSION/openshift-client-linux-$VERSION.tar.gz | tar zxvf - oc
sudo cp oc /usr/local/bin/
oc adm release extract --registry-config "${PULLSECRET}" --command=$CMD --to "${EXTRACT_DIR}" ${RELEASE_IMAGE}

sudo yum -y install podman httpd httpd-tools
sudo mkdir -p /opt/registry/{auth,certs,data}
sudo openssl req -newkey rsa:4096 -nodes -sha256 -keyout /opt/registry/certs/domain.key -x509 -days 365 -out /opt/registry/certs/domain.crt -subj "/C=US/ST=NorthCarolina/L=Raleigh/O=Red Hat/OU=Marketing/CN=provision.schmaustech.com"
sudo cp /opt/registry/certs/domain.crt /home/cloud-user/domain.crt
sudo chown cloud-user:cloud-user /home/cloud-user/domain.crt
sudo cp /opt/registry/certs/domain.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust extract

sudo htpasswd -bBc /opt/registry/auth/htpasswd dummy dummy

sudo podman create --name poc-registry --net host -p 5000:5000 -v /opt/registry/data:/var/lib/registry:z -v /opt/registry/auth:/auth:z -e "REGISTRY_AUTH=htpasswd" -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry" -e "REGISTRY_HTTP_SECRET=ALongRandomSecretForRegistry" -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd -v /opt/registry/certs:/certs:z -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key docker.io/library/registry:2

sudo podman start poc-registry
sudo podman ps
sleep 10


export IRONIC_DATA_DIR=/opt/ocp/ironic
export IRONIC_IMAGES_DIR="${IRONIC_DATA_DIR}/html/images"
export IRONIC_IMAGE=quay.io/metal3-io/ironic:master
sudo mkdir -p $IRONIC_IMAGES_DIR
sudo chown -R "${USER}:${USER}" "$IRONIC_DATA_DIR"
sudo find $IRONIC_DATA_DIR -type d -print0 | xargs -0 chmod 755
sudo chmod -R +r $IRONIC_DATA_DIR
sudo podman pod create -n ironic-pod
sudo podman run -d --net host --privileged --name httpd --pod ironic-pod -v $IRONIC_DATA_DIR:/shared --entrypoint /bin/runhttpd ${IRONIC_IMAGE}

sudo podman ps
sleep 10

export UPSTREAM_REPO="registry.svc.ci.openshift.org/ocp/release:$VERSION"
export PULLSECRET=/home/cloud-user/pull-secret.json
export LOCAL_REG='provision.schmaustech.com:5000'
export LOCAL_REPO='ocp4/openshift4'
oc adm release mirror -a $PULLSECRET --from=$UPSTREAM_REPO --to-release-image=$LOCAL_REG/$LOCAL_REPO:$VERSION --to=$LOCAL_REG/$LOCAL_REPO

sed -i -e 's/^/  /' $HOME/domain.crt
echo "additionalTrustBundle: |" >> $HOME/install-config.yaml
cat $HOME/domain.crt >> $HOME/install-config.yaml

ssh-keygen -t rsa -q -f "$HOME/.ssh/id_rsa" -N ""
SSHKEY=$HOME/.ssh/id_rsa.pub
sed -i "s/SSH_KEY/$(sed 's:/:\\/:g' $SSHKEY)/" $HOME/install-config.yaml
