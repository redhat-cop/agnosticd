#!/usr/bin/env bash
set -eu

    # DONE   2 azure_open_envs-ansible2.9-python3.6-2022-01-10
    # DONE   2 equinix_metal-ansible2.9-python3.6-2021-11-03
    # FAIL   2 openstack-ansible-2.8    (python2, won't create)
    # DONE   3 equinix_metal-ansible2.9-python3.6-2021-07-02
    # FAIL   4 openstack-ansible-2.9.12    (python2, won't create)
    # DONE  77 ansible2.9-python3.6-2021-11-30
    # FAIL  82 aws-ansible-2.9    (python2, won't create)
    # FAIL 215 openstack-ansible-2.9 (python2, won't create)
    # DONE 244 ansible2.9-python3.6-2021-01-22


for venv in \
    azure_open_envs-ansible2.9-python3.6-2022-01-10 \
    equinix_metal-ansible2.9-python3.6-2021-07-02 \
    ansible2.9-python3.6-2021-01-22 \
    ansible2.9-python3.6-2021-11-30 ; do

    echo "${venv}"
    cp ../../virtualenvs/${venv}.txt requirements.txt
    # pyOpenSSL >= 20 is incompatible with ansible-runner 2.0.4.dev18
    sed -i 's/pyOpenSSL==20\..*/pyOpenSSL==19.1.0/' requirements.txt
    md5sum requirements.txt

    # public
    ansible-builder build -v 3 -c . \
        --build-arg EE_BASE_IMAGE=quay.io/ansible/ansible-runner:stable-2.9-latest \
        --tag ee-${venv}-public

    # private (subscriptions)
    ansible-builder build -v 3 -c . \
        --build-arg EE_BASE_IMAGE=registry.redhat.io/ansible-automation-platform-21/ee-29-rhel8:1.0.0-46 \
        --tag ee-${venv}

    echo "Pushing ${venv}"

    # Public
    podman push ee-${venv}-public quay.io/redhat-gpte/agnosticd-images:ee-${venv}

    # Private (subscriptions)
    REPO=image-registry.apps-dev.open.redhat.com
    podman push ee-${venv} $REPO/agnosticd/ee-${venv}
done

# only one ansible 2.11
venv=equinix_metal-ansible2.9-python3.6-2021-11-03
echo "${venv}"
cp ../../virtualenvs/${venv}.txt requirements.txt
# pyOpenSSL >= 20 is incompatible with ansible-runner 2.0.4.dev18
sed -i 's/pyOpenSSL==20\..*/pyOpenSSL==19.1.0/' requirements.txt
md5sum requirements.txt
ansible-builder build -v 3 -c . \
    --build-arg EE_BASE_IMAGE=quay.io/ansible/ansible-runner:stable-2.11-latest \
    --tag ee-${venv}-public

# private (subscriptions)
ansible-builder build -v 3 -c . \
    --build-arg EE_BASE_IMAGE=registry.redhat.io/ansible-automation-platform-21/ee-supported-rhel8:1.0.1-11 \
    --tag ee-${venv}

echo "Pushing ${venv}"
# Public
podman push ee-${venv}-public quay.io/redhat-gpte/agnosticd-images:ee-${venv}

# Private
REPO=image-registry.apps-dev.open.redhat.com
podman push ee-${venv}-public $REPO/agnosticd/ee-${venv}
