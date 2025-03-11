#!/bin/bash
set -eo pipefail

ORIG=$(cd $(dirname $0); cd ../..; pwd)
ansible_path=${ORIG}/ansible
static=${ORIG}/tests/static

cd ${ORIG}

output=$(mktemp)

baseref=$1
headref=$2

# find_yamllint() finds the closest .yamllint file in current or
# parent dirs.
# The result is printed on stdout.
# If no yamllint is found, nothing is printed.
find_yamllint() {
    local f=$1
    local dir
    if [ -d "${f}" ]; then
        dir="${f}"
    else
        dir="$(dirname "${f}")"
    fi

    while true; do
        if [ -e "${dir}/.yamllint" ]; then
            echo "${dir}/.yamllint"
            return 0
        fi

        # not found
        if [ "${dir}" = "." ] || [ "${dir}" = "${ORIG}" ] || [ "${dir}" = "/" ]; then
            return 2
        fi

        # Go one dir up
        dir=$(dirname "${dir}")
    done
}

# Given a specific directory or file, this function runs yamllint
# with the appropriate .yamllint conf file.
do_yamllint() {
    local f=$1
    local conf

    if [ -f "${f}" ]; then
        [[ $f =~ \.ya?ml$ ]] || [[ $f =~ \.yamllint$ ]] || return
    fi

    if ! conf=$(find_yamllint "${f}"); then
        echo "WARNING ........ yamllint:  No conf .yamllint found for ${f}"
        return
    fi

    (
        f=$(realpath "${f}")
        cd $(dirname ${conf})
        yamllint "${f}" &> $output
    )

    if [ $? = 0 ]; then
        echo "OK .......... yamllint ${f}"
    else
        echo "FAIL ........ yamllint ${f}"
        echo
        cat $output
        exit 2
    fi
}

do_ansible_syntax() {
    i="${1}"
    item=$(basename $(dirname ${i}))/$(basename ${i})

    extra_args=()

    config=$(basename $(dirname "${i}"))

    if ! egrep --quiet ^env_type: ${i}; then
        echo "No env_type found in ${i}"
    fi
    env_type=$(egrep ^env_type: ${i}|cut -d' ' -f 2)

    # Ansible Workshops AKA as Linklight needs to be downloaded
    if [ "${env_type}" = linklight ] || [ "${env_type}" = ansible-workshops ] || [ "${env_type}" = aap2-ansible-workshops ]; then
        if [ ! -d ${ansible_path}/workdir/${env_type} ]; then
            set +e

            git clone --branch devel \
                https://github.com/ansible/workshops.git \
                ${ansible_path}/workdir/${env_type} &> $output

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
}

if [[ ${baseref} ]]; then
    ##########################################################
    # PULL REQUEST
    # SHORT version for pull_request action, only a few files
    ##########################################################
    changed_files=$(mktemp)
    # look for Added or modified files only
    git diff \
        --no-commit-id \
        --name-only \
        --diff-filter=AM \
        origin/${baseref}...${headref} > $changed_files

    set +e
    while read f; do
        if [[ ${f} =~ .*\.ya?ml ]]; then
           do_yamllint "${f}"
        fi
    done < ${changed_files}

    # look at all files of the PR, then filter the configs
    changed_configs=$(mktemp)

    git diff \
        --no-commit-id \
        --name-only \
        origin/${baseref}...${headref} \
        | grep ansible/configs \
        | perl -pe 's{.*ansible/configs/([^/]+).*}{$1}' \
        | sort \
        | uniq > ${changed_configs}

    while read f; do
        for i in $(find ansible/configs/${f} ! -path "ansible/configs/archive/*" -name 'sample_vars*.y*ml' | sort); do
            do_ansible_syntax "${i}"
        done
    done < ${changed_configs}
    set -e
else
    set +e
    ##########################################################
    # Push
    # LONG version for push action
    ##########################################################
    for YAMLLINT in $(find ansible -name .yamllint ! -path "ansible/configs/archive/*"); do
        do_yamllint "$(dirname ${YAMLLINT})"
    done
    set -e

    for i in $(find ${ORIG}/ansible/configs ! -path "${ORIG}/ansible/configs/archive/*" -name 'sample_vars*.y*ml' | sort); do
        do_ansible_syntax "${i}"
    done
fi

exit 0
