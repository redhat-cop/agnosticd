#!/bin/bash
cat <<EOF | oc apply -f -
apiVersion: ceph.rook.io/v1
kind: CephBlockPool
metadata:
  name: rbd
  namespace: rook-ceph
spec:
  failureDomain: host
  replicated:
    size: 3
EOF

# Retrieve the base64 encoded key and ID for the admin user on the cluster and store them in env variables to use for storageclass config
admin_key=$(pod=$(kubectl get pod -n rook-ceph -l app=rook-ceph-operator -o jsonpath="{.items[0].metadata.name}"); kubectl exec -ti -n rook-ceph ${pod} -- bash -c "ceph auth get-key client.admin -c /var/lib/rook/rook-ceph/rook-ceph.config | base64")
admin_id=$(pod=$(kubectl get pod -n rook-ceph -l app=rook-ceph-operator -o jsonpath="{.items[0].metadata.name}"); kubectl exec -ti -n rook-ceph ${pod} -- bash -c "echo -n admin|base64")

# Use the keys from above to create a secrets object on our Kubernetes cluster
cat <<EOF | oc create -f -
apiVersion: v1
kind: Secret
metadata:
  name: csi-rbd-secret
  namespace: default
data:
  userID: ${admin_id}
  userKey: ${admin_key}
EOF

#Create our csi-rbd storage class
cat <<EOF | oc create -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
   name: csi-rbd
provisioner: rbd.csi.ceph.com
parameters:
    # Specify a string that identifies your cluster. Ceph CSI supports any
    # unique string. When Ceph CSI is deployed by Rook use the Rook namespace,
    # this value can be found doing this 'oc edit cm rook-ceph-mon-endpoints -n rook-ceph',
    # for example "rook-ceph".
    clusterID: rook-ceph
    
    # Ceph pool into which the RBD image shall be created
    pool: rbd
    
    # RBD image format. Defaults to "2".
    imageFormat: "2"
    
    # RBD image features. Available for imageFormat: "2". CSI RBD currently supports only layering feature.
    imageFeatures: layering
    
    # The secrets have to contain Ceph admin credentials.
    csi.storage.k8s.io/provisioner-secret-name: csi-rbd-secret
    csi.storage.k8s.io/provisioner-secret-namespace: default
    csi.storage.k8s.io/node-stage-secret-name: csi-rbd-secret
    csi.storage.k8s.io/node-stage-secret-namespace: default
    # Ceph users for operating RBD
    adminid: admin
    
    # uncomment the following to use rbd-nbd as mounter on supported nodes
    # mounter: rbd-nbd
reclaimPolicy: Delete
EOF
