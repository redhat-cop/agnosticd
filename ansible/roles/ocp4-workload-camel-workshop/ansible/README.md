# Installation

## Ansible

### Run with docker

Run using the container based executing environment:

OCP_USERNAME="admin"
OCP_VERSION="4.11"

```sh
docker run -i -t --rm --entrypoint /usr/local/bin/ansible-playbook \
		-v $PWD:/runner \
		-v ~/tmp/kube-rhpds:/home/runner/.kube/config \
		quay.io/agnosticd/ee-multicloud:v0.0.11  \
		-e="ocp_username=${OCP_USERNAME}" \
		-e="ocp_version=${OCP_VERSION}" \
		./install.yaml
```