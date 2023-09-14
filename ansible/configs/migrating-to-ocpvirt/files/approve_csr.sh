NOTREADY=$((oc get nodes || echo NotReady) |grep -c NotReady)
while [ $NOTREADY -gt 0 ]; do
        oc get csr|grep Pending|awk '{print $1}'|xargs -i oc adm certificate approve {}
        NOTREADY=$((oc get nodes || echo NotReady) |grep -c NotReady)
        sleep 10
done
