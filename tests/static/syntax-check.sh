#!/bin/bash

set -eo pipefail

ORIG=$(cd $(dirname $0); cd ../..; pwd)
ansible_path=${ORIG}/ansible
static=${ORIG}/tests/static

cd ${ORIG}

output=$(mktemp)

set +e
for YAMLLINT in $(find ansible -name .yamllint); do
    cd $(dirname $YAMLLINT)
    yamllint .  &> $output
    if [ $? = 0 ]; then
        echo "OK .......... yamllint ${YAMLLINT}"
    else
        echo "FAIL ........ yamllint ${YAMLLINT}"
        echo
        cat $output
        exit 2
    fi
    cd ${ORIG}
done
set -e


for i in \
    $(find ${ORIG}/ansible/configs -name 'sample_vars*.y*ml' | sort); do

    item=$(basename $(dirname ${i}))/$(basename ${i})

    extra_args=()

    config=$(basename $(dirname "${i}"))

    if ! egrep --quiet ^env_type: ${i}; then
        echo "No env_type found in ${i}"
    fi
    env_type=$(egrep ^env_type: ${i}|cut -d' ' -f 2)

    # Ansible Workshops AKA as Linklight needs to be downloaded
    if [ "${env_type}" = linklight ] || [ "${env_type}" = ansible-workshops ]; then
        if [ ! -d ${ansible_path}/workdir/${env_type} ]; then
            set +e
            git clone --branch master https://github.com/ansible/workshops.git ${ansible_path}/workdir/${env_type} &> $output
            if [ $? = 0 ]; then
                commit=$(cd ${ansible_path}/workdir/${env_type}; PAGER=cat git show --no-patch --format=oneline --no-color)
                echo "OK .......... ${item} / Download ansible-workshop -- $commit"
            else
                echo "FAIL ........ ${item} / Download ansible-workshop"
                echo
                cat $output
                exit 2
            fi

            set -e
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
    set +e
    ansible-playbook --tags galaxy_roles \
                     "${inventory[@]}" \
                     ${ansible_path}/main.yml \
                     ${extra_args[@]} \
                     -e @${i} &> $output

    if [ $? = 0 ]; then
        echo "OK .......... Galaxy roles ${item}"
    else
        echo "FAIL ........ Galaxy roles ${item}"
        echo
        cat $output
        exit 2
    fi

    for playbook in \
        ${ansible_path}/main.yml \
        ${ansible_path}/destroy.yml; do

        ansible-playbook --syntax-check \
                         --list-tasks \
                         "${inventory[@]}" \
                         "${playbook}" \
                         ${extra_args[@]} \
                         -e @${i} &> $output
        if [ $? = 0 ]; then
            echo "OK .......... syntax-check ${item} / ${playbook}"
        else
            echo "FAIL ........ syntax-check ${item} / ${playbook}"
            echo
            cat $output
            exit 2
        fi
    done
    # lifecycle (stop / start)

    for ACTION in stop start status; do
        ansible-playbook --syntax-check \
                        --list-tasks \
                        "${inventory[@]}" \
                        ${ansible_path}/lifecycle_entry_point.yml \
                        ${extra_args[@]} \
                        -e ACTION=${ACTION} \
                        -e @${i} &> $output
        if [ $? = 0 ]; then
            echo "OK .......... syntax-check ${item} / lifecycle ${ACTION}"
        else
            echo "FAIL ........ syntax-check ${item} / lifecycle ${ACTION}"
            echo
            cat $output
            exit 2
        fi
    done
done

exit 0
