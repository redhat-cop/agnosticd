#!/bin/bash

worker_nodes=$(oc get nodes --selector='node-role.kubernetes.io/worker' -o jsonpath='{.items[*].metadata.labels.kubernetes\.io/hostname}')


for item in $worker_nodes; do
   cat <<EOF | oc apply --validate=false -f -
---
kind: Namespace
apiVersion: v1
metadata:
  name: rook-cleanup
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: rook-cleanup
  namespace: rook-cleanup
EOF
   oc adm policy add-scc-to-user privileged -z rook-cleanup
   cat <<EOF | oc apply -f -
---
kind: Pod
apiVersion: v1
metadata:
  name: rook-cleanup-pod
  namespace: rook-cleanup
spec:
  serviceAccountName: rook-cleanup
  volumes:
    - name: rook-cleanup-pv-storage
      hostPath:
        path: "/var/lib/rook"
        type: Directory
  containers:
    - name: rook-cleanup-pv-container
      image: registry.access.redhat.com/rhel7
      command: ["/bin/sh", "-c"]
      args: ["rm -rf /tmp/*; sleep 600"]
      volumeMounts:
        - mountPath: "/tmp"
          name: rook-cleanup-pv-storage
      securityContext:
        privileged: true
  nodeSelector:
    kubernetes.io/hostname: ${item}
EOF
   sleep 75
   oc delete pod rook-cleanup-pod -n rook-cleanup
done
oc delete project rook-cleanup