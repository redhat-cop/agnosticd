#!/bin/bash
THT=/usr/share/openstack-tripleo-heat-templates/
CNF=/home/stack/templates/
openstack overcloud deploy --templates $THT \
-r $CNF/roles_data.yaml \
-n $CNF/network_data.yaml \
-e ~/containers-prepare-parameter.yaml \
-e $THT/environments/ceph-ansible/ceph-rgw.yaml \
-e $THT/environments/ceph-ansible/ceph-mds.yaml \
-e $THT/environments/ceph-ansible/ceph-ansible.yaml \
-e $THT/environments/cinder-volume-active-active.yaml \
-e $THT/environments/services/manila.yaml \
-e $THT/environments/manila-cephfsganesha-config.yaml \
-e $CNF/environments/node-info.yaml \
-e $THT/environments/network-isolation.yaml \
-e /usr/share/openstack-tripleo-heat-templates/environments/services/neutron-ovs.yaml \
-e $CNF/environments/network-environment.yaml \
-e $CNF/environments/ips-from-pool-all.yaml \
-e $CNF/ceph-config.yaml \
-e $CNF/scheduler-hints.yaml \
-e $CNF/environments/fix-nova-reserved-host-memory.yaml

