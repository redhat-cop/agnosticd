#!/bin/bash

usage() {
    echo "$0 [TAGNAME]"
    echo "   or"
    echo "$0 [CONFIG] [STAGE]"
    echo
    echo "TAGNAME: any tag without the version. Usually same as CONFIG-STAGE."
    echo "CONFIG: ocp-workshop | ocp-demo-lab | ans-tower-lab | ..."
    echo "STAGE: test | prod | rhte | ..."
    echo
    echo "ex:"
    echo "$0 ocp4-workshop-prod"
    echo "  will increment the version to ocp4-workshop-prod-1.24 if 1.23 exists."
}

if [ -z "${1}" ]; then
    usage
    exit 1
fi

config=$1
stage=$2

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

git log -1
echo
echo "About to tag this commit."
prompt_continue || exit 0

if [ -z "${stage}" ]; then
    tagname="${config}"
else
    tagname="${config}-${stage}"
    if echo "${tagname}" | grep -q -e "-${stage}-${stage}"; then
        echo
        echo "ERROR: ${tagname} has '${stage}' twice, please use ${stage} only once."
        echo
        exit 1
    fi
fi
last=$(git tag -l|egrep "^${tagname}-[0-9]+" |sort -V|tail -n 1)
if [ -n "${last}" ]; then
    echo "Found tag ${last}"
fi

last_version=$(echo "${last}"|egrep -o '[0-9]+\.[0-9]+\.[0-9]+$')
if [ -z "${last_version}" ]; then
    last_version=$(echo "${last}"|egrep -o '[0-9]+\.[0-9]+$')
    if [ -z "${last_version}" ]; then
        echo "INFO: no version found for ${tagname}, skipping"
        echo "Do you want to create it ?"
        prompt_continue || exit 0

        next_tag=${tagname}-0.1
    else
        major=$(echo $last_version|egrep -o '^[0-9]+')
        minor=$(echo $last_version|egrep -o '[0-9]+$')
        next_tag=${tagname}-${major}.$(( minor + 1))
    fi
else
    # Semantic versioning
    major=$(echo $last_version|cut -f1 -d.)
    minor=$(echo $last_version|cut -f2 -d.)
    patch=$(echo $last_version|cut -f3 -d.)
    next_tag=${tagname}-${major}.${minor}.$(( patch + 1))
fi

echo "will now perform 'git tag ${next_tag}'"
prompt_continue || exit 0

git tag ${next_tag}

echo "will now perform 'git push origin ${next_tag}"
prompt_continue || exit 0
git push origin ${next_tag}
