#!/usr/bin/env sh

set -u

retries=10
delay=20

for i in $(seq ${retries}); do
    ansible-galaxy role install \
       -r /tmp/requirements.yml \
       --roles-path "/usr/share/ansible/roles" \
       && rc=0 && break
    rc=$?
    sleep $delay
done

[ "${rc}" != 0 ] && exit $rc


for i in $(seq ${retries}); do
    ansible-galaxy collection install -vv \
        -r /tmp/requirements.yml \
        --collections-path "/usr/share/ansible/collections" \
       && rc=0 && break
    rc=$?
    sleep $delay
done

[ "${rc}" != 0 ] && exit $rc

for col in \
    azure/azcollection/requirements-azure.txt \
    community/vmware/requirements.txt \
    google/cloud/requirements.txt \
    kubernetes/core/requirements.txt; do

    for i in $(seq ${retries}); do
        pip install --no-cache-dir -r /usr/share/ansible/collections/ansible_collections/${col} \
            && rc=0 && break
        rc=$?
        sleep $delay
    done
    [ "${rc}" != 0 ] && exit $rc
done

exit 0
