#!/bin/sh -xe
cat << EOF | oc apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: metallb-system
EOF

cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: metallb-operator
  namespace: metallb-system
EOF

cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: metallb-operator-sub
  namespace: metallb-system
spec:
  channel: stable
  name: metallb-operator
  source: redhat-operators 
  sourceNamespace: openshift-marketplace
EOF

until oc get metallbs.metallb.io; do sleep 60; done
cat << EOF | oc apply -f -
apiVersion: metallb.io/v1beta1
kind: MetalLB
metadata:
  name: metallb
  namespace: metallb-system
EOF
sleep 60

cat << EOF | oc apply -f -
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: ip-addresspool
  namespace: metallb-system
spec:
  addresses:
    - 192.168.123.240-192.168.123.250
  autoAssign: true
  avoidBuggyIPs: false
EOF
sleep 60

cat << EOF | oc apply -f -
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: l2-adv
  namespace: metallb-system
spec:
  ipAddressPools:
    - ip-addresspool
  interfaces:
    - br-ex
EOF

cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  labels:
    operators.coreos.com/lvms-operator.openshift-storage: ''
  name: lvms-operator
  namespace: openshift-storage
spec:
  channel: stable-4.14
  installPlanApproval: Automatic
  name: lvms-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  startingCSV: lvms-operator.v4.14.1
EOF

until oc get lvmclusters.lvm.topolvm.io; do sleep 60; done
cat << EOF | oc apply -f -
apiVersion: lvm.topolvm.io/v1alpha1
kind: LVMCluster
metadata:
 name: my-lvmcluster
 namespace: openshift-storage
spec:
 storage:
   deviceClasses:
   - name: vg1
     deviceSelector:
       paths:
       - /dev/vdd
     thinPoolConfig:
       name: thin-pool-1
       sizePercent: 90
       overprovisionRatio: 10
EOF
