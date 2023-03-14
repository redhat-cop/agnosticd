#!/bin/sh
# Reboot the nodes
masternodes=$(oc get nodes -l node-role.kubernetes.io/master= -o jsonpath='{.items[*].metadata.name}')
workernodes=$(oc get nodes -l node-role.kubernetes.io/worker= -o jsonpath='{.items[*].metadata.name}')
for node in ${masternodes[@]}
do
        ssh -o  StrictHostKeyChecking=no core@$node sudo reboot
done
# Wait till the API is available again
sleep 10
while ! curl --output /dev/null --silent --connect-timeout 1 -k https://api.ocp.example.com:6443/healthz; do sleep 1 && echo -n .; done;
sleep 120
for node in ${workernodes[@]}
do
        ssh -o  StrictHostKeyChecking=no core@$node sudo reboot
done
sleep 10
while ! curl --output /dev/null --silent --connect-timeout 1 -k http://test.apps.ocp.example.com/; do sleep 1 && echo -n .; done;
