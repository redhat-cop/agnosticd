#!/bin/sh
export KUBECONFIG=/home/lab-user/install/auth/kubeconfig
for node in master-{0,1,2} worker-{0,1,2} ; do
	/usr/local/bin/oc adm taint nodes ${node} network.openshift.io/mtu-too-small=value:NoSchedule- || true
done
exit 0
