GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '{{ mysql_root_password }}';
FLUSH PRIVILEGES;
