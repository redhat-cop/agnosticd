#!/bin/bash
THT=/usr/share/openstack-tripleo-heat-templates/
CNF=/home/stack/templates/
openstack overcloud deploy --templates $THT \
-r $CNF/roles_data.yaml \
-n $CNF/network_data.yaml \
-e ~/containers-prepare-parameter.yaml \
-e $THT/environments/services/barbican.yaml \
-e $THT/environments/barbican-backend-simple-crypto.yaml \
-e $THT/environments/cinder-backup.yaml \
-e $CNF/environments/node-info.yaml \
-e $THT/environments/network-isolation.yaml \
-e $CNF/environments/network-environment.yaml \
-e $CNF/environments/ips-from-pool-all.yaml \
-e $CNF/scheduler-hints.yaml \
-e $CNF/environments/fix-nova-reserved-host-memory.yaml \
-e $CNF/environments/barbican.yaml

