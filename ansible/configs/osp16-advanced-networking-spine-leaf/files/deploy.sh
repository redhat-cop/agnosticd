#!/bin/bash

THT=/usr/share/openstack-tripleo-heat-templates
CNF=~/templates

openstack overcloud deploy --templates \
-r $CNF/roles_data_spine_leaf.yaml \
-n $CNF/network_data_spine_leaf.yaml \
-e $THT/environments/network-isolation.yaml \
-e $THT/environments/disable-telemetry.yaml \
-e $THT/environments/low-memory-usage.yaml \
-e $THT/environments/net-multiple-nics.yaml \
-e $CNF/environments/network-environment.yaml \
-e $CNF/node-config.yaml \
-e $CNF/ips-from-pool-all.yaml \
-e $CNF/scheduler-hints.yaml \
-e ~/containers-prepare-parameter.yaml
