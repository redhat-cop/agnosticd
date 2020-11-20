#!/bin/bash
exec 1>cyberark_setup/mysqldb_deploy.log 2>&1

cd cyberark_setup

export CYBERARK_NAMESPACE_NAME=$1

source dap_service_rhpds.config

main() {
  deploy_mysql_db
}

########################
deploy_mysql_db() {
  oc adm policy add-scc-to-user anyuid -z mysql-db -n $CYBERARK_NAMESPACE_NAME
  cat ./templates/mysql.template                    		\
  | sed "s#{{ MYSQL_IMAGE_NAME }}#$REGISTRY_MYSQL_IMAGE#g"		\
  | sed "s#{{ CYBERARK_NAMESPACE_NAME }}#$CYBERARK_NAMESPACE_NAME#g"	\
  | sed "s#{{ MYSQL_USERNAME }}#$MYSQL_USERNAME#g"              	\
  | sed "s#{{ MYSQL_PASSWORD }}#$MYSQL_PASSWORD#g"              	\
  > ./mysql.yaml
  oc apply -f ./mysql.yaml -n $CYBERARK_NAMESPACE_NAME
}

main "$@"