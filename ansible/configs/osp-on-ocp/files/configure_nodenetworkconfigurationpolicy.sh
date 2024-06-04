cat << EOF | oc apply -f -
---
apiVersion: nmstate.io/v1
kind: NodeNetworkConfigurationPolicy
metadata:
  name: ovs-br-flat
spec:
  nodeSelector:
    node-role.kubernetes.io/worker: ''
  desiredState:
    interfaces:
    - name: ovs-br
      description: |-
        An OVS with enp3s0 uplink
      type: ovs-bridge
      state: up
      bridge:
        options:
          stp: false
        port:
        - name: enp3s0
    ovn:
      bridge-mappings:
      - localnet: vm-network
        bridge: ovs-br
        state: present
EOF

cat << EOF | oc apply -f -
---
apiVersion: operator.openshift.io/v1
kind: Network
metadata:
  name: cluster
spec:
  useMultiNetworkPolicy: true
EOF
