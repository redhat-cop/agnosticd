#!/bin/bash

# deploys "Hello, OpenShift" app to random X number of namespaces

echo "Number of namespaces? "; read x

echo $x > .ns

ns_prefix="hello-openshift-"
app_manifest=https://raw.githubusercontent.com/openshift/origin/master/examples/hello-openshift/hello-pod.json

for i in $(seq 1 $x); do
	oc create namespace "$ns_prefix""$i"
        oc apply -f $app_manifest -n "$ns_prefix""$i"
        oc expose pod hello-openshift -n "$ns_prefix""$i"
        oc expose svc hello-openshift -n "$ns_prefix""$i"
done

echo "Finding routes..."

for i in $(seq 1 $x); do
	oc get route hello-openshift -n "$ns_prefix""$i" -o go-template='{{ .spec.host }}{{ println }}'
done
 
