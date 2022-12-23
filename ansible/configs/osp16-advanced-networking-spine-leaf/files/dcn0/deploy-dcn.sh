#!/bin/bash
THT=/usr/share/openstack-tripleo-heat-templates
STACK=dcn0
source ~/stackrc
#     -e $THT/environments/network-isolation.yaml \
time openstack overcloud deploy \
     --stack $STACK \
     --templates /usr/share/openstack-tripleo-heat-templates/ \
     -r roles_data.yaml \
     -n network_data_spine_leaf.yaml \
     -e ~/dcn-common/central-export.yaml \
     -e site-name.yaml \
     -e dcn0-images-env.yaml \
     -e ~/containers-prepare-parameter.yaml \
     -e network-environment.yaml \
     -e network-environment-dcn.yaml \
     -e ips-from-pool-all.yaml \
     -e overrides.yaml
