#!/bin/bash
echo { }
exit 0 
# This script is a wrapper for ec2.py. The purpose is to avoid HTTP 400 from AWS as we run several
# deployments simultaneously.
# It follows the recommandations from: http://docs.aws.amazon.com/general/latest/gr/api-retries.html

# There must be a way to configure boto and num_retries in some profile to avoid using a wrapper
# if someone knows where to set it, please, let us know!

# pseudo-code:
#
#DO
# wait for (2^retries * 100) milliseconds
# status = Get the result of the asynchronous operation.
#
#IF status = SUCCESS
#retry = false
#ELSE IF status = NOT_READY
#retry = true
#ELSE IF status = THROTTLED
#retry = true
#ELSE
#Some other error occurred, so stop calling the API.
#retry = false
#END IF
#
#retries = retries + 1
#
#WHILE (retry AND (retries < MAX_RETRIES))

# 10 * 90-150s ~ 20 minutes max
MAX_RETRIES=10
MAX_DELAY=$(( 90 + RANDOM % 60))
retries=0

ORIG=$(cd $(dirname $0); pwd)

output=$(mktemp)
errlog=$(mktemp)

while [ $retries -le $MAX_RETRIES ]; do
    duration=$(bc <<< "2^${retries} * 0.${RANDOM}")
    if [ $(bc <<< "$duration > $MAX_DELAY") -eq 1 ]; then
        duration=$MAX_DELAY
    fi

    sleep $duration

    $ORIG/ec2.py "$@" > $output 2>$errlog
    RET=$?
    if [ "$RET" = "0" ]; then
        cat $output
        cat $errlog >&2
        rm $output
        rm $errlog
        exit 0
    fi
    retries=$((retries + 1))
done

cat $output
cat $errlog >&2
rm $output
rm $errlog
exit 2
