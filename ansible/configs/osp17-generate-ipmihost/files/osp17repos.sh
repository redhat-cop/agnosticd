#!/bin/sh -e
yum install -y httpd
systemctl enable --now httpd
for repo in rhel-9-for-x86_64-baseos-eus-rpms rhel-9-for-x86_64-appstream-eus-rpms rhel-9-for-x86_64-highavailability-eus-rpms openstack-17-for-rhel-9-x86_64-rpms fast-datapath-for-rhel-9-x86_64-rpms rhceph-5-tools-for-rhel-9-x86_64-rpms; do
/bin/reposync -p /var/www/html/repos/ --download-metadata --repo=$repo
done
restorecon -R -v /var/www/html/repos/
sync
df -hT > /root/df2.txt

