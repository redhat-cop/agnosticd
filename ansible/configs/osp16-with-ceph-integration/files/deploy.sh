#!/bin/bash

THT=/usr/share/openstack-tripleo-heat-templates
CNF=~/templates

openstack overcloud deploy --templates \
-r $CNF/roles_data.yaml \
-n $CNF/network_data.yaml \
-e $THT/environments/network-environment.yaml \
-e $THT/environments/network-isolation.yaml \
-e $THT/environments/net-bond-with-vlans.yaml \
-e $THT/environments/barbican-backend-simple-crypto.yaml \
-e $THT/environments/services/barbican.yaml \
-e $THT/environments/services/octavia.yaml \
-e $THT/environments/services/manila.yaml \
-e $THT/environments/manila-generic-config.yaml \
-e $THT/environments/cinder-backup.yaml \
-e $THT/environments/disable-telemetry.yaml \
-e $CNF/node-info.yaml \
-e $CNF/keystone_domain_specific_ldap_backend.yaml \
-e ~/containers-prepare-parameter.yaml
