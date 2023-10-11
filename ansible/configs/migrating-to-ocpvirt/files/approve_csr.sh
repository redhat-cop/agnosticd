#!/bin/sh -x
oc get csr 2>error.log
ERRORS=$(wc -l < error.log)
while [ $ERRORS -gt 0 ]; do
  oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
  oc get csr 2>error.log
  ERRORS=$(wc -l < error.log)
done

oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
sleep 120
READY=$((oc get nodes || echo NotReady) |grep -c " Ready ")
echo "Ready servers: $READY"
while [ $READY -ne 6 ]; do
        oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
        READY=$((oc get nodes || echo NotReady) |grep -c " Ready ")
        echo "Ready servers: $READY"
        sleep 10
done
sleep 120
oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
READY=$((oc get nodes || echo NotReady) |grep -c " Ready ")
echo "Ready servers: $READY"
while [ $READY -ne 6 ]; do
        oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
        READY=$((oc get nodes || echo NotReady) |grep -c " Ready ")
        echo "Ready servers: $READY"
        sleep 10
done
