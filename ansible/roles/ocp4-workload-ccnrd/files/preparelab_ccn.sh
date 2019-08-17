#!/bin/bash
#
# Prereqs: a running ocp 4 cluster, logged in as kubeadmin
#
MYDIR="$( cd "$(dirname "$0")" ; pwd -P )"
function usage() {
    echo "usage: $(basename $0) [-c/--count usercount] -m/--module-type module_type"
}

#exec > logfile.txt

# Defaults
USERCOUNT=10
MODULE_TYPE=m1
REQUESTED_CPU=2
REQUESTED_MEMORY=4Gi
GOGS_PWD=r3dh4t1!

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -c|--count)
    USERCOUNT="$2"
    shift # past argument
    shift # past value
    ;;
    -m|--module-type)
    MODULE_TYPE="$2"
    shift # past argument
    shift # past value
    ;;
    *)    # unknown option
    echo "Unknown option: $key"
    usage
    exit 1
    ;;
esac
done

echo -e "Start with CCNRD Dev Track Environment Deployment... \n"
start_time=$SECONDS

set -- "${POSITIONAL[@]}" # restore positional parameters
echo -e "USERCOUNT: $USERCOUNT"
echo -e "MODULE_TYPE: $MODULE_TYPE\n"

if [ ! "$(oc get clusterrolebindings)" ] ; then
  echo "not cluster-admin"
  exit 1
fi

# Make the admin as cluster admin
oc adm policy add-cluster-role-to-user cluster-admin $(oc whoami)

# Add view role of default namespace to all userXX
for i in $(eval echo "{0..$USERCOUNT}") ; do
  oc adm policy add-role-to-user view user$i -n default
  echo -n .
  sleep 2
done

# create labs-infra project
oc new-project labs-infra

# adjust limits for admin
oc get userquota/default 
RESULT=$? 
if [ $RESULT -eq 0 ]; then
  oc delete userquota/default
else
  echo -e "userquota already is deleted...\n"
fi

oc delete limitrange --all -n labs-infra

# get routing suffix
TMP_PROJ="dummy-$RANDOM"
oc new-project $TMP_PROJ
oc create route edge dummy --service=dummy --port=8080 -n $TMP_PROJ
ROUTE=$(oc get route dummy -o=go-template --template='{{ .spec.host }}' -n $TMP_PROJ)
HOSTNAME_SUFFIX=$(echo $ROUTE | sed 's/^dummy-'${TMP_PROJ}'\.//g')
MASTER_URL=$(oc whoami --show-server)
CONSOLE_URL=$(oc whoami --show-console)

echo -e "HOSTNAME_SUFFIX: $HOSTNAME_SUFFIX \n"

oc project labs-infra

# create templates for labs
oc create -f $MYDIR/../files/template-binary.json -n openshift
oc create -f $MYDIR/../files/template-prod.json -n openshift
oc create -f $MYDIR/../files/ccn-sso72-template.json -n openshift

# deploy rhamt
if [ -z "${MODULE_TYPE##*m1*}" ] ; then
  oc process -f $MYDIR/../files/web-template-empty-dir-executor.json \
      -p WEB_CONSOLE_REQUESTED_CPU=$REQUESTED_CPU \
      -p WEB_CONSOLE_REQUESTED_MEMORY=$REQUESTED_MEMORY \
      -p EXECUTOR_REQUESTED_CPU=$REQUESTED_CPU \
      -p EXECUTOR_REQUESTED_MEMORY=2Gi | oc create -n labs-infra  -f -
fi

# deploy gogs
oc -n labs-infra new-app -f $MYDIR/../files/gogs-template.yaml \
      -p HOSTNAME=gogs-labs-infra.$HOSTNAME_SUFFIX \
      -p GOGS_VERSION=0.11.34 \
      -p SKIP_TLS_VERIFY=true \
      -p APPLICATION_NAME=gogs
# oc set resources dc/gogs --limits=cpu=400m,memory=512Mi --requests=cpu=100m,memory=128Mi

# Wait for gogs postgresql to be running
echo -e "Waiting for gogs postgresql to be running... \n"
while [ 1 ]; do
  STAT=$(curl -s -w '%{http_code}' -o /dev/null http://gogs-labs-infra.$HOSTNAME_SUFFIX)
  if [ "$STAT" = 200 ] ; then
    break
  fi
  echo -n .
  sleep 10
done

# Create gogs admin user
STAT=$(curl -s -w '%{http_code}' -o /dev/null -X POST http://gogs-labs-infra.$HOSTNAME_SUFFIX/user/sign_up \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "user_name=adminuser&password=adminpwd&&retype=adminpwd&&email=adminuser@gogs.com")
if [ "$STAT" = 302 ] || [ "$STAT" = 200 ] ; then
  echo "adminuser is created successfully..."
else
  echo "Failure to create adminuser with $STAT"
fi

# Create gogs users
echo -e "Creating $USERCOUNT gogs users.... \n"
for i in $(eval echo "{0..$USERCOUNT}") ; do
  STAT=$(curl -s -w '%{http_code}' -o /dev/null -X POST http://gogs-labs-infra.$HOSTNAME_SUFFIX/api/v1/admin/users \
        -H "Content-Type: application/json" \
        -d '{"login_name": "user'"$i"'", "username": "user'"$i"'", "email": "user'"$i"'@gogs.com", "password": "'"$GOGS_PWD"'"}' \
        -u adminuser:adminpwd)
  if [ "$STAT" = 200 ] || [ "$STAT" = 201 ] ; then
    echo "user$i is created successfully..."
  else
    echo "Failure to create user$i with $STAT"
  fi
done

# Create users' private repo
echo -e "Creating $USERCOUNT users' private repo...."
for MODULE in $(echo $MODULE_TYPE | sed "s/,/ /g") ; do
  MODULE_NO=$(echo $MODULE | cut -c 2)
  CLONE_ADDR=https://github.com/RedHat-Middleware-Workshops/cloud-native-workshop-v2m$MODULE_NO-labs.git
  REPO_NAME=cloud-native-workshop-v2m$MODULE_NO-labs
  for i in $(eval echo "{0..$USERCOUNT}") ; do
    USER_ID=$(($i + 2))
    STAT=$(curl -s -w '%{http_code}' -o /dev/null -X POST http://gogs-labs-infra.$HOSTNAME_SUFFIX/api/v1/repos/migrate \
        -H "Content-Type: application/json" \
        -d '{"clone_addr": "'"$CLONE_ADDR"'", "uid": '"$USER_ID"', "repo_name": "'"$REPO_NAME"'" }' \
        -u "user${i}:${GOGS_PWD}")
    if [ "$STAT" = 201 ] ; then
      echo "user$i $MODULE repo is created successfully..."
    else
      echo "Failure to create user$i $MODULE repo with $STAT"
    fi
  done
done

# Setup Istio Service Mesh
oc get project istio-operator 
RESULT=$? 
if [ $RESULT -eq 0 ]; then
  echo -e "istio-operator already exists..."
elif [ -z "${MODULE_TYPE##*m3*}" ] ; then
  echo -e "Installing istio-operator..."
  oc new-project istio-operator
  oc apply -n istio-operator -f $MYDIR/../files/servicemesh-operator.yaml
fi

oc get project istio-system 
RESULT=$? 
if [ $RESULT -eq 0 ]; then
  echo -e "istio-system already exists..."
elif [ -z "${MODULE_TYPE##*m3*}" ] ; then
  echo -e "Deploying the Istio Control Plane with Single-Tenant..."
  oc new-project istio-system
  oc create -n istio-system -f $MYDIR/../files/servicemeshcontrolplane.yaml
  # bash <(curl -L https://git.io/getLatestKialiOperator) --operator-image-version v1.0.0 --operator-watch-namespace '**' --accessible-namespaces '**' --operator-install-kiali false
  # oc apply -n istio-system -f https://raw.githubusercontent.com/kiali/kiali/v1.0.0/operator/deploy/kiali/kiali_cr.yaml
fi

# Create coolstore & bookinfo projects for each user
echo -e "Creating coolstore & bookinfo projects for each user... \n"
for i in $(eval echo "{0..$USERCOUNT}") ; do
  if [ -z "${MODULE_TYPE##*m1*}" ] || [ -z "${MODULE_TYPE##*m2*}" ] || [ -z "${MODULE_TYPE##*m3*}" ] ; then
    oc new-project user$i-inventory
    oc adm policy add-scc-to-user anyuid -z default -n user$i-inventory 
    oc adm policy add-scc-to-user privileged -z default -n user$i-inventory 
    oc adm policy add-role-to-user admin user$i -n user$i-inventory
    oc new-project user$i-catalog
    oc adm policy add-scc-to-user anyuid -z default -n user$i-catalog 
    oc adm policy add-scc-to-user privileged -z default -n user$i-catalog 
    oc adm policy add-role-to-user admin user$i -n user$i-catalog 
  fi
  if [ -z "${MODULE_TYPE##*m3*}" ] ; then
    oc new-project user$i-bookinfo 
    oc adm policy add-scc-to-user anyuid -z default -n user$i-bookinfo 
    oc adm policy add-scc-to-user privileged -z default -n user$i-bookinfo 
    oc adm policy add-role-to-user admin user$i -n user$i-bookinfo 
    oc adm policy add-role-to-user view user$i -n istio-system 
  fi
  if [ -z "${MODULE_TYPE##*m4*}" ] ; then
    oc new-project user$i-cloudnativeapps 
    oc adm policy add-role-to-user admin user$i -n user$i-cloudnativeapps 
  fi
done

# deploy guides
for MODULE in $(echo $MODULE_TYPE | sed "s/,/ /g") ; do
  MODULE_NO=$(echo $MODULE | cut -c 2)
  oc -n labs-infra new-app quay.io/osevg/workshopper --name=guides-$MODULE \
      -e MASTER_URL=$MASTER_URL \
      -e CONSOLE_URL=$CONSOLE_URL \
      -e ECLIPSE_CHE_URL=http://codeready-labs-infra.$HOSTNAME_SUFFIX \
      -e KEYCLOAK_URL=http://keycloak-labs-infra.$HOSTNAME_SUFFIX \
      -e GIT_URL=http://gogs-labs-infra.$HOSTNAME_SUFFIX \
      -e ROUTE_SUBDOMAIN=$HOSTNAME_SUFFIX \
      -e CONTENT_URL_PREFIX="https://raw.githubusercontent.com/RedHat-Middleware-Workshops/cloud-native-workshop-v2$MODULE-guides/master" \
      -e WORKSHOPS_URLS="https://raw.githubusercontent.com/RedHat-Middleware-Workshops/cloud-native-workshop-v2$MODULE-guides/master/_cloud-native-workshop-module$MODULE_NO.yml" \
      -e LOG_TO_STDOUT=true
  oc -n labs-infra expose svc/guides-$MODULE
done

# update Jenkins templates and create Jenkins project
if [ -z "${MODULE_TYPE##*m2*}" ] ; then
  oc replace -f $MYDIR/../files/jenkins-ephemeral.yml -n openshift
  oc get project jenkins
  RESULT=$? 
  if [ $RESULT -eq 0 ]; then
    echo -e "jenkins project already exists..."
  elif [ -z "${MODULE_TYPE##*m2*}" ] ; then
    echo -e "Creating Jenkins project..."
    oc new-project jenkins --display-name='Jenkins' --description='Jenkins CI Engine'
    oc new-app --template=jenkins-ephemeral -l app=jenkins -p JENKINS_SERVICE_NAME=jenkins -p DISABLE_ADMINISTRATIVE_MONITORS=true
    oc set resources dc/jenkins --limits=cpu=1,memory=2Gi --requests=cpu=1,memory=512Mi
  fi
fi

# Configure RHAMT Keycloak
if [ -z "${MODULE_TYPE##*m1*}" ] ; then
  echo -e "Getting access token to update RH-SSO theme \n"
  RESULT_TOKEN=$(curl -k -X POST https://secure-rhamt-web-console-labs-infra.$HOSTNAME_SUFFIX/auth/realms/master/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin" \
  -d 'password=password' \
  -d 'grant_type=password' \
  -d 'client_id=admin-cli' | jq -r '.access_token')

  echo -e "Updating a master realm with RH-SSO theme \n"
  RES=$(curl -s -w '%{http_code}' -o /dev/null  -k -X PUT https://secure-rhamt-web-console-labs-infra.$HOSTNAME_SUFFIX/auth/admin/realms/master/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $RESULT_TOKEN" \
  -d '{ "displayName": "rh-sso", "displayNameHtml": "<strong>Red Hat</strong><sup>®</sup> Single Sign On", "loginTheme": "rh-sso", "adminTheme": "rh-sso", "accountTheme": "rh-sso", "emailTheme": "rh-sso", "accessTokenLifespan": 6000 }')

  if [ "$RES" = 204 ] ; then
    echo -e "Updated a master realm with RH-SSO theme successfully...\n"
  else
    echo -e "Failure to update a master realm with RH-SSO theme with $RES\n"
  fi

  echo -e "Creating RH-SSO users as many as gogs users \n"
  for i in $(eval echo "{0..$USERCOUNT}") ; do
    RES=$(curl -s -w '%{http_code}' -o /dev/null  -k -X POST https://secure-rhamt-web-console-labs-infra.$HOSTNAME_SUFFIX/auth/admin/realms/rhamt/users \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $RESULT_TOKEN" \
    -d '{ "username": "user'"$i"'", "enabled": true, "disableableCredentialTypes": [ "password" ] }')
    if [ "$RES" = 200 ] || [ "$RES" = 201 ] || [ "$RES" = 409 ] ; then
      echo -e "Created RH-SSO user$i successfully...\n"
    else
      echo -e "Failure to create RH-SSO user$i with $RES\n"
    fi
  done

  echo -e "Retrieving RH-SSO user's ID list \n"
  USER_ID_LIST=$(curl -k -X GET https://secure-rhamt-web-console-labs-infra.$HOSTNAME_SUFFIX/auth/admin/realms/rhamt/users/ \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $RESULT_TOKEN")
  echo -e "USER_ID_LIST: $USER_ID_LIST \n"

  echo -e "Getting access token to reset passwords \n"
  export RESULT_TOKEN=$(curl -k -X POST https://secure-rhamt-web-console-labs-infra.$HOSTNAME_SUFFIX/auth/realms/master/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin" \
  -d 'password=password' \
  -d 'grant_type=password' \
  -d 'client_id=admin-cli' | jq -r '.access_token')
  echo -e "RESULT_TOKEN: $RESULT_TOKEN \n"

  echo -e "Reset passwords for each RH-SSO user \n"
  for i in $(jq '. | keys | .[]' <<< "$USER_ID_LIST"); do
    USER_ID=$(jq -r ".[$i].id" <<< "$USER_ID_LIST")
    USER_NAME=$(jq -r ".[$i].username" <<< "$USER_ID_LIST")
    if [ "$USER_NAME" != "rhamt" ] ; then 
      RES=$(curl -s -w '%{http_code}' -o /dev/null -k -X PUT https://secure-rhamt-web-console-labs-infra.$HOSTNAME_SUFFIX/auth/admin/realms/rhamt/users/$USER_ID/reset-password \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -H "Authorization: Bearer $RESULT_TOKEN" \
        -d '{ "type": "password", "value": "'"$GOGS_PWD"'", "temporary": true}')
      if [ "$RES" = 204 ] ; then
        echo -e "user$i password is reset successfully...\n"
      else
        echo -e "Failure to reset user$i password with $RES\n"
      fi
    fi
  done
fi

oc delete project $TMP_PROJ

# Install Che
echo -e "Installing CodeReady Workspace...\n"
cat <<EOF | oc apply -n openshift-marketplace -f -
apiVersion: operators.coreos.com/v1
kind: CatalogSourceConfig
metadata:
  finalizers:
  - finalizer.catalogsourceconfigs.operators.coreos.com
  name: installed-redhat-che
  namespace: openshift-marketplace
spec:
  targetNamespace: labs-infra
  packages: codeready-workspaces
  csDisplayName: Red Hat Operators
  csPublisher: Red Hat
EOF

cat <<EOF | oc apply -n labs-infra -f -
apiVersion: operators.coreos.com/v1alpha2
kind: OperatorGroup
metadata:
  name: che-operator-group
  namespace: labs-infra
  generateName: che-
  annotations:
    olm.providedAPIs: CheCluster.v1.org.eclipse.che
spec:
  targetNamespaces:
  - labs-infra
EOF

cat <<EOF | oc apply -n labs-infra -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: codeready-workspaces
  namespace: labs-infra
  labels:
    csc-owner-name: installed-redhat-che
    csc-owner-namespace: openshift-marketplace
spec:
  channel: final
  installPlanApproval: Automatic
  name: codeready-workspaces
  source: installed-redhat-che
  sourceNamespace: labs-infra
  startingCSV: crwoperator.v1.2.0
EOF

# Wait for checluster to be a thing
echo "Waiting for CheCluster CRDs"
while [ true ] ; do
  if [ "$(oc explain checluster)" ] ; then
    break
  fi
  echo -n .
  sleep 10
done

cat <<EOF | oc apply -n labs-infra -f -
apiVersion: org.eclipse.che/v1
kind: CheCluster
metadata:
  name: codeready
  namespace: labs-infra
spec:
  server:
    cheFlavor: codeready
    tlsSupport: false
    selfSignedCert: false
    serverMemoryRequest: '2Gi'
    serverMemoryLimit: '6Gi'
  database:
    externalDb: false
    chePostgresHostName: ''
    chePostgresPort: ''
    chePostgresUser: ''
    chePostgresPassword: ''
    chePostgresDb: ''
  auth:
    openShiftoAuth: false
    externalKeycloak: false
    keycloakURL: ''
    keycloakRealm: ''
    keycloakClientId: ''
  storage:
    pvcStrategy: per-workspace
    pvcClaimSize: 1Gi
    preCreateSubPaths: true
EOF

# Wait for che to be up
echo "Waiting for Che to come up..."
while [ 1 ]; do
  STAT=$(curl -s -w '%{http_code}' -o /dev/null http://codeready-labs-infra.$HOSTNAME_SUFFIX/dashboard/)
  if [ "$STAT" = 200 ] ; then
    break
  fi
  echo -n .
  sleep 10
done

# workaround for PVC problem
oc get --export cm/custom -n labs-infra -o yaml | yq w - 'data.CHE_INFRA_KUBERNETES_PVC_WAIT__BOUND' \"false\" | oc apply -f - -n labs-infra
oc scale -n labs-infra deployment/codeready --replicas=0
oc scale -n labs-infra deployment/codeready --replicas=1

# Wait for che to be back up
echo "Waiting for Che to come back up..."
while [ 1 ]; do
  STAT=$(curl -s -w '%{http_code}' -o /dev/null http://codeready-labs-infra.$HOSTNAME_SUFFIX/dashboard/)
  if [ "$STAT" = 200 ] ; then
    break
  fi
  echo -n .
  sleep 10
done

# get keycloak admin password
KEYCLOAK_USER="$(oc set env deployment/keycloak --list -n labs-infra|grep SSO_ADMIN_USERNAME | cut -d= -f2)"
KEYCLOAK_PASSWORD="$(oc set env deployment/keycloak --list -n labs-infra|grep SSO_ADMIN_PASSWORD | cut -d= -f2)"
SSO_TOKEN=$(curl -s -d "username=${KEYCLOAK_USER}&password=${KEYCLOAK_PASSWORD}&grant_type=password&client_id=admin-cli" \
  -X POST http://keycloak-labs-infra.$HOSTNAME_SUFFIX/auth/realms/master/protocol/openid-connect/token | \
  jq  -r '.access_token')

# Import realm 
curl -v -H "Authorization: Bearer ${SSO_TOKEN}" -H "Content-Type:application/json" -d @../files/ccnrd-realm.json \
  -X POST "http://keycloak-labs-infra.$HOSTNAME_SUFFIX/auth/admin/realms"

## MANUALLY add ProtocolMapper to map User Roles to "groups" prefix for JWT claims
echo "Keycloak credentials: $KEYCLOAK_USER / $KEYCLOAK_PASSWORD"
echo "URL: http://keycloak-labs-infra.${HOTSNAME_SUFFIX}"

# import stack image
oc create -n openshift -f $MYDIR/../files/stack.imagestream.yaml
oc import-image --all quarkus-stack -n openshift

# Import stack definition
SSO_CHE_TOKEN=$(curl -s -d "username=admin&password=admin&grant_type=password&client_id=admin-cli" \
  -X POST http://keycloak-labs-infra.$HOSTNAME_SUFFIX/auth/realms/codeready/protocol/openid-connect/token | \
  jq  -r '.access_token')

STACK_RESULT=$(curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' \
    --header "Authorization: Bearer ${SSO_CHE_TOKEN}" -d @files/stack-ccn.json \
    "http://codeready-labs-infra.$HOSTNAME_SUFFIX/api/stack")

STACK_ID=$(echo $STACK_RESULT | jq -r '.id')

# Give all users access to the stack
echo -e "Giving all users access to the stack...\n"
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' \
    --header "Authorization: Bearer ${SSO_CHE_TOKEN}" -d '{"userId": "*", "domainId": "stack", "instanceId": "'"$STACK_ID"'", "actions": [ "read", "search" ]}' \
    "http://codeready-labs-infra.$HOSTNAME_SUFFIX/api/permissions"

# Scale the cluster
WORKERCOUNT=$(oc get nodes|grep worker | wc -l)
if [ "$WORKERCOUNT" -lt 10 ] ; then
    for i in $(oc get machinesets -n openshift-machine-api -o name | grep worker| cut -d'/' -f 2) ; do
      echo "Scaling $i to 3 replicas"
      oc patch -n openshift-machine-api machineset/$i -p '{"spec":{"replicas": 3}}' --type=merge
    done
fi

end_time=$SECONDS
elapsed_time_sec=$(( end_time - start_time ))
elapsed_time_min=$(printf '%dh:%dm:%ds\n' $(($elapsed_time_sec/3600)) $(($elapsed_time_sec%3600/60)) $(($elapsed_time_sec%60)))
echo "Total of $elapsed_time_min seconds elapsed for CCNRD Dev Track Environment Deployment"
