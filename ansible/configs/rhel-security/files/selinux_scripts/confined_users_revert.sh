#!/bin/bash

# restore the detault SELinux Users mapping
semanage login -d -s sysadm_u -r 's0-s0:c0.c1023' admin1 &> /dev/null
semanage login -d -s staff_u -r 's0-s0:c0.c1023' admin2 &> /dev/null
semanage login -m -s unconfined_u -r s0 __default__ &> /dev/null
semanage user -m -R "sysadm_r" sysadm_u &> /dev/null

# restore the default boolean setting
setsebool -P ssh_sysadm_login off

# remove lab users
userdel -r admin1 &> /dev/null
userdel -r admin2 &> /dev/null
userdel -r user42 &> /dev/null
rm -rf -f /etc/sudoers.d/administrators &> /dev/null
