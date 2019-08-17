#!/bin/bash
#
# Prereqs: a running ocp 4 cluster, logged in as kubeadmin
#
MYDIR="$( cd "$(dirname "$0")" ; pwd -P )"
function usage() {
    echo "usage: $(basename $0)"
}

if [ ! "$(oc get clusterrolebindings)" ] ; then
  echo "not cluster-admin"
  exit 1
fi

oc delete project labs-infra
oc delete template coolstore-monolith-binary-build coolstore-monolith-pipeline-build ccn-sso72 -n openshift
oc delete CatalogSourceConfig/installed-redhat-che -n openshift-marketplace

# delete user projects
for proj in $(oc get projects -o name | grep 'user*' | cut -d/ -f2) ; do
  oc delete project $proj
done

# scale back down
for i in $(oc get machinesets -n openshift-machine-api -o name | grep worker| cut -d'/' -f 2) ; do
  echo "Scaling $i to 1 replica"
  oc patch -n openshift-machine-api machineset/$i -p '{"spec":{"replicas": 1}}' --type=merge
done
