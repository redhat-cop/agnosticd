#!/bin/bash

usage() {
    echo "$0 [CONFIG] [STAGE]"
    echo
    echo "CONFIG: ALL | ocp-workshop | ocp-demo-lab | ans-tower-lab | ..."
    echo "STAGE: test | prod | rhte"
}

if [ -z "${1}" ] || [ -z "${2}" ]; then
    usage
    exit 1
fi

set -u -o pipefail

ORIG=$(cd $(dirname $0); pwd)

prompt_continue() {
    # call with a prompt string or use a default
    read -r -p "${1:-Continue? [Y/n]} " response

    if [ -z "${response}" ]; then
        true
    else
        case "${response}" in
            yes|y|Y|Yes|YES) true ;;
            *) false ;;
        esac
    fi
}

configs=$1
stage=$2

if [ "${configs}" = "ALL" ]; then
    configs=$(ls ${ORIG}/../ansible/configs)
fi

git log -1
echo
echo "About to tag this commit."
prompt_continue || exit 0

for config in ${configs}; do
    last=$(git tag -l|grep ^${config}-${stage} |sort -V|tail -n 1|egrep -o '[0-9]+\.[0-9]+$')
    if [ -z "${last}" ]; then
        echo "INFO: no version found for ${config}, skipping"
        echo "Do you want to create it ?"
        prompt_continue || continue

        next_tag=${config}-${stage}-0.1
    else
        major=$(echo $last|egrep -o '^[0-9]+')
        minor=$(echo $last|egrep -o '[0-9]+$')
        next_tag=${config}-${stage}-${major}.$(( minor + 1))
    fi

    echo "will now perform 'git tag ${next_tag}'"
    prompt_continue || continue

    git tag ${next_tag}

    echo "will now perform 'git push origin ${next_tag}"
    prompt_continue || continue
    git push origin ${next_tag}
done
