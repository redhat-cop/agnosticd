#!/bin/bash

set -xue -o pipefail

: "${credentials:?"credentials not defined"}"
[ -n "${1}" ]
[ -n "${2}" ]
username=$(echo "$credentials" | cut -d: -f1)
export username
password=$(echo "$credentials" | cut -d: -f2)
export password

openshift_location="${1}"
export openshift_location
guid="${2}"
export guid

config=${guid}.config
OC="oc --config $config --insecure-skip-tls-verify=true"
FINALRC=0
TIMEOUT=300

assert_OK() {
  RET=$?
  if [ $RET != 0 ]; then
    echo "assert_OK failed: $RET"
    FINALRC=$RET
  fi
}

assert_FAIL() {
  RET=$?
  if [ $RET = 0 ]; then
    echo "assert_FAIL failed: $RET"
    FINALRC=2
  fi
}

$OC login ${openshift_location} --username="${username}" --password="${password}"

projects=$($OC get projects -o json|jq -r '.items[].metadata.name'|grep ${guid})


set +xe

# Wait until DC are done
for j in $(seq 4); do
  sleep 1
  for p in $projects; do
      deploymentconfigs=$($OC get dc -n "${p}" -o json|jq -r '.items[].metadata.name')

      for dc in $deploymentconfigs; do
          timeout $TIMEOUT $OC rollout status dc/${dc} -w -n "${p}"
      done
  done
done

for p in $projects; do
  echo "######################### Project $p"

  # if there are no pods in this project (exclude pods from jobs), continue
  if [ "$($OC get pods -n "$p" --no-headers 2>/dev/null|grep -v -x -f <($OC get pod -n "$p" --no-headers -l job-name)|wc -l)" -eq 0 ]; then
  	continue
  fi
  # Print all pod Running or Completed   (there should be at least one)
  $OC get pods -n "$p" --no-headers\
  |awk 'BEGIN{z=1} $3 == "Running" || $3 == "Completed" {print; z=0} END{exit z}'
  assert_OK

  # Print all pods not Running and not Completed  (there should be none), exclude pods from jobs
  $OC get pods -n "$p" --no-headers \
  |grep -v -x -f <($OC get pods -n "${p}" --no-headers -l job-name)\
  |awk 'BEGIN{z=1} $3 != "Running" && $3 != "Completed" {print; z=0} END{exit z}'

  assert_FAIL
done

if [ $FINALRC != 0 ]; then
	echo
	echo DIAGNOSTICS
	echo
	for p in $projects; do
        echo
        echo "######################### Project $p"
        echo
		$OC get pvc -n "$p"
        pods=$($OC get pods -n "$p" --no-headers|grep -v -x -f <($OC get pod -n "$p" --no-headers -l job-name)|awk '$3 != "Running" && $3 != "Completed" {print $1}')

        for pod in $pods; do
        	$OC describe pod $pod -n "$p"
            $OC logs $pod -n "$p"
        done
	done
fi

exit $FINALRC
