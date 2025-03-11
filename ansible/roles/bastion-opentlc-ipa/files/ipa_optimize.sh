#!/bin/bash -xe
LOG=/tmp/ipa_optimize.log
sed -i "2i ldap_group_nesting_level=0" /etc/sssd/sssd.conf 1>> ${LOG} 2>> ${LOG}
sed -i "3i entry_cache_timeout=1" /etc/sssd/sssd.conf 1>> ${LOG} 2>> ${LOG}
systemctl restart sssd 1>> ${LOG} 2>> ${LOG}
echo "PermitRootLogin without-password" >> /etc/ssh/sshd_config
sed -i "s/^PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config 1>> ${LOG} 2>> ${LOG}
sed -i "s/^ChallengeResponseAuthentication yes/ChallengeResponseAuthentication no/" /etc/ssh/sshd_config 1>> ${LOG} 2>> ${LOG}
systemctl restart sshd 1>> ${LOG} 2>> ${LOG}
