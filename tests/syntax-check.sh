#!/bin/bash

set -eo pipefail

ORIG=$(cd $(dirname $0); cd ..; pwd)
ansible_path=${ORIG}/ansible

for i in ${ORIG}/tests/scenarii/*.{yaml,yml}; do
    config=$(basename "${i}")

    env_type=$(egrep ^env_type: ${i}|cut -d' ' -f 2)

    if [ -e "${ansible_path}/configs/${env_type}/hosts" ]; then
        inventory=(-i "${ansible_path}/configs/${env_type}/hosts")
    else
        inventory=()
    fi

    echo '############################'
    echo "${config}"
    echo '############################'
    touch ${ansible_path}/configs/${env_type}/env_secret_vars.yml
    ansible-playbook --syntax-check \
                     --list-tasks \
                     "${inventory[@]}" \
                     -e ANSIBLE_REPO_PATH=${ansible_path} \
                     ${ORIG}/ansible/main.yml \
                     -e @${i}
    ansible-playbook --syntax-check \
                     --list-tasks \
                     "${inventory[@]}" \
                     -e ANSIBLE_REPO_PATH=${ansible_path} \
                     ${ORIG}/ansible/destroy.yml \
                     -e @${i}
done
