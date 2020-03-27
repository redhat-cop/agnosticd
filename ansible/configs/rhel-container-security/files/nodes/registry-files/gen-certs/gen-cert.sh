#!/bin/bash
#
# Edit myserver.cnf and set the FQDN and ORGNAME variables to reflect your system then run this script.
#
touch myserver.key
chmod 600 myserver.key
openssl req -new -newkey rsa:4096 -nodes -sha256  -config myserver.cnf -keyout myserver.key -out myserver.csr
openssl x509 -signkey myserver.key -in myserver.csr -req -days 2000 -out myserver.cert
openssl x509 -noout -text -in myserver.cert | head -10
