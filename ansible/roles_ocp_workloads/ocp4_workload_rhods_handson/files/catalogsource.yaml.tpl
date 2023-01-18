kind: List
metadata: {}
apiVersion: v1
items:
  - apiVersion: operators.coreos.com/v1alpha1
    kind: CatalogSource
    metadata:
      name: addon-managed-odh-catalog
      namespace: openshift-marketplace
    spec:
      displayName: Managed Open Data Hub Operator
      image: ${CATALOG_SOURCE_IMAGE}
      publisher: OSD Red Hat Addons
      sourceType: grpc
      secrets:
        - modh-idh-cluster-image-puller-pull-secret
  - apiVersion: operators.coreos.com/v1alpha2
    kind: OperatorGroup
    metadata:
      name: redhat-layered-product-og
      namespace: redhat-ods-operator
  - apiVersion: operators.coreos.com/v1alpha1
    kind: Subscription
    metadata:
      name: addon-managed-odh
      namespace: redhat-ods-operator
    spec:
      channel: beta
      name: rhods-operator
      source: addon-managed-odh-catalog
      sourceNamespace: openshift-marketplace

