#!/bin/sh

echo "Installing jq and fio"
dnf install -y jq fio

echo "creating fio directory"
mkdir /var/lib/etcd/fio

echo "running tests"
for i in {1..50};do echo "running test $i";fio --rw=write --ioengine=sync --fdatasync=1 --directory=/var/lib/etcd/fio --size=22m --bs=2300 --name=mytest --output-format=json+ | jq '.jobs[].sync.lat_ns.percentile."99.000000"' >> $(cat /etc/hostname)-fio.out;done

echo "uploading to s3"
/host/root/upload.sh '' '' nstephan-test ./ $(cat /etc/hostname)-fio.out