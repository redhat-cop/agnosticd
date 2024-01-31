#!/bin/bash
for proj in `oc get projects|grep Terminating|awk '{print $1}'`
do
  echo $proj
  /usr/local/bin/wack_terminating_project.sh $proj
done