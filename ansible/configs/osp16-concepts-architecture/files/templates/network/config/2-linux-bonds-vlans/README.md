This directory contains Heat templates to demonstrate configuration of
VLANs on 2 Linux bonds, each with a pair of NICs, for each Overcloud role.
The Tenant network does not need to be on a bridge in order for VXLAN to
function, but the Tenant network appears on the bridge interface in order
to group tenant VLAN traffic and VXLAN traffic together.

Configuration
-------------

To make use of these templates create a Heat environment that looks
something like this:

  resource\_registry:
    OS::TripleO::BlockStorage::Net::SoftwareConfig: network/config/2-linux-bonds-vlans/cinder-storage.yaml
    OS::TripleO::Compute::Net::SoftwareConfig: network/config/2-linux-bonds-vlans/compute.yaml
    OS::TripleO::Controller::Net::SoftwareConfig: network/config/2-linux-bonds-vlans/controller.yaml
    OS::TripleO::ObjectStorage::Net::SoftwareConfig: network/config/2-linux-bonds-vlans/swift-storage.yaml
    OS::TripleO::CephStorage::Net::SoftwareConfig: network/config/2-linux-bonds-vlans/ceph-storage.yaml

Or use this Heat environment file:

  environments/net-2-bonds-with-vlans.yaml

Configuration with no External Network
--------------------------------------

Edit roles_data.yaml to remove the External network from the Controller role.

Configuration with System Management Network
--------------------------------------------

The Management network is enabled for backwards-compatibility, but
is not included in any roles by default.

Add the network to the list of networks used by each role in the role
definition file (e.g. roles_data.yaml). Refer to installation documentation
for procedure to generate a role file for custom roles.

