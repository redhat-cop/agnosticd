# Customizations to ama-tomcat vm image

The tomcat vm for this demo is based on the one used in the ama_demo_shared.

The following steps are to be run on top of the ama_demo_shared vm.

scp -r /coolstore-portfolio/coolstore-legacy/coolstore-legacy-0.0.1-SNAPSHOT.tar.gz lab-user@{vm-ip-address}:/tmp/

ssh lab-user@{vm-ip-address}

sudo rm /etc/NetworkManager/conf.d/99-cloud-init.conf

sudo systemctl stop tomcat

sudo rm -rf /usr/local/tomcat/webapps/customers-tomcat-0.0.1-SNAPSHOT*
sudo rm -rf /usr/local/tomcat/webapps/ROOT/*

tar -xvzf coolstore-legacy-0.0.1-SNAPSHOT.tar.gz

sudo cp -rf /tmp/coolstore-legacy-0.0.1-SNAPSHOT/* /usr/local/tomcat/webapps/ROOT/

sudo chown -R tomcat:tomcat /usr/local/tomcat/webapps/ROOT/*

sudo rm -rf /usr/local/tomcat/logs/*

sudo systemctl start tomcat

curl -i http://localhost:8080/health/live
curl -i http://localhost:8080/health/ready

sudo systemctl stop tomcat

sudo vim /opt/config/persistence.properties
```
  jdbc.driverClassName=oracle.jdbc.driver.OracleDriver
  jdbc.url=jdbc:oracle:thin:@//oracle:1521/XEPDB1
  jdbc.user=customer
  jdbc.password=redhat
  hibernate.hbm2ddl.auto=create-drop
  hibernate.dialect=org.hibernate.dialect.Oracle10gDialect
````

### In rhvm:

1. vm shutdown
2. disk copy (appmod-tomcat-qcow2)
3. disk download

### Upload image to S3

aws s3 cp /appmod-tomcat-qcow2.qcow2 s3://gpte-public/appmod_demo/appmod-tomcat.qcow2
