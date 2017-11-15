#!/bin/bash
systemctl restart sssd
sleep 10

for i in $(seq 20); do
    /usr/bin/sss_ssh_authorizedkeys jenkins-sfo01
    RET=$?
    if [ $RET = 0 ]; then exit 0; fi

    systemctl restart sssd
    sleep 10
done

exit 2
