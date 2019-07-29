#!/bin/bash
# Retrieve the base64 encoded passwords for the admin users on the cluster and store them in env variables to use for storageclass config
admin_key=$(pod=$(kubectl get pod -n rook-ceph -l app=rook-ceph-operator  -o jsonpath="{.items[0].metadata.name}"); kubectl exec -ti -n rook-ceph ${pod} -- bash -c "ceph auth get-key client.admin -c /var/lib/rook/rook-ceph/rook-ceph.config | base64")
admin_id=$(pod=$(kubectl get pod -n rook-ceph -l app=rook-ceph-operator  -o jsonpath="{.items[0].metadata.name}"); kubectl exec -ti -n rook-ceph ${pod} -- bash -c "echo -n admin|base64")

# Use the key and ID from above to create a secrets object on our Kubernetes cluster
cat <<EOF | oc apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: csi-cephfs-secret
  namespace: default
data:
  # Required if provisionVolume is set to false
  userID: $admin_id
  userKey: $admin_key

  # Required if provisionVolume is set to true
  adminID: $admin_id
  adminKey: $admin_key
EOF

#Create our csi-cephfs storage class
cat <<EOF | oc apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
   name: csi-cephfs
provisioner: cephfs.csi.ceph.com
parameters:
    # Specify a string that identifies your cluster. Ceph CSI supports any
    # unique string. When Ceph CSI is deployed by Rook use the Rook namespace,
    # this value can be found doing this 'oc edit cm rook-ceph-mon-endpoints -n rook-ceph',
    # for example "rook-ceph".
    clusterID: rook-ceph

    # For provisionVolume: "true":
    #   A new volume will be created along with a new Ceph user.
    #   Requires admin credentials (adminID, adminKey).
    # For provisionVolume: "false":
    #   It is assumed the volume already exists and the user is expected
    #   to provide path to that volume (rootPath) and user credentials (userID, userKey).
    # provisionVolume: "true"

    # CephFS filesystem name into which the volume shall be created
    fsName: myfs

    # Ceph pool into which the volume shall be created
    # Required for provisionVolume: "true"
    pool: myfs-data0

    # Root path of an existing CephFS volume
    # Required for provisionVolume: "false"
    # rootPath: /absolute/path
 
    # The secrets have to contain user and/or Ceph admin credentials.
    csi.storage.k8s.io/provisioner-secret-name: csi-cephfs-secret
    csi.storage.k8s.io/provisioner-secret-namespace: default
    csi.storage.k8s.io/node-stage-secret-name: csi-cephfs-secret
    csi.storage.k8s.io/node-stage-secret-namespace: default

    # (optional) The driver can use either ceph-fuse (fuse) or ceph kernel client (kernel)
    # If omitted, default volume mounter will be used - this is determined by probing for ceph-fuse
    # or by setting the default mounter explicitly via --volumemounter command-line argument.
    # mounter: kernel
reclaimPolicy: Delete
mountOptions:
  - noexec
EOF
