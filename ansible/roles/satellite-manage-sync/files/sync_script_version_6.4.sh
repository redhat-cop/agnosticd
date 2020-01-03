#!/bin/bash

function repo_sync() {
  # check if repository exist
  hammer --output cve repository list  --organization "${1}" --name  "${2}" | grep Name
  exit_status=$?
  if [ ${exit_status} -ne 0 ]
    then
      echo "Repository or product not exist"
      return 
  elif [ ${exit_status} -eq 0 ]
    then
      repo_status=$(hammer repository info  --organization "${1}" --name  "${2}"  --product "${3}" | grep Status: | awk -F':' '{print $2}' | sed  's/^ //')
      echo $repo_status
      if [ "${repo_status}"  == 'Not Synced' ]
        then
          sync_task_id=$(hammer repository synchronize  --organization "${1}" --name "${2}"  --product "${3}" --async)
          echo "${sync_task_id}"
      else
          echo "Already synced or in-process"
      fi
  fi
}

if [ "$#" -eq 3 ]
  then
    repo_sync "${1}" "${2}" "${3}"

elif [ "$#" -gt 3 ]
  then
    echo -e "More than three arguments provided,  Three arguments required:\n Organizzation Name Product" >&2
else
    echo -e "Argument missing, Three arguments required:\n Organizzation Name Product" >&2
fi