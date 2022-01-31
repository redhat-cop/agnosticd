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


REPO=image-registry.apps-dev.open.redhat.com
for venv in \
    azure_open_envs-ansible2.9-python3.6-2022-01-10 \
    equinix_metal-ansible2.9-python3.6-2021-11-03 \
    equinix_metal-ansible2.9-python3.6-2021-07-02 \
    ansible2.9-python3.6-2021-11-30 \
    ansible2.9-python3.6-2021-01-22; do

    echo "${venv}"
    cp ../../virtualenvs/${venv}.txt requirements.txt
    # pyOpenSSL >= 20 is incompatible with ansible-runner 2.0.4.dev18
    sed -i 's/pyOpenSSL==20\..*/pyOpenSSL==19.1.0/' requirements.txt
    md5sum requirements.txt
    ansible-builder build -v 3 -c . --tag ee-${venv}
    echo "Pushing ${venv}"
    podman push ee-${venv} $REPO/agnosticd/ee-${venv}
done
