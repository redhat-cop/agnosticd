#!/bin/bash

if [ -z "$1" ]
then
  echo "Usage: $0 <project>"
  exit 1
fi

project=$1

tmp=/tmp/term.$$.json

test=`oc get project $project | grep Terminating`

if [ -z "$test" ]
then
  echo "Error: Project $project does not exist or is not in Terminating state."
  exit 1
fi

echo "Force terminating project $project..."

oc get project $project -o json > $tmp
sed -i 's/"kubernetes"//' $tmp
sed -i 's/"project.openshift.io\/v1"/"v1"/' $tmp
oc proxy -p 28001 > /dev/null &
sleep 1
curl -s -k -H "Content-Type: application/json" -X PUT --data-binary @$tmp http://127.0.0.1:28001/api/v1/namespaces/$project/finalize > /dev/null
rm -f $tmp
sleep 5

oc get project $project > /dev/null 2>&1

if [ $? != 1 ]
then
  echo "Error: Project $project did not go away as expected."
else
  echo "The project $project went away as expected."
fi

kill %1 >/dev/null 2>&1