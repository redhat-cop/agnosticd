#!/bin/sh -xe
cat << EOF | oc apply -f -
---
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-cnv
---
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: openshift-cnv
  namespace: openshift-cnv
spec:
  targetNamespaces:
  - openshift-cnv
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-cnv
  namespace: openshift-cnv
spec:
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  name: kubevirt-hyperconverged
  channel: stable
EOF

until oc get hyperconvergeds.hco.kubevirt.io; do sleep 60; done

sleep 60

export VERSION=$(curl https://storage.googleapis.com/kubevirt-prow/release/kubevirt/kubevirt/stable.txt)
wget -O /usr/bin/virtctl  https://github.com/kubevirt/kubevirt/releases/download/${VERSION}/virtctl-${VERSION}-linux-amd64
chmod 775 /usr/bin/virtctl

cat << EOF | oc apply -f -
---
apiVersion: hco.kubevirt.io/v1beta1
kind: HyperConverged
metadata:
  name: kubevirt-hyperconverged
  namespace: openshift-cnv
spec:
EOF

cat << EOF | oc apply -f -
---
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-mtv
EOF

cat << EOF | oc apply -f -
---
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: openshift-mtv
  namespace: openshift-mtv
spec:
  targetNamespaces:
  - openshift-mtv
EOF

cat << EOF | oc apply -f -
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-mtv
  namespace: openshift-mtv
spec:
  channel: release-v2.6
  installPlanApproval: Automatic
  name: mtv-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF

until oc get forkliftcontrollers.forklift.konveyor.io; do sleep 60; done
sleep 60


cat << EOF | oc apply -f -
---
apiVersion: forklift.konveyor.io/v1beta1
kind: ForkliftController
metadata:
  name: forklift-controller
  namespace: openshift-mtv
spec:
  controller_max_vm_inflight: 1
EOF

cat << EOF | oc apply -f -
---
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-nmstate
EOF

cat << EOF | oc apply -f -
---
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: openshift-nmstate
  namespace: openshift-nmstate
spec:
  targetNamespaces:
  - openshift-nmstate
EOF

cat << EOF| oc apply -f -
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-nmstate
  namespace: openshift-nmstate
spec:
  channel: stable
  installPlanApproval: Automatic
  name: kubernetes-nmstate-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF

until oc get nmstates.nmstate.io; do sleep 60; done
sleep 60


cat << EOF | oc apply -f -
---
apiVersion: nmstate.io/v1
kind: NMState
metadata:
  name: nmstate
EOF

cat << EOF | oc apply -f -
---
apiVersion: v1
kind: Namespace
metadata:
  name: metallb-system
EOF

cat << EOF | oc apply -f -
---
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: metallb-system
  namespace: metallb-system
EOF

cat << EOF | oc apply -f -
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: metallb-system
  namespace: metallb-system
spec:
  channel: stable
  name: metallb-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF

until oc get metallbs.metallb.io; do sleep 60; done
sleep 60


cat << EOF | oc apply -f -
---
apiVersion: metallb.io/v1beta1
kind: MetalLB
metadata:
  name: metallb
  namespace: metallb-system
EOF

cat << EOF | oc apply -f -
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: web-terminal
  namespace: openshift-operators
spec:
  channel: fast
  installPlanApproval: Automatic
  name: web-terminal
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  startingCSV: web-terminal.v1.10.0
EOF

cat <<EOF | oc apply -f -
---
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-terminal
EOF

sleep 30

# https://access.redhat.com/solutions/7084768
# $ oc edit csv devworkspace-operator.v0.30.0 -n openshift-operators
and replace all references of
# registry.redhat.io/openshift4/ose-kube-rbac-proxy@sha256:fde6314359436241171f6361f9a1e23c60bdf2d421c0c5740734d1dcf5f01ac2
# to
# registry.redhat.io/openshift4/ose-kube-rbac-proxy@sha256:514e9e03f1d96046ff819798e54aa5672621c15805d61fb6137283f83f57a1e3
#
# and
#
#
# a oc edit deployment devworkspace-webhook-server -n openshift-operators
# Eventually, the devworkspace-controller-manager and devworkspace-webhook-server pods will use the updated image:
# $ oc get pods -n openshift-operators
# NAME                                             READY   STATUS   RESTARTS   AGE
# devworkspace-controller-manager-54f7dd576b-2xx8k  2/2    Running   0         117s
# devworkspace-webhook-server-579f68466f-c7vv2      2/2    Running   0         115s
# devworkspace-webhook-server-579f68466f-fb8th      2/2    Running   0         95s



until oc get DevWorkspace -n openshift-terminal; do sleep 30; done

cat << EOF | oc apply -f -
---
apiVersion: workspace.devfile.io/v1alpha2
kind: DevWorkspace
metadata:
  annotations:
    controller.devfile.io/devworkspace-source: web-terminal
    controller.devfile.io/restricted-access: 'true'
  name: webterminal
  namespace: openshift-terminal
  finalizers:
  - rbac.controller.devfile.io
  labels:
    console.openshift.io/terminal: 'true'
spec:
  routingClass: web-terminal
  started: true
  template:
    components:
    - name: web-terminal-tooling
      plugin:
        kubernetes:
          name: web-terminal-tooling
          namespace: openshift-operators
    - name: web-terminal-exec
      plugin:
        kubernetes:
          name: web-terminal-exec
          namespace: openshift-operators
EOF
