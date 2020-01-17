#!/bin/bash

# deletes "Hello, OpenShift" app previously deployed to X namespaces using deploy.sh

x=$(cat .ns)

ns_prefix="hello-openshift-"
app_manifest=https://raw.githubusercontent.com/openshift/origin/master/examples/hello-openshift/hello-pod.json

for i in $(seq 1 $x); do
	oc delete project "$ns_prefix""$i"
done

echo "Done..." 
