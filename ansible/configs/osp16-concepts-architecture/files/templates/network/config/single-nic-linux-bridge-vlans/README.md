This directory contains Heat templates to help configure
Vlans on a single NICs for each Overcloud role.

Configuration
-------------

To make use of these templates create a Heat environment that looks
something like this:

  resource\_registry:
    OS::TripleO::BlockStorage::Net::SoftwareConfig: network/config/single-nic-linux-bridge-vlans/cinder-storage.yaml
    OS::TripleO::Compute::Net::SoftwareConfig: network/config/single-nic-linux-bridge-vlans/compute.yaml
    OS::TripleO::Controller::Net::SoftwareConfig: network/config/single-nic-linux-bridge-vlans/controller.yaml
    OS::TripleO::ObjectStorage::Net::SoftwareConfig: network/config/single-nic-linux-bridge-vlans/swift-storage.yaml
    OS::TripleO::CephStorage::Net::SoftwareConfig: network/config/single-nic-linux-bridge-vlans/ceph-storage.yaml

Or use this Heat environment file:

  environments/net-single-nic-linux-bridge-with-vlans.yaml

Configuration with IPv6 Networks
--------------------------------

There is no longer a requirement to use controller-v6.yaml for Controller nodes
when deploying with IPv6. You may now define both an IPv4 network and an IPv6
network as default routes by adding both networks to the default_route_networks
list for the Controller role in roles_data.yaml.
