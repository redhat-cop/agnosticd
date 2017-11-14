#!/bin/bash

/usr/bin/sss_ssh_authorizedkeys jenkins-sfo01
if [ $? = 0 ]; then exit 0; fi

systemctl restart sssd
exit 1
