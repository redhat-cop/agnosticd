#!/bin/sh

# This is only needed if we are using the fedora image instead of custom
# echo "Installing jq and fio"
# dnf install -y jq fio nmap-nca

echo "running tests"

mkdir -p /var/lib/etcd/fio
# GUID=$(echo $HOSTNAME |cut -d \- -f 1)
for i in $(seq $test_runs)
do
  echo "running test $i"
  result=$(fio --rw=write --ioengine=sync --fdatasync=1 --directory=/var/lib/etcd/fio --size=22m --bs=2300 --name=mytest --output-format=json+ | jq '.jobs[].sync.lat_ns.percentile."99.000000"')
  echo $result
  echo "fio.$GUID.latency $result `date +%s`" | nc overwatch.osp.opentlc.com 2003
  echo $result >> /host/home/core/$GUID.out
done