#!/bin/sh

version=stable
arch=x86_64
tarball=openshift-client-linux.tar.gz
url="https://mirror.openshift.com/pub/openshift-v4/${arch}/clients/ocp/${version}/${tarball}"
cd /tmp
curl -s "${url}" -o ${tarball}
tar xzvf ${tarball}
install -t /usr/bin oc kubectl
