#!/bin/bash

# wgets routes created in previously deployed "Hello,OpenShift" app

GREEN='\033[0;33m'
NC='\033[0m'

x=$(cat .ns)

ns_prefix="hello-openshift-"

for i in $(seq 1 $x); do
        echo -e "${GREEN}Probing app in namespace ""$ns_prefix""$i""${NC}"	
	route=$(oc get route hello-openshift -n "$ns_prefix""$i" -o go-template='{{ .spec.host }}{{ println }}')
	curl http://${route}
done
 
