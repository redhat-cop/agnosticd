#!/bin/bash

# Wait until IP Address is set
IP_ADDRESS=""

until [ ${IP_ADDRESS} != "" ]
do
  sleep 1
  IP_ADDRESS=$(ip -4 route get 8.8.8.8 | awk {'print $7'} | tr -d '\n')

  # or
  # IP_ADDRESS=$(curl ifconfig.io)
  # or
  # IP_ADDRESS=$(/sbin/ip -o -4 addr list eth0 | awk '{print $4}' | cut -d/ -f1)
done

echo "IP Address: ${IP_ADDRESS}"

# in /opt/oracle/homes/OraDBHome21cXE/network/admin/listener.ora
#Replace
#      (ADDRESS = (PROTOCOL = TCP)(HOST = dc.e1.3ca9.ip4.static.sl-reverse.com)(PORT = 1521))
#with
#      (ADDRESS = (PROTOCOL = TCP)(HOST = ${IP_ADDRESS})(PORT = 1521))

cp /opt/oracle/homes/OraDBHome21cXE/network/admin/listener.ora /opt/oracle/homes/OraDBHome21cXE/network/admin/listener.ora.$(date +"%Y-%m-%d-%H-%M-%S")

sed -i "s/      (ADDRESS = (PROTOCOL = TCP)(HOST.*/      (ADDRESS = (PROTOCOL = TCP)(HOST = ${IP_ADDRESS})(PORT = 1521))/" /opt/oracle/homes/OraDBHome21cXE/network/admin/listener.ora

# in /opt/oracle/homes/OraDBHome21cXE/network/admin/tnsnames.ora
# Set Host to IP twice

cp /opt/oracle/homes/OraDBHome21cXE/network/admin/tnsnames.ora /opt/oracle/homes/OraDBHome21cXE/network/admin/tnsnames.ora.$(date +"%Y-%m-%d-%H-%M-%S")
sed -i "s/    (ADDRESS = (PROTOCOL = TCP)(HOST.*/    (ADDRESS = (PROTOCOL = TCP)(HOST = ${IP_ADDRESS})(PORT = 1521))/" /opt/oracle/homes/OraDBHome21cXE/network/admin/tnsnames.ora
sed -i "s/  (ADDRESS = (PROTOCOL = TCP)(HOST.*)(PORT = 1521))/  (ADDRESS = (PROTOCOL = TCP)(HOST = ${IP_ADDRESS})(PORT = 1521))/" /opt/oracle/homes/OraDBHome21cXE/network/admin/tnsnames.ora

# Sleep for 10 minutes for SystemD to be happy
# Skip by passing any parameter to the script
if [ "$#" -eq "0" ]
then
  z=0
  for i in {1..10}; do
      sleep 1m
      ((z++))
  done
fi

exit 0
