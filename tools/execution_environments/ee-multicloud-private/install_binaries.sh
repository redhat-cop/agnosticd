#!/bin/sh
set -ue

cd /tmp

# OC

version=stable
arch=x86_64
tarball=openshift-client-linux.tar.gz
url="https://mirror.openshift.com/pub/openshift-v4/${arch}/clients/ocp/${version}/${tarball}"
curl -s -L "${url}" -o ${tarball}
tar xzf ${tarball}
install -t /usr/bin oc kubectl

# Bitwarden

url="https://vault.bitwarden.com/download/?app=cli&platform=linux"
curl -s -L "${url}" -o bw.zip
unzip bw.zip
install -t /usr/bin bw


# AWS CLI

aws_version=2.4.23
curl -s -L "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${aws_version}.zip" \
    -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
