#!/bin/bash
BASE_DIR=$(cd "$(dirname "$0")"; pwd)

DEFAULT_OPENSHIFT_PROJECT="workspaces"
DEFAULT_ENABLE_OPENSHIFT_OAUTH="false"
DEFAULT_SERVER_IMAGE_NAME="registry.access.redhat.com/codeready-workspaces/server:latest"
DEFAULT_OPERATOR_IMAGE_NAME="registry.access.redhat.com/codeready-workspaces/server-operator:latest"
DEFAULT_NAMESPACE_CLEANUP="false"

HELP="

How to use this script:
-d,     --deploy          | deploy using settings in config.yaml
-p=,    --project=        | project namespace to deploy CodeReady Workspaces, default: ${DEFAULT_OPENSHIFT_PROJECT}
-c=,    --cert=           | absolute path to a self signed certificate which OpenShift Console uses
-oauth, --enable-oauth    | enable Log into CodeReady Workspaces with OpenShift credentials, default: ${DEFAULT_ENABLE_OPENSHIFT_OAUTH}
--force-cleanup           | clean up existing namespace to remove CodeReady Workspaces objects from previous installations, default: ${DEFAULT_NAMESPACE_CLEANUP}
--operator-image=         | operator image, default: ${DEFAULT_OPERATOR_IMAGE_NAME}
--server-image=           | server image, default: ${DEFAULT_SERVER_IMAGE_NAME}
-h,     --help            | show this help menu
"
if [[ $# -eq 0 ]] ; then
  echo -e "$HELP"
  exit 0
fi
for key in "$@"
do
  case $key in
    -c=*| --cert=*)
      PATH_TO_SELF_SIGNED_CERT="${key#*=}"
      shift
      ;;
    -oauth| --enable-oauth)
      ENABLE_OPENSHIFT_OAUTH="true"
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
    -d | --deploy)
      DEPLOY=true
      ;;
    --force-cleanup)
      NAMESPACE_CLEANUP=true
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

export OPENSHIFT_PROJECT=${OPENSHIFT_PROJECT:-${DEFAULT_OPENSHIFT_PROJECT}}

export ENABLE_OPENSHIFT_OAUTH=${ENABLE_OPENSHIFT_OAUTH:-${DEFAULT_ENABLE_OPENSHIFT_OAUTH}}

export SERVER_IMAGE_NAME=${SERVER_IMAGE_NAME:-${DEFAULT_SERVER_IMAGE_NAME}}

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
    if [ ${ENABLE_OPENSHIFT_OAUTH} = true ] ; then
      ${OC_BINARY} get oauthclients > /dev/null 2>&1
      OUT=$?
      if [ ${OUT} -ne 0 ]; then
        printError "You have enabled OpenShift oAuth for your installation but this feature requires cluster-admin privileges. Login in as user with cluster-admin role"
        exit $OUT
      fi
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
      else
          if [ "${NAMESPACE_CLEANUP}" = true ] ; then
          printInfo "Deleting CodeReady Workspaces related objects from namespace ${OPENSHIFT_PROJECT}"
           ${OC_BINARY} delete all --all -n="${OPENSHIFT_PROJECT}"
           ${OC_BINARY} delete pvc -l=app=postgres -n="${OPENSHIFT_PROJECT}"
           ${OC_BINARY} delete sa -l=app=che -n="${OPENSHIFT_PROJECT}"
           ${OC_BINARY} delete sa che-operator -n="${OPENSHIFT_PROJECT}"
           ${OC_BINARY} delete cm che-operator che -n="${OPENSHIFT_PROJECT}"
           ${OC_BINARY} delete role -l=app=che -n="${OPENSHIFT_PROJECT}"
           ${OC_BINARY} delete rolebinding -l=app=che -n="${OPENSHIFT_PROJECT}"
           ${OC_BINARY} delete rolebinding che-operator -n="${OPENSHIFT_PROJECT}"
           ${OC_BINARY} delete secret self-signed-cert -n="${OPENSHIFT_PROJECT}"
          fi
      fi
}

createServiceAccount() {
  printInfo "Creating installer service account"
  ${OC_BINARY} create sa che-operator -n=${OPENSHIFT_PROJECT}
  ${OC_BINARY} create rolebinding che-operator --clusterrole=admin --serviceaccount=${OPENSHIFT_PROJECT}:che-operator -n=${OPENSHIFT_PROJECT}

  if [ ${ENABLE_OPENSHIFT_OAUTH} = true ] ; then
    printInfo "You have chosen an option to enable Login With OpenShift. Granting cluster-admin privileges for apb service account"
    ${OC_BINARY} adm policy add-cluster-role-to-user cluster-admin -z che-operator
    OUT=$?
    if [ ${OUT} -ne 0 ]; then
      printError "Failed to grant cluster-admin role to abp service account"
      exit $OUT
    fi
  fi
}

createCertSecret(){
  if [ ! -z "${PATH_TO_SELF_SIGNED_CERT}" ]; then
    printInfo "You have provided a path to a self-signed certificate. Passing cert to Operator.."
    ls ${PATH_TO_SELF_SIGNED_CERT} > /dev/null
    OUT=$?
    if [ ${OUT} -ne 0 ]; then
      printError "Failed convert cert to base64 string"
      exit $OUT
    fi
    SELF_SIGNED_CERT=$(cat ${PATH_TO_SELF_SIGNED_CERT} | base64 -w 0)
  fi
}

deployCRW() {

  if [ ! -z "${PATH_TO_SELF_SIGNED_CERT}" ]; then
  USE_SELF_SIGNED_CERT=true
  fi

if [ "${JENKINS_BUILD}" = true ] ; then
  PARAMS="-i"
else
  PARAMS="-it"
fi


${OC_BINARY} create -f ${BASE_DIR}/config.yaml -n=${OPENSHIFT_PROJECT}
${OC_BINARY} patch cm/che-operator -p "{\"data\": {\"CHE_IMAGE\":\"${SERVER_IMAGE_NAME}\", \"CHE_OPENSHIFT_OAUTH\": \"${ENABLE_OPENSHIFT_OAUTH}\", \"CHE_SELF__SIGNED__CERT\": \"${SELF_SIGNED_CERT}\", \"CHE_OPENSHIFT_API_URL\": \"${OPENSHIFT_API_URI}\"}}" -n ${OPENSHIFT_PROJECT}
${OC_BINARY} delete pod che-operator -n=${OPENSHIFT_PROJECT}  2> /dev/null || true
${OC_BINARY} run -ti "che-operator" \
        --restart='Never' \
        --serviceaccount='che-operator' \
        --image="${OPERATOR_IMAGE_NAME}" \
        --overrides='{"spec":{"containers":[{"image": "'${OPERATOR_IMAGE_NAME}'", "name": "che-operator", "imagePullPolicy":"IfNotPresent","envFrom":[{"configMapRef":{"name":"che-operator"}}]}]}}' \
        -n=${OPENSHIFT_PROJECT}

OUT=$?
  if [ ${OUT} -ne 0 ]; then
    printError "Failed to deploy CodeReady Workspaces. Inspect error log."
    exit 1
  else
    PROTOCOL="http"
    TLS=$(${OC_BINARY} get route codeready -n=${OPENSHIFT_PROJECT} -o=jsonpath='{.spec.tls.termination}')
    if [ "${TLS}" ]; then
      PROTOCOL="https"
    fi
    CODEREADY_HOST=${PROTOCOL}://$(${OC_BINARY} get route codeready -n=${OPENSHIFT_PROJECT} -o=jsonpath='{.spec.host}')
    printInfo "CodeReady Workspaces successfully deployed and available at ${CODEREADY_HOST}"
  fi
}

if [ "${DEPLOY}" = true ] ; then
  preReqs
  isLoggedIn
  createNewProject
  createServiceAccount
  createCertSecret
  deployCRW
fi
