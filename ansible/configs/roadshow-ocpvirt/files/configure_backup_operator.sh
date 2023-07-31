cat << EOF | oc apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-adp
  annotations:
    workload.openshift.io/allowed: management
  labels:
    name: openshift-adp
    openshift.io/cluster-monitoring: "true"
---
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: redhat-oadp-operator-group
  namespace: openshift-adp
spec:
  targetNamespaces:
  - openshift-adp
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: redhat-oadp-operator-subscription
  namespace: openshift-adp
spec:
  channel: "stable"
  name: redhat-oadp-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF

cat << EOF | oc apply -f -
apiVersion: objectbucket.io/v1alpha1
kind: ObjectBucketClaim
metadata:
  name: obc-backups
  namespace: openshift-storage
spec:
  storageClassName: openshift-storage.noobaa.io
  generateBucketName: backups
EOF

until oc get secret obc-backups -n openshift-storage; do sleep 30; done

AWS_ACCESS_KEY_ID=$(oc get secret obc-backups -n openshift-storage -o jsonpath='{.data.AWS_ACCESS_KEY_ID}{"\n"}' | base64 -d)
AWS_SECRET_ACCESS_KEY=$(oc get secret obc-backups -n openshift-storage -o jsonpath='{.data.AWS_SECRET_ACCESS_KEY}{"\n"}' | base64 -d)
BUCKET_HOST=$(oc get cm obc-backups -n openshift-storage -o jsonpath='{.data.BUCKET_HOST}{"\n"}')
BUCKET_NAME=$(oc get cm obc-backups -n openshift-storage -o jsonpath='{.data.BUCKET_NAME}{"\n"}')


cat << EOF > ./credentials-velero
[default]
aws_access_key_id=${AWS_ACCESS_KEY_ID}
aws_secret_access_key=${AWS_SECRET_ACCESS_KEY}
EOF

oc create secret generic cloud-credentials -n openshift-adp --from-file cloud=credentials-velero

until oc get dataprotectionapplications.oadp.openshift.io; do sleep 30; done
cat << EOF | oc apply -f -
apiVersion: oadp.openshift.io/v1alpha1
kind: DataProtectionApplication
metadata:
  name: oadp-dpa
  namespace: openshift-adp
spec:
  configuration:
    velero:
      featureFlags:
        - EnableCSI
      defaultPlugins:
        - csi 
        - openshift
        - aws
        - kubevirt
  backupLocations:
    - velero:
        config:
          profile: "default"
          region: "localstorage"
          s3Url: "http://${BUCKET_HOST}"
          s3ForcePathStyle: "true"
        provider: aws
        credential:
          name: cloud-credentials
          key: cloud
        default: true
        objectStorage:
          bucket: ${BUCKET_NAME}
          prefix: velero
EOF

oc label volumesnapshotclass ocs-storagecluster-rbdplugin-snapclass velero.io/csi-volumesnapshot-class=true


