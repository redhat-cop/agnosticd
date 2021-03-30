#!/bin/bash 
BASE_DIR=$(cd "$(dirname "$0")"; pwd)
CRFILE=${BASE_DIR}/custom-resource.yaml

DEFAULT_OPENSHIFT_PROJECT="workspaces"
HELP="

How to use this script to migrate from CRW 1.0 to 1.1:
-p=,    --project=            | project namespace to deploy CodeReady Workspaces, default: ${DEFAULT_OPENSHIFT_PROJECT}
-c=,    --custom-resource=    | path to custom-resource.yaml file, default: ${CRFILE}
-h,     --help                | show this help menu
"
if [[ $# -eq 0 ]] ; then
  echo -e "$HELP"
  exit 0
fi
for key in "$@"
do
  case $key in
    -p=*| --project=*)
      OPENSHIFT_PROJECT="${key#*=}"
      shift
      ;;
    -c=*| --custom-resource=*)
      CRFILE="${key#*=}"
      shift
      ;;
    -h | --help)
      echo -e "$HELP"
      exit 1
      ;;
    *)
      echo "Unknown argument passed: '$key'."
      echo -e "$HELP"
      exit 1
      ;;
  esac
done
export OPENSHIFT_PROJECT=${OPENSHIFT_PROJECT:-${DEFAULT_OPENSHIFT_PROJECT}}

if [[ ! -f ${CRFILE} ]]; then
	echo "
[ERROR] Could not find file ${CRFILE}. Please copy into this directory to proceed.
" && exit 1
fi


# check `oc status` for an error
status="$(oc status 2>&1)"
if [[ $status == *"Error"* ]]; then
	echo "$status" 
	echo "
[ERROR] You must log in to your cluster to use this script. For example,

 oc login --username developer --password developer

	" && exit 1
fi
# check `oc project` for a selected project
status="$(oc project 2>&1)"
if [[ $status == *"error"* ]]; then
	echo "$status" && exit 1
fi

POSTGRESQL_PASSWORD=$(oc get deployment postgres -o=jsonpath={'.spec.template.spec.containers[0].env[?(@.name=="POSTGRESQL_PASSWORD")].value'} -n=$OPENSHIFT_PROJECT)
SSO_ADMIN_USERNAME=$(oc get deployment keycloak -o=jsonpath={'.spec.template.spec.containers[0].env[?(@.name=="SSO_ADMIN_USERNAME")].value'} -n=$OPENSHIFT_PROJECT)
SSO_ADMIN_PASSWORD=$(oc get deployment keycloak -o=jsonpath={'.spec.template.spec.containers[0].env[?(@.name=="SSO_ADMIN_PASSWORD")].value'} -n=$OPENSHIFT_PROJECT)
SECRET=$(oc get oauthclient/openshift-identity-provider-h2fh -o=jsonpath={'.secret'})

if [[ ${SECRET} == "" ]]; then echo "
[WARNING] No secret found for oauthclient/openshift-identity-provider-h2fh !"; fi

# replace values in custom resource yaml
sed -i -e "s/chePostgresPassword: .\+/chePostgresPassword: '${POSTGRESQL_PASSWORD}'/g" \
	-e "s/keycloakAdminUserName: .\+/keycloakAdminUserName: '${SSO_ADMIN_USERNAME}'/g" \
	-e "s/keycloakAdminPassword: .\+/keycloakAdminPassword: '${SSO_ADMIN_PASSWORD}'/g" ${CRFILE}
sed -i "/ \+\(oAuthClientName\|oAuthSecret\): .\+/d" ${CRFILE}
sed -i "/auth:/a \      oAuthClientName: 'openshift-identity-provider-h2fh'\\n \     oAuthSecret: '${SECRET}'" ${CRFILE}

echo "
Successfully patched ${CRFILE} 

You can now run deploy.sh with arguments that suit your installation.
"
