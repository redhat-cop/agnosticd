#!/bin/bash

cat <<EOF | oc apply -f -
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: worker
  name: 01-sebool
spec:
  config:
    ignition:
      version: 3.2.0
    systemd:
      units:
      - contents: |
          [Unit]
          Description=Enable container_manage_cgroup on worker nodes
          Before=kubelet.service

          [Service]
          ExecStart=/usr/sbin/setsebool container_manage_cgroup 1

          [Install]
          WantedBy=multi-user.target
        enabled: true
        name: sebool.service
EOF

sleep 10
oc wait mcp/worker --for condition=updated