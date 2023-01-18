# RHODS OLM Installation

Facilitates RHODS install on any (not just OSD) cluster.


## Installation

Run the following command to install a RHODS instance in your Openshift
cluster from the OLM:

```shell
./setup.sh quay.io/modh/rhods-catalog:v1.1.1-58
```

By default, we use $USER as the `rhods-admin`, if that's not right for you, you
will need to change setup.sh to use your openshift username at the bottom where
it is setting up the rhods-admins/rhods-users for JupyterHub.


## Custom repository

If the images are not stored in the `quay.io/modh` repository, replace the pull
secrets with the corresponding credentials:

```shell
$ oc delete secret modh-idh-cluster-image-puller-pull-secret -n openshift-marketplace
$ oc create secret docker-registry modh-idh-cluster-image-puller-pull-secret \
    --from-file=".dockerconfigjson=~/pull-secret.json" -n openshift-marketplace

$ oc delete secret addon-managed-odh-pullsecret -n redhat-ods-operator
$ oc create secret docker-registry addon-managed-odh-pullsecret \
    --from-file=".dockerconfigjson=~/pull-secret.json" -n redhat-ods-operator

$ oc delete secret addon-managed-odh-pullsecret -n redhat-ods-applications
$ oc create secret docker-registry addon-managed-odh-pullsecret \
    --from-file=".dockerconfigjson=~/pull-secret.json" -n redhat-ods-applications
```


## Clean up

Run the following command to clean up the environment:

```shell
./cleanup.sh
```
