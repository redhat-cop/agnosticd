#!/bin/sh

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

aws_version=1.22.66
curl "https://s3.amazonaws.com/aws-cli/awscli-bundle-${aws_version}.zip" -o "awscli-bundle.zip"
unzip awscli-bundle.zip
python3.6 ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws
