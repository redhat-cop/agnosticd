cat << EOF | oc apply -f -
apiVersion: nmstate.io/v1
kind: NodeNetworkConfigurationPolicy
metadata:
  name: br-flat
spec:
  nodeSelector:
    node-role.kubernetes.io/worker: ""
  desiredState:
    interfaces:
      - name: br-flat
        description: Linux bridge with enp3s0 as a port
        type: linux-bridge
        state: up
        ipv4:
          dhcp: false
          enabled: false
        bridge:
          options:
            stp:
              enabled: false
          port:
            - name: enp3s0
EOF

