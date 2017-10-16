#!/bin/bash -xe

sed -i "2i ldap_group_nesting_level=0" /etc/sssd/sssd.conf
systemctl restart sssd
echo "PermitRootLogin without-password" >> /etc/ssh/sshd_config
sed -i "s/^PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config
sed -i "s/^ChallengeResponseAuthentication yes/ChallengeResponseAuthentication no/" /etc/ssh/sshd_config
systemctl restart sshd
