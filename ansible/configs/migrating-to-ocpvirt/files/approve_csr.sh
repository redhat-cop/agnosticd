#!/bin/sh -x
READY=$((oc get nodes || echo NotReady) |grep -c " Ready ")
echo "Ready servers: $READY"
while [ $READY -ne 6 ]; do
        oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
        READY=$((oc get nodes || echo NotReady) |grep -c " Ready ")
        echo "Ready servers: $READY"
        sleep 10
done
