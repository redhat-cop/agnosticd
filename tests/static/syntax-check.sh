#!/bin/bash

set -eo pipefail

ORIG=$(cd $(dirname $0); cd ../..; pwd)
ansible_path=${ORIG}/ansible
static=${ORIG}/tests/static

cd ${ORIG}

for i in \
    $(find ${ORIG}/ansible/configs -name 'sample_vars*.y*ml' | sort) \
    ${static}/scenarii/*.{yaml,yml}; do
    echo
    echo '##################################################'
    echo "$(basename $(dirname ${i}))/$(basename ${i})"
    echo '##################################################'


    extra_args=()

    config=$(basename $(dirname "${i}"))

    if ! egrep --quiet ^env_type: ${i}; then
        echo "No env_type found in ${i}"
    fi
    env_type=$(egrep ^env_type: ${i}|cut -d' ' -f 2)

    # Linklight needs to be downloaded
    if [ "${env_type}" = linklight ]; then
        if [ ! -d ${ansible_path}/workdir/linklight ]; then
            echo "Download linklight"
            git clone https://github.com/ansible/workshops.git ${ansible_path}/workdir/linklight
        fi
        touch $(dirname "${i}")/env_secret_vars.yml
        extra_args=(
            -e ANSIBLE_REPO_PATH=${ansible_path}
        )
    fi

    if [ -e "${ansible_path}/configs/${env_type}/hosts" ]; then
        inventory=(-i "${ansible_path}/configs/${env_type}/hosts")
    else
        inventory=(-i "${static}/tox-inventory.txt")
    fi

    # Setup galaxy roles and collections, make sure it works
    ansible-playbook --tags galaxy_roles \
                     "${inventory[@]}" \
                     ${ansible_path}/main.yml \
                     ${extra_args[@]} \
                     -e @${i}

    for playbook in \
        ${ansible_path}/main.yml \
        ${ansible_path}/destroy.yml; do
        ansible-playbook --syntax-check \
                         --list-tasks \
                         "${inventory[@]}" \
                         "${playbook}" \
                         ${extra_args[@]} \
                         -e @${i}
    done
    # lifecycle (stop / start)

    for ACTION in stop start status; do
        ansible-playbook --syntax-check \
                        --list-tasks \
                        "${inventory[@]}" \
                        ${ansible_path}/lifecycle_entry_point.yml \
                        ${extra_args[@]} \
                        -e ACTION=${ACTION} \
                        -e @${i}
    done
done

exit 0
