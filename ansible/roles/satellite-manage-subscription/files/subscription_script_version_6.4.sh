#!/bin/bash


org="${1}"
repo_name="${2}"
name="${3}"
product="${4}"
basearch="${5}"
releasever="${6}"

repo_status=$(hammer repository info --organization "${org}" --name "${repo_name}" --product "${product}" >&/dev/null; echo $?)
if [ ${repo_status} -eq 0 ]; then
    echo "Repository already exist" 
else 
    if [ ${#releasever} -eq 0 ]; then
        hammer repository-set enable --organization "${org}" --name "${name}" --product "${product}" --basearch "${basearch}" 
        if [ $? -eq 0 ]; then
            echo "Repository enabled"
        else    
            exit 1
        fi
    else
        hammer repository-set enable --organization "${org}" --name "${name}" --product "${product}" --basearch "${basearch}" --releasever "${releasever}"
        if [ $? -eq 0 ]; then
            echo "Repository enabled"
        else    
            exit 1
        fi
    fi
fi


