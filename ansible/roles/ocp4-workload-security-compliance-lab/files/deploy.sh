#!/bin/bash
BASE_DIR=$(cd "$(dirname "$0")"; pwd)

DEFAULT_OPENSHIFT_PROJECT="workspaces"
DEFAULT_ENABLE_OPENSHIFT_OAUTH="false"
DEFAULT_TLS_SUPPORT="false"
DEFAULT_SELF_SIGNED_CERT="true"
DEFAULT_SERVER_IMAGE_NAME="registry.access.redhat.com/codeready-workspaces/server"
DEFAULT_SERVER_IMAGE_TAG="1.1"
DEFAULT_OPERATOR_IMAGE_NAME="registry.access.redhat.com/codeready-workspaces/server-operator:1.1"
DEFAULT_NAMESPACE_CLEANUP="false"

HELP="

How to use this script:
-d,     --deploy              | deploy using settings in custom-resource.yaml
-p=,    --project=            | project namespace to deploy CodeReady Workspaces, default: ${DEFAULT_OPENSHIFT_PROJECT}
-o, --oauth                   | enable Log into CodeReady Workspaces with OpenShift credentials, default: ${DEFAULT_ENABLE_OPENSHIFT_OAUTH}
-s,     --secure              | tls support, default: ${DEFAULT_TLS_SUPPORT}
--public-certs                | skip creating a secret with OpenShift router cert, default: false, which means operator will auto fetch router cert
--operator-image=             | operator image, default: ${DEFAULT_OPERATOR_IMAGE_NAME}
--server-image=               | server image, default: ${DEFAULT_SERVER_IMAGE_NAME}
-v=, --version=               | server image tag, default: ${DEFAULT_SERVER_IMAGE_TAG}
--verbose                     | stream deployment logs to console, default: false
-h,     --help                | show this help menu
"
if [[ $# -eq 0 ]] ; then
  echo -e "$HELP"
  exit 0
fi
for key in "$@"
do
  case $key in
    --verbose)
      FOLLOW_LOGS="true"
      shift
      ;;
    --public-certs)
      SELF_SIGNED_CERT="false"
      shift
      ;;
    -o| --oauth)
      ENABLE_OPENSHIFT_OAUTH="true"
      shift
      ;;
    -s| --secure)
      TLS_SUPPORT="true"
      shift
      ;;
    -p=*| --project=*)
      OPENSHIFT_PROJECT="${key#*=}"
      shift
      ;;
    --operator-image=*)
      OPERATOR_IMAGE_NAME=$(echo "${key#*=}")
      shift
      ;;
    --server-image=*)
      SERVER_IMAGE_NAME=$(echo "${key#*=}")
      shift
      ;;
    -v=*|--version=*)
      SERVER_IMAGE_TAG=$(echo "${key#*=}")
      shift
      ;;
    -d | --deploy)
      DEPLOY=true
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

export TERM=xterm

export TLS_SUPPORT=${TLS_SUPPORT:-${DEFAULT_TLS_SUPPORT}}

export SELF_SIGNED_CERT=${SELF_SIGNED_CERT:-${DEFAULT_SELF_SIGNED_CERT}}

export OPENSHIFT_PROJECT=${OPENSHIFT_PROJECT:-${DEFAULT_OPENSHIFT_PROJECT}}

export ENABLE_OPENSHIFT_OAUTH=${ENABLE_OPENSHIFT_OAUTH:-${DEFAULT_ENABLE_OPENSHIFT_OAUTH}}

export SERVER_IMAGE_NAME=${SERVER_IMAGE_NAME:-${DEFAULT_SERVER_IMAGE_NAME}}

export SERVER_IMAGE_TAG=${SERVER_IMAGE_TAG:-${DEFAULT_SERVER_IMAGE_TAG}}

export OPERATOR_IMAGE_NAME=${OPERATOR_IMAGE_NAME:-${DEFAULT_OPERATOR_IMAGE_NAME}}

DEFAULT_NO_NEW_NAMESPACE="false"
export NO_NEW_NAMESPACE=${NO_NEW_NAMESPACE:-${DEFAULT_NO_NEW_NAMESPACE}}

export NAMESPACE_CLEANUP=${NAMESPACE_CLEANUP:-${DEFAULT_NAMESPACE_CLEANUP}}

printInfo() {
  green=`tput setaf 2`
  reset=`tput sgr0`
  echo "${green}[INFO]: ${1} ${reset}"
}

printWarning() {
  yellow=`tput setaf 3`
  reset=`tput sgr0`
  echo "${yellow}[WARNING]: ${1} ${reset}"
}

printError() {
  red=`tput setaf 1`
  reset=`tput sgr0`
  echo "${red}[ERROR]: ${1} ${reset}"
}

preReqs() {
  printInfo "Welcome to CodeReady Workspaces Installer"
  if [ -x "$(command -v oc)" ]; then
    printInfo "Found oc client in PATH"
    export OC_BINARY="oc"
  elif [[ -f "/tmp/oc" ]]; then
    printInfo "Using oc client from a tmp location"
    export OC_BINARY="/tmp/oc"
  else
    printError "Command line tool ${OC_BINARY} (https://docs.openshift.org/latest/cli_reference/get_started_cli.html) not found. Download oc client and add it to your \$PATH."
    exit 1
  fi
}

# check if ${OC_BINARY} client has an active session
isLoggedIn() {
  printInfo "Checking if you are currently logged in..."
  ${OC_BINARY} whoami -t > /dev/null
  OUT=$?
  if [ ${OUT} -ne 0 ]; then
    printError "Log in to your OpenShift cluster: ${OC_BINARY} login --server=yourServer. Do not use system:admin login"
    exit 1
  else
    OC_TOKEN=$(${OC_BINARY} whoami -t)
    CONTEXT=$(${OC_BINARY} whoami -c)
    OPENSHIFT_API_URI=$(${OC_BINARY} whoami --show-server)
    printInfo "Active session found. Your current context is: ${CONTEXT}"
      ${OC_BINARY} get customresourcedefinitions > /dev/null 2>&1
      OUT=$?
      if [ ${OUT} -ne 0 ]; then
        printWarning "Creation of a CRD and RBAC rules requires cluster-admin privileges. Login in as user with cluster-admin role"
        printWarning "The installer will continue, however deployment is likely to fail"
    fi
  fi
}

createNewProject() {
  ${OC_BINARY} get namespace "${OPENSHIFT_PROJECT}" > /dev/null 2>&1
  OUT=$?
      if [ ${OUT} -ne 0 ]; then
           printWarning "Namespace '${OPENSHIFT_PROJECT}' not found, or current user does not have access to it. Installer will try to create namespace '${OPENSHIFT_PROJECT}'"
          printInfo "Creating namespace \"${OPENSHIFT_PROJECT}\""
          # sometimes even if the project does not exist creating a new one is impossible as it apparently exists
          sleep 1
          ${OC_BINARY} new-project "${OPENSHIFT_PROJECT}" > /dev/null
          OUT=$?
          if [ ${OUT} -eq 1 ]; then
            printError "Failed to create namespace ${OPENSHIFT_PROJECT}. It may exist in someone else's account or namespace deletion has not been fully completed. Try again in a short while or pick a different project name -p=myProject"
            exit ${OUT}
          else
            printInfo "Namespace \"${OPENSHIFT_PROJECT}\" successfully created"
          fi
      fi
}

createServiceAccount() {
  printInfo "Creating operator service account"
  ${OC_BINARY} get sa codeready-operator > /dev/null 2>&1
  OUT=$?
  if [ ${OUT} -ne 0 ]; then
    ${OC_BINARY} create sa codeready-operator -n=${OPENSHIFT_PROJECT} > /dev/null
  else
    printInfo "Service account already exists"
  fi
  printInfo "Create service account roles"
  ${OC_BINARY} apply -f - <<EOF  > /dev/null
  apiVersion: rbac.authorization.k8s.io/v1
  kind: Role
  metadata:
    name: codeready-operator
  rules:
    - apiGroups:
        - extensions/v1beta1
      resources:
        - ingresses
      verbs:
        - "*"
    - apiGroups:
        - route.openshift.io
      resources:
        - routes
      verbs:
        - "*"
    - apiGroups:
        - rbac.authorization.k8s.io
      resources:
        - roles
        - rolebindings
      verbs:
        - "*"
    - apiGroups:
        - rbac.authorization.k8s.io
      resources:
        - clusterroles
        - clusterrolebindings
      verbs:
        - "*"
    - apiGroups:
        - ""
      resources:
        - pods
        - services
        - serviceaccounts
        - endpoints
        - persistentvolumeclaims
        - events
        - configmaps
        - secrets
        - pods/exec
        - pods/log
      verbs:
        - '*'
    - apiGroups:
        - ""
      resources:
        - namespaces
      verbs:
        - get
    - apiGroups:
        - apps
      resources:
        - deployments
      verbs:
        - '*'
    - apiGroups:
        - monitoring.coreos.com
      resources:
        - servicemonitors
      verbs:
        - get
        - create
    - apiGroups:
        - org.eclipse.che
      resources:
        - '*'
      verbs:
        - '*'
EOF
OUT=$?
if [ ${OUT} -ne 0 ]; then
  printError "Failed to create role for operator service account"
  exit 1
fi
  ${OC_BINARY} get rolebinding codeready-operator > /dev/null 2>&1
  OUT=$?
  if [ ${OUT} -ne 0 ]; then
    printInfo "Creating Role Binding"
    ${OC_BINARY} create rolebinding codeready-operator --role=codeready-operator --serviceaccount=${OPENSHIFT_PROJECT}:codeready-operator -n=${OPENSHIFT_PROJECT} > /dev/null
  else
    printInfo "Role Binding already exists"
  fi

  if [ "${SELF_SIGNED_CERT}" == "true" ]; then
    printInfo "Self-signed certificate support enabled"
    printInfo "Adding extra privileges for an operator service account"
    ${OC_BINARY} get namespace openshift-ingress > /dev/null 2>&1
    OUT=$?
    if [ ${OUT} -ne 0 ]; then
      ROUTER_NAMESPACE="default"
    else
      ROUTER_NAMESPACE="openshift-ingress"
    fi
    printInfo "Creating secret-reader role and rolebinding in namespace ${ROUTER_NAMESPACE}"
    ${OC_BINARY} get role secret-reader -n=${ROUTER_NAMESPACE} > /dev/null 2>&1
    OUT=$?
    if [ ${OUT} -ne 0 ]; then
      ${OC_BINARY} create role secret-reader --resource=secrets --verb=get -n=${ROUTER_NAMESPACE} > /dev/null
      OUT=$?
      if [ ${OUT} -ne 0 ]; then
        printError "Failed to create secret reader role"
        exit 1
      fi
    else
      printInfo "Role secret-reader already exists"
    fi
    printInfo "Creating role binding to let operator get secrets in namespace ${ROUTER_NAMESPACE}"
    ${OC_BINARY} get rolebinding ${OPENSHIFT_PROJECT}-codeready-operator -n=${ROUTER_NAMESPACE} > /dev/null 2>&1
    OUT=$?
    if [ ${OUT} -ne 0 ]; then
      ${OC_BINARY} create rolebinding ${OPENSHIFT_PROJECT}-codeready-operator --role=secret-reader --serviceaccount=${OPENSHIFT_PROJECT}:codeready-operator -n=${ROUTER_NAMESPACE} > /dev/null
      OUT=$?
      if [ ${OUT} -ne 0 ]; then
        printWarning "Failed to create rolebinding for secret reader role"
        exit 1
      fi
    else
      printInfo "Role binding codeready-operator already exists in namespace ${ROUTER_NAMESPACE}"
    fi
  fi
  if [ "${ENABLE_OPENSHIFT_OAUTH}" == "true" ]; then
    printInfo "Creating cluster role to let operator service account create oAuthClients"
    ${OC_BINARY} get clusterrole codeready-operator > /dev/null 2>&1
    OUT=$?
    if [ ${OUT} -ne 0 ]; then
      ${OC_BINARY} create clusterrole codeready-operator --resource=oauthclients --verb=get,create,delete,update,list,watch > /dev/null
      OUT=$?
      if [ ${OUT} -ne 0 ]; then
        printError "Failed to create cluster role"
        exit 1
      fi
    else
      printInfo "Cluster role already exists"
    fi
    printInfo "Creating cluster role binding to let operator service account create oAuthClients"
    ${OC_BINARY} get clusterrolebinding ${OPENSHIFT_PROJECT}-codeready-operator > /dev/null 2>&1
    OUT=$?
    if [ ${OUT} -ne 0 ]; then
      ${OC_BINARY} create clusterrolebinding ${OPENSHIFT_PROJECT}-codeready-operator --clusterrole=codeready-operator --serviceaccount=${OPENSHIFT_PROJECT}:codeready-operator > /dev/null
      OUT=$?
      if [ ${OUT} -ne 0 ]; then
        printError "Failed to create cluster RoleBinding"
        exit 1
      fi
    else
      printInfo "Cluster role binding codeready-operator already exists"
    fi
  fi
}

checkCRD() {

  ${OC_BINARY} get customresourcedefinitions/checlusters.org.eclipse.che > /dev/null 2>&1
  OUT=$?
  if [ ${OUT} -ne 0 ]; then
    printInfo "Creating custom resource definition"
    createCRD > /dev/null
  else
    printInfo "Custom resource definition already exists"
  fi
}

createCRD() {
  printInfo "Creating custom resource definition"
  ${OC_BINARY} apply -f - <<EOF  > /dev/null
  apiVersion: apiextensions.k8s.io/v1beta1
  kind: CustomResourceDefinition
  metadata:
    name: checlusters.org.eclipse.che
  spec:
    group: org.eclipse.che
    names:
      kind: CheCluster
      listKind: CheClusterList
      plural: checlusters
      singular: checluster
    scope: Namespaced
    version: v1
    subresources:
      status: {}
EOF

OUT=$?
if [ ${OUT} -ne 0 ]; then
  printWarning "Failed to create custom resource definition. Current user does not have privileges to list and create CRDs"
  printWarning "Ask your cluster admin to register a CheCluster CRD:"
  cat <<EOF
  apiVersion: apiextensions.k8s.io/v1beta1
  kind: CustomResourceDefinition
  metadata:
    name: checlusters.org.eclipse.che
  spec:
    group: org.eclipse.che
    names:
      kind: CheCluster
      listKind: CheClusterList
      plural: checlusters
      singular: checluster
    scope: Namespaced
    version: v1
    subresources:
      status: {}
EOF
  # exit $OUT
fi
}


createOperatorDeployment() {

DEPLOYMENT=$(cat <<EOF
kind: Template
apiVersion: v1
metadata:
  name: codeready-operator
objects:
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: codeready-operator
  spec:
    replicas: 1
    selector:
      matchLabels:
        name: codeready-operator
    template:
      metadata:
        labels:
          name: codeready-operator
      spec:
        serviceAccountName: codeready-operator
        containers:
          - name: codeready-operator
            image: \${IMAGE}
            ports:
            - containerPort: 60000
              name: metrics
            command:
            - che-operator
            imagePullPolicy: IfNotPresent
            env:
              - name: WATCH_NAMESPACE
                valueFrom:
                  fieldRef:
                    fieldPath: metadata.namespace
              - name: POD_NAME
                valueFrom:
                  fieldRef:
                    fieldPath: metadata.name
              - name: OPERATOR_NAME
                value: "codeready-operator"
parameters:
- name: IMAGE
  displayName: Operator Image
  description: Operator Image
  required: true
EOF
  )

printInfo "Creating Operator Deployment"
${OC_BINARY} get deployments/codeready-operator -n=${OPENSHIFT_PROJECT} > /dev/null 2>&1
OUT=$?
if [ ${OUT} == 0 ]; then
  printInfo "Existing operator deployment found. It will be deleted"
  ${OC_BINARY} delete deployments/codeready-operator -n=${OPENSHIFT_PROJECT} --grace-period=1 > /dev/null
fi
echo "${DEPLOYMENT}" | ${OC_BINARY} new-app -p IMAGE=$OPERATOR_IMAGE_NAME -n="${OPENSHIFT_PROJECT}" -f - > /dev/null
OUT=$?
if [ ${OUT} -ne 0 ]; then
  printError "Failed to deploy CodeReady Operator"
  exit 1
else
  printInfo "Waiting for the Operator deployment to be scaled to 1"
  DESIRED_REPLICA_COUNT=1
  UNAVAILABLE=$(${OC_BINARY} get deployment/codeready-operator -n="${OPENSHIFT_PROJECT}" -o=jsonpath='{.status.unavailableReplicas}')
  DEPLOYMENT_TIMEOUT_SEC=300
  POLLING_INTERVAL_SEC=5
  end=$((SECONDS+DEPLOYMENT_TIMEOUT_SEC))
  while [ "${UNAVAILABLE}" == 1 ]; do
    UNAVAILABLE=$(${OC_BINARY} get deployment/codeready-operator -n="${OPENSHIFT_PROJECT}" -o=jsonpath='{.status.unavailableReplicas}')
    sleep 3
  done
  CURRENT_REPLICA_COUNT=$(${OC_BINARY} get deployment/codeready-operator -n="${OPENSHIFT_PROJECT}" -o=jsonpath='{.status.availableReplicas}')
  while [ "${CURRENT_REPLICA_COUNT}" -ne "${DESIRED_REPLICA_COUNT}" ] && [ ${SECONDS} -lt ${end} ]; do
    CURRENT_REPLICA_COUNT=$(${OC_BINARY} get deployment/codeready-operator -o=jsonpath='{.status.availableReplicas}')
    timeout_in=$((end-SECONDS))
    printInfo "Deployment is in progress...(Current replica count=${CURRENT_REPLICA_COUNT}, ${timeout_in} seconds remain)"
    sleep ${POLLING_INTERVAL_SEC}
  done

  if [ "${CURRENT_REPLICA_COUNT}" -ne "${DESIRED_REPLICA_COUNT}"  ]; then
    printError "CodeReady Operator deployment failed. Aborting. Run command 'oc logs deployment/codeready-operator' to get more details."
    exit 1
  elif [ ${SECONDS} -ge ${end} ]; then
    printError "Deployment timeout. Aborting."
    exit 1
  fi
  printInfo "Codeready Operator successfully deployed"
fi
}

createCustomResource() {
  printInfo "Creating Custom resource. This will initiate CodeReady Workspaces deployment"
  printInfo "CodeReady is going to be deployed with the following settings:"
  printInfo "TLS support:       ${TLS_SUPPORT}"
  printInfo "OpenShift oAuth:   ${ENABLE_OPENSHIFT_OAUTH}"
  printInfo "Self-signed certs: ${SELF_SIGNED_CERT}"
  ${OC_BINARY} get checlusters/codeready -n ${OPENSHIFT_PROJECT} > /dev/null 2>&1
  OUT=$?
  if [ ${OUT} == 0 ]; then
    printWarning "Custom resource codeready aleady exists. If you want the installer to create a CR, delete an existing one:"
    printWarning "${OC_BINARY} delete checlusters/codeready -n ${OPENSHIFT_PROJECT}"
  fi
  ${OC_BINARY} new-app -f ${BASE_DIR}/custom-resource.yaml \
               -p SERVER_IMAGE_NAME=${SERVER_IMAGE_NAME} \
               -p SERVER_IMAGE_TAG=${SERVER_IMAGE_TAG} \
               -p TLS_SUPPORT=${TLS_SUPPORT} \
               -p ENABLE_OPENSHIFT_OAUTH=${ENABLE_OPENSHIFT_OAUTH} \
               -p SELF_SIGNED_CERT=${SELF_SIGNED_CERT} \
               -n="${OPENSHIFT_PROJECT}" > /dev/null
  OUT=$?
  if [ ${OUT} -ne 0 ]; then
    printError "Failed to create Custom Resource. If it is already exists error, disregard it"
  fi
    DEPLOYMENT_TIMEOUT_SEC=1200
    printInfo "Waiting for CodeReady to boot. Timeout: ${DEPLOYMENT_TIMEOUT_SEC} seconds"
    if [ "${FOLLOW_LOGS}" == "true" ]; then
      printInfo "You may exit this script as soon as the log reports a successful CodeReady deployment"
      ${OC_BINARY} logs -f deployment/codeready-operator -n="${OPENSHIFT_PROJECT}"
    else
      DESIRED_STATE="Available"
      CURRENT_STATE=$(${OC_BINARY} get checluster/codeready -n="${OPENSHIFT_PROJECT}" -o=jsonpath='{.status.cheClusterRunning}')
      POLLING_INTERVAL_SEC=5
      end=$((SECONDS+DEPLOYMENT_TIMEOUT_SEC))
      while [ "${CURRENT_STATE}" != "${DESIRED_STATE}" ] && [ ${SECONDS} -lt ${end} ]; do
        CURRENT_STATE=$(${OC_BINARY} get checluster/codeready -n="${OPENSHIFT_PROJECT}" -o=jsonpath='{.status.cheClusterRunning}')
        timeout_in=$((end-SECONDS))
        sleep ${POLLING_INTERVAL_SEC}
      done

      if [ "${CURRENT_STATE}" != "${DESIRED_STATE}"  ]; then
        printError "CodeReady deployment failed. Aborting. Codeready operator logs: oc logs deployment/codeready-operator"
        exit 1
      elif [ ${SECONDS} -ge ${end} ]; then
        printError "Deployment timeout. Aborting. Codeready operator logs: oc logs deployment/codeready-operator"
        exit 1
      fi
      CODEREADY_ROUTE=$(${OC_BINARY} get checluster/codeready -o=jsonpath='{.status.cheURL}')
      printInfo "CodeReady Workspaces successfully deployed and is available at ${CODEREADY_ROUTE}"
  fi
}

if [ "${DEPLOY}" = true ] ; then
  preReqs
  isLoggedIn
  createNewProject
  createServiceAccount
  createCRD
  createOperatorDeployment
  createCustomResource
fi
