#!/bin/bash

export NAME="infra-$1"
oc get machineset -n openshift-machine-api -o json\
  | jq '.items[0]'\
  | jq '.metadata.name=env["NAME"]'\
  | jq '.spec.selector.matchLabels."machine.openshift.io/cluster-api-machineset"=env["NAME"]'\
  | jq '.spec.template.metadata.labels."machine.openshift.io/cluster-api-machineset"=env["NAME"]'\
  | jq '.spec.template.spec.metadata.labels."node-role.kubernetes.io/infra"=""'\
  | jq '.spec.template.spec.providerSpec.value.instanceType="m5.4xlarge"'\
  | jq 'del (.metadata.annotations)'\
  | jq '.metadata.labels += {"machineset":"infra"}'\
  | jq '.spec.replicas=3'\
  | oc create -f -