subscription-manager release  --set=8.4
yum install -y httpd

systemctl enable --now httpd

echo "Hello from OpenStack" > /var/www/html/index.html
