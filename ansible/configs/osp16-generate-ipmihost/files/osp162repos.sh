#subscription-manager attach --pool=8a85f98260c27fc50160c323247e39e0
yum install -y httpd
systemctl enable --now httpd
for repo in rhel-8-for-x86_64-baseos-eus-rpms rhel-8-for-x86_64-appstream-eus-rpms rhel-8-for-x86_64-highavailability-eus-rpms ansible-2.9-for-rhel-8-x86_64-rpms openstack-16.2-for-rhel-8-x86_64-rpms fast-datapath-for-rhel-8-x86_64-rpms rhel-9.2-for-x86_64-baseos-eus-rpms rhel-9.2-for-x86_64-appstream-eus-rpms rhel-9.2-for-x86_64-highavailability-eus-rpms openstack-beta-for-rhel-9-x86_64-rpms fast-datapath-for-rhel-9-x86_64-rpms; do
/bin/reposync -p /var/www/html/repos/ --download-metadata --repo=$repo
done
restorecon -R -v /var/www/html/repos/
