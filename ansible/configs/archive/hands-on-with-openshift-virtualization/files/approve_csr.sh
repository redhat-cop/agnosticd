#!/bin/sh
export KUBECONFIG=/home/lab-user/install/auth/kubeconfig
NOTREADY=$((/usr/local/bin/oc get nodes || echo NotReady) |grep -c NotReady)
while [ $NOTREADY -gt 0 ]; do
        /usr/local/bin/oc get csr|grep Pending|awk '{print $1}'|xargs -i /usr/local/bin/oc adm certificate approve {}
        NOTREADY=$((/usr/local/bin/oc get nodes || echo NotReady) |grep -c NotReady)
        sleep 10
done
exit 0
