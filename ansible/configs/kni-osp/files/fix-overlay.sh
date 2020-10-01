#!/usr/bin/env bash

export KUBECONFIG=/home/cloud-user/scripts/ocp/auth/kubeconfig

for i in $(oc get nodes -o wide | awk '/NotReady/ {print $6;}');
do
  ssh -o StrictHostKeyChecking=no core@$i "sudo systemctl stop kubelet crio && sudo rm -rf /var/lib/containers/storage/overlay/* && sudo rm -f /var/lib/containers/storage/overlay-layers/layers.json && sudo systemctl restart crio kubelet"
done
