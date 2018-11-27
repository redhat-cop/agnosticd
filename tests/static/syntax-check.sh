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
    touch ${ansible_path}/configs/${env_type}/env_secret_vars.yml
    ansible-playbook --syntax-check \
                     --list-tasks \
                     "${inventory[@]}" \
                     -e ANSIBLE_REPO_PATH=${ansible_path} \
                     ${ansible_path}/main.yml \
                     -e @${i}
    ansible-playbook --syntax-check \
                     --list-tasks \
                     "${inventory[@]}" \
                     -e ANSIBLE_REPO_PATH=${ansible_path} \
                     ${ansible_path}/destroy.yml \
                     -e @${i}
    ansible-playbook --syntax-check \
                     --list-tasks \
                     "${inventory[@]}" \
                     -e ANSIBLE_REPO_PATH=${ansible_path} \
                     ${ansible_path}/configs/${env_type}/destroy_env.yml \
                     -e @${i}

    echo
    echo "Without setting ANSIBLE_REPO_PATH:"

    ansible-playbook --syntax-check \
                     --list-tasks \
                     "${inventory[@]}" \
                     ${ansible_path}/main.yml \
                     -e @${i}
    ansible-playbook --syntax-check \
                     --list-tasks \
                     "${inventory[@]}" \
                     ${ansible_path}/destroy.yml \
                     -e @${i}
    ansible-playbook --syntax-check \
                     --list-tasks \
                     "${inventory[@]}" \
                     ${ansible_path}/configs/${env_type}/destroy_env.yml \
                     -e @${i}

done
