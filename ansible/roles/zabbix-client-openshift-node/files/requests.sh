#!/bin/bash
set -euo pipefail

# example usage
# ./requests.sh memory
# ./requests.sh cpu

# args:
# - cpu|memory
#
# output:
# returns the % request/node_capacity, (also visible in `oc describe node`)
WHAT=$1

# load configuration (TOKEN and HAWKULAR host)
. /etc/zabbix/requests.rc


CURLOPT=(-s -k -H "Authorization: Bearer ${TOKEN}" -H 'Hawkular-Tenant: _system' -X GET)

URL="https://${HAWKULAR}/hawkular/metrics/gauges/data?tags=group_id:/${WHAT}/request,hostname:$(hostname)&bucketDuration=1h&limit=1"

request=$(curl "${CURLOPT[@]}" "$URL" | python -m json.tool|grep avg|head -1|sed 's/^ *"avg *"://;s/,$//')

URL="https://${HAWKULAR}/hawkular/metrics/gauges/data?tags=group_id:/${WHAT}/node_capacity,hostname:$(hostname)&bucketDuration=1h&limit=1"

capacity=$(curl "${CURLOPT[@]}" "$URL" | python -m json.tool|grep avg|head -1|sed 's/^ *"avg *"://;s/,$//')

bc <<< "scale=2; 100*${request}/${capacity}"
