#!/bin/sh
set -ue

cd /tmp


# initArch discovers the architecture for this system.
ARCH=$(uname -m)
case $ARCH in
    armv5*) ARCH="armv5";;
    armv6*) ARCH="armv6";;
    armv7*) ARCH="arm";;
    aarch64) ARCH="arm64";;
    x86) ARCH="386";;
    x86_64) ARCH="amd64";;
    i686) ARCH="386";;
    i386) ARCH="386";;
esac

echo "Detected architecture: ${ARCH}"

# OC
# Install rhel8 version of oc
# https://access.redhat.com/solutions/7077895
version=stable
tarball=openshift-client-linux-${ARCH}-rhel8.tar.gz
url="https://mirror.openshift.com/pub/openshift-v4/${ARCH}/clients/ocp/${version}/${tarball}"
curl -s -L "${url}" -o ${tarball}
tar xzf ${tarball}
install -t /usr/bin oc kubectl
rm ${tarball}

# Bitwarden
# DISCLAIMER: BW doesn't support ARM64 yet, so this is just a placeholder
url="https://vault.bitwarden.com/download/?app=cli&platform=linux"
curl -s -L "${url}" -o bw.zip
unzip bw.zip
install -t /usr/bin bw
rm bw bw.zip


# AWS CLI
aws_version=2.4.23
curl -s -L "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m)-${aws_version}.zip" \
    -o "awscliv2.zip"
unzip -q awscliv2.zip
./aws/install

rm awscliv2.zip
rm -rf aws

# helm

curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

# IBM Cloud binary
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh

# Install all plugins, best effort
ibmcloud plugin install --all || true
