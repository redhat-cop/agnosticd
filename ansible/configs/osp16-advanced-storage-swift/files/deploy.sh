#!/bin/bash
sudo dnf module disable -y container-tools:rhel8
sudo dnf module enable -y container-tools:3.0
sudo yum install -y python3-tripleoclient
openstack tripleo container image prepare default   --output-env-file containers-prepare-parameter.yaml
sed -i "s/registry.redhat.io/192.168.56.253/" containers-prepare-parameter.yaml
cat <<EOF > $HOME/standalone_parameters.yaml
parameter_defaults:
  CloudName: 172.16.7.200
  ControlPlaneStaticRoutes: []
  Debug: true
  DeploymentUser: $USER
  DnsServers:
    - 8.8.8.8
  DockerInsecureRegistryAddress:
    - allinone.ctlplane.localdomain:8787
    - localhost:8787
    - 192.168.56.253
  NeutronPublicInterface: eth1
  NeutronDnsDomain: localdomain
  NeutronBridgeMappings: datacentre:br-ctlplane
  NeutronPhysicalBridge: br-ctlplane
  StandaloneEnableRoutedNetworks: false
  StandaloneHomeDir: $HOME
  StandaloneLocalMtu: 1500
  SwiftPassword: r3dh4t1!
  AdminPassword: r3dh4t1!
EOF

sudo openstack tripleo deploy   --templates   --local-ip=172.16.7.200/24   -e /usr/share/openstack-tripleo-heat-templates/environments/standalone/standalone-tripleo.yaml   -e /usr/share/openstack-tripleo-heat-templates/environments/services/neutron-ovs.yaml   -r /usr/share/openstack-tripleo-heat-templates/roles/Standalone.yaml   -e $HOME/containers-prepare-parameter.yaml   -e $HOME/standalone_parameters.yaml   --output-dir $HOME   --standalone
