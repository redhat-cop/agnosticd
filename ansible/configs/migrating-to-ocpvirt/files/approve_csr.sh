#!/bin/sh -x
oc get csr 2>error.log
ERRORS=$(grep -v "No resources found" error.log|wc -l)
while [ $ERRORS -gt 0 ]; do
  sleep 10
  oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
  oc get csr 2>error.log
  ERRORS=$(grep -v "No resources found" error.log|wc -l)  
done

oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
sleep 30
READY=$((oc get nodes || echo NotReady) |grep -c " Ready ")
echo "Ready servers: $READY"
while [ $READY -ne 6 ]; do
        oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
        READY=$((oc get nodes || echo NotReady) |grep -c " Ready ")
        echo "Ready servers: $READY"
        sleep 5
done
sleep sleep 30
oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
READY=$((oc get nodes || echo NotReady) |grep -c " Ready ")
echo "Ready servers: $READY"
while [ $READY -ne 6 ]; do
        oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
        READY=$((oc get nodes || echo NotReady) |grep -c " Ready ")
        echo "Ready servers: $READY"
        sleep 5
done
