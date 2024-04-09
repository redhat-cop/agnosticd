#!/bin/bash

set -eo pipefail

REQUIRED_VARS=("AGD_AWS_ACCESS_KEY_ID" "AGD_AWS_SECRET_ACCESS_KEY" "AGD_HOME" "AGD_EXECUTION_DIR" "AGD_SECRETS_YAML")

for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    echo "ERROR: Required environment vars are missing"
    echo "ERROR: Run the following command to configure your shell"
    echo "ERROR: source init.sh aws-access-key-id aws-secret-access-key sandbox"
    exit 1
  fi
done

echo "----------------------------------------"
env | grep "AGD_"
echo "----------------------------------------"

AGD_CONFIG_NAME=$1
AGD_OCP_WORKLOADS=$2
AGD_EXTRA_PARAMS=$3

if [[ "$AGD_CONFIG_NAME" = "ocp-workloads" ]] && [[ -f "$AGD_OCP_WORKLOADS" ]]; then
  cat ${AGD_HOME}/${AGD_EXECUTION_DIR}/ocp-workloads-base.yml ${AGD_OCP_WORKLOADS} > ${AGD_HOME}/${AGD_EXECUTION_DIR}/ocp-workloads.yml
elif [[ "$AGD_CONFIG_NAME" = "ocp-workloads" ]]; then
  echo "ERROR: $AGD_OCP_WORKLOADS file not found"
  exit 1
fi

AGD_CONFIG_LIST=("rosa" "ocp4-cluster" "ocp-workloads")
if [[ " ${AGD_CONFIG_LIST[*]} " =~ " ${AGD_CONFIG_NAME} " ]]; then
  podman --version
  podman run \
  --privileged \
  --interactive \
  --tty \
  --rm \
  --name=agnosticd-${AGD_GUID} \
  --volume=${AGD_HOME}:/runner/agnosticd \
  --workdir=/runner/agnosticd \
  quay.io/agnosticd/ee-multicloud:latest \
  ansible-playbook \
  ansible/main.yml \
  --extra-vars=@${AGD_EXECUTION_DIR}/${AGD_CONFIG_NAME}.yml \
  --extra-vars=@${AGD_SECRETS_YAML} \
  --extra-vars=aws_access_key_id=${AGD_AWS_ACCESS_KEY_ID} \
  --extra-vars=aws_secret_access_key=${AGD_AWS_SECRET_ACCESS_KEY} $3
else
  echo "ERROR: Config [${AGD_CONFIG_NAME}] not found"
  exit 1
fi
