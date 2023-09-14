READY=$((oc get nodes || echo NotReady) |grep -c " Ready ")
while [ $READY -ne 6 ]; do
        oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
        READY=$((oc get nodes || echo NotReady) |grep -c " Ready ")
        sleep 10
done
