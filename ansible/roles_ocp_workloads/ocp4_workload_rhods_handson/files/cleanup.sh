#! /bin/bash

oc delete subscription addon-managed-odh -n redhat-ods-operator
oc delete operatorgroup redhat-layered-product-og -n redhat-ods-operator
oc delete catalogsource addon-managed-odh-catalog -n openshift-marketplace
oc delete -f /home/cloud-user/olminstall/fakesecret.yaml
oc delete kfdef opendatahub -n redhat-ods-applications --force --grace-period=0 &
oc delete kfdef monitoring -n redhat-ods-monitoring --force --grace-period=0 &
oc delete kfdef rhods-notebooks -n rhods-notebooks --force --grace-period=0 &
oc patch -n redhat-ods-applications kfdef opendatahub --type=merge -p '{"metadata": {"finalizers":null}}'
oc patch -n redhat-ods-monitoring kfdef monitoring --type=merge -p '{"metadata": {"finalizers":null}}'
oc patch -n rhods-notebooks kfdef rhods-notebooks --type=merge -p '{"metadata": {"finalizers":null}}'
oc delete crd kfdefs.kfdef.apps.kubeflow.org
oc delete project redhat-ods-operator --force --grace-period=0
oc delete clusterrolebinding prometheus-scraper
oc delete clusterrole prometheus-scraper
oc delete rolebinding cluster-monitor-rhods-reader -n redhat-ods-monitoring
oc delete service alertmanager -n redhat-ods-monitoring
oc delete service prometheus -n redhat-ods-monitoring
oc delete configmap prometheus -n redhat-ods-monitoring
oc delete configmap alertmanager -n redhat-ods-monitoring
oc delete secret grafana-config -n redhat-ods-monitoring
oc delete secret grafana-proxy-config -n redhat-ods-monitoring
oc delete secret grafana-datasources -n redhat-ods-monitoring
oc delete secret redhat-rhods-deadmanssnitch -n redhat-ods-monitoring
oc delete clusterrolebinding prometheus-scraper
oc delete clusterrolebinding grafana-auth-rb
oc delete clusterrolebinding grafana
oc delete clusterrole prometheus-scraper
oc delete project redhat-ods-applications --force --grace-period=0
oc delete project redhat-ods-monitoring --force --grace-period=0
oc delete project rhods-notebooks --force --grace-period=0
oc delete -f /home/cloud-user/olminstall/modh-idh-cluster-image-puller-secret.yml --namespace=openshift-marketplace
oc delete group rhods-admins
oc delete group rhods-users
