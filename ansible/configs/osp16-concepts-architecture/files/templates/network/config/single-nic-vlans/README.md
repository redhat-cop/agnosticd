This directory contains Heat templates to help configure
VLANs on a single NIC for each Overcloud role.

There are two versions of the controller role template, one with
an external network interface, and another without. If the
external network interface is not configured, the ctlplane address
ranges will be used for external (public) network traffic.

Configuration
-------------

To make use of these templates create a Heat environment that looks
something like this:

  resource\_registry:
    OS::TripleO::BlockStorage::Net::SoftwareConfig: network/config/single-nic-vlans/cinder-storage.yaml
    OS::TripleO::Compute::Net::SoftwareConfig: network/config/single-nic-vlans/compute.yaml
    OS::TripleO::Controller::Net::SoftwareConfig: network/config/single-nic-vlans/controller.yaml
    OS::TripleO::ObjectStorage::Net::SoftwareConfig: network/config/single-nic-vlans/swift-storage.yaml
    OS::TripleO::CephStorage::Net::SoftwareConfig: network/config/single-nic-vlans/ceph-storage.yaml

Or use this Heat environment file:

  environments/net-single-nic-with-vlans.yaml

Configuration with no External Network
--------------------------------------

Same as above except set the following value for the controller role:

    OS::TripleO::Controller::Net::SoftwareConfig: network/config/single-nic-vlans/controller-no-external.yaml

Configuration with IPv6 Networks
--------------------------------

There is no longer a requirement to use controller-v6.yaml for Controller nodes
when deploying with IPv6. You may now define both an IPv4 network and an IPv6
network as default routes by adding both networks to the default_route_networks
list for the Controller role in roles_data.yaml.

Configuration with System Management Network
--------------------------------------------

The Management network is enabled for backwards-compatibility, but
is not included in any roles by default. To enable the optional System
Management network, create a Heat environment that looks something like
this:

  resource\_registry:
    OS::TripleO::Network::Management: ../network/management.yaml
    OS::TripleO::Controller::Ports::ManagementPort: ../network/ports/management.yaml
    OS::TripleO::Compute::Ports::ManagementPort: ../network/ports/management.yaml
    OS::TripleO::CephStorage::Ports::ManagementPort: ../network/ports/management.yaml
    OS::TripleO::ObjectStorage::Ports::ManagementPort: ../network/ports/management.yaml
    OS::TripleO::BlockStorage::Ports::ManagementPort: ../network/ports/management.yaml

Or use this Heat environment file:

  environments/network-management.yaml

Or, add the network to the list of networks used by each role in the role
definition file (e.g. roles_data.yaml). Refer to installation documentation
for procedure to generate a role file for custom roles.
