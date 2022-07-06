#!/bin/bash 

prometheus_server=$PROM_SERVER
i=0 
r_dir=/tmp/results

rm -rf $r_dir/*.json

mkdir -p $r_dir
mkdir -p /var/lib/etcd/fio

send_metrics () {
  count=$1
  out_file=$r_dir/job-$count.json
  value=$(cat $out_file | jq '.jobs[].sync.lat_ns.percentile["99.000000"]')
  echo "Sending FIO # $i value: $value"
cat <<EOF | curl --data-binary @- http://$prometheus_server/metrics/job/fio/instance/$HOSTNAME
# TYPE fio_latency counter
fio_latency $value
# TYPE fio_current_run counter
fio_current_run $count
EOF

}

while true
do 

  out_file=$r_dir/job-$i.json
  rm -f $out_file

  echo "Running FIO # $i"
  fio --rw=write --ioengine=sync --fdatasync=1 --directory=/var/lib/etcd/fio --size=22m --bs=2300 --name=mytest --output-format=json+ >> $out_file

  send_metrics $i
  i=$((i+1))
 
done

# for i in {1..{{ $test_runs | default(30) }}}
# do 
#   out_file=$r_dir/job-$i.json
#   rm -f $out_file

#   echo "Running FIO # $i"
#   fio --rw=write --ioengine=sync --fdatasync=1 --directory=/var/lib/etcd/fio --size=22m --bs=2300 --name=mytest --output-format=json+ >> $out_file

#   send_metrics $i

# done
