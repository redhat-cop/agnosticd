#!/bin/sh 
EXPECTED_NODES=$1
export KUBECONFIG=/home/lab-user/install/auth/kubeconfig
NOTREADY=$(oc get nodes |grep -c NotReady)

while [ $NOTREADY -gt 0 ]; do
        oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
        sleep 30
        NOTREADY=$(oc get nodes |grep -c NotReady)
done
