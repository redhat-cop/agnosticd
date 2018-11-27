#!/bin/bash

set -eo pipefail

ORIG=$(cd $(dirname $0); cd ../..; pwd)
ansible_path=${ORIG}/ansible
static=${ORIG}/tests/static

cd ${ORIG}

for i in ${static}/scenarii/*.{yaml,yml}; do
    config=$(basename "${i}")

    env_type=$(egrep ^env_type: ${i}|cut -d' ' -f 2)

    if [ -e "${ansible_path}/configs/${env_type}/hosts" ]; then
        inventory=(-i "${ansible_path}/configs/${env_type}/hosts")
    else
        inventory=(-i "${static}/tox-inventory.txt")
    fi

    echo
    echo '############################'
    echo "${config}"
    echo '############################'

    for playbook in \
        ${ansible_path}/main.yml \
        ${ansible_path}/destroy.yml \
        ${ansible_path}/configs/${env_type}/destroy_env.yml \
        ${ansible_path}/configs/${env_type}/scaleup.yml; do
        if [ -e "${playbook}" ]; then
            echo
            echo -n "With ANSIBLE_REPO_PATH: "
            ansible-playbook --syntax-check \
                             --list-tasks \
                             "${inventory[@]}" \
                             -e ANSIBLE_REPO_PATH=${ansible_path} \
                             "${playbook}" \
                             -e @${i}
            echo -n "Without ANSIBLE_REPO_PATH: "

            ansible-playbook --syntax-check \
                            --list-tasks \
                            "${inventory[@]}" \
                            "${playbook}" \
                            -e @${i}
        fi
    done
done
