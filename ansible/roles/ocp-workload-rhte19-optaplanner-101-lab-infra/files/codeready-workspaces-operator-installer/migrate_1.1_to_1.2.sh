#!/bin/bash 

# default images & versions - these CANNOT be overridden
# see commandline flags below for what can be overridden for offline & custom registry scenarios
DEFAULT_IDENTITY_PROVIDER_IMAGE_PATH_TAG="redhat-sso-7/sso73-openshift:1.0-11"
DEFAULT_POSTGRES_IMAGE_PATH_TAG="rhscl/postgresql-96-rhel7:1-40"
DEFAULT_PVC_JOBS_IMAGE_PATH_TAG="ubi8-minimal:8.0-127"

DEFAULT_SERVER_IMAGE_NAME="server-rhel8"
DEFAULT_OPERATOR_IMAGE_NAME="server-operator-rhel8"
# set this to 1 to support having a null CRW_PREFIX (see --no-crw-prefix flag)
NO_CRW_PREFIX=0 

# default images & versions - these CAN be overriden
# see commandline flags below for what can be overridden for offline & custom registry scenarios
DEFAULT_OPENSHIFT_PROJECT="workspaces" 

DEFAULT_RH_REGISTRY="registry.redhat.io"  # could use another registry, like registry.access.redhat.com
DEFAULT_CRW_REGISTRY="${DEFAULT_RH_REGISTRY}" # could use another registry, like quay.io
DEFAULT_CRW_PREFIX="codeready-workspaces/" # could use another organization, like crw/ (for quay.io), or set blank if not used

DEFAULT_SERVER_VERSION="1.2"
DEFAULT_OPERATOR_VERSION="${DEFAULT_SERVER_VERSION}"

DEFAULT_SERVER_IMAGE="${DEFAULT_CRW_REGISTRY}/${DEFAULT_CRW_PREFIX}${DEFAULT_SERVER_IMAGE_NAME}"
DEFAULT_OPERATOR_IMAGE="${DEFAULT_CRW_REGISTRY}/${DEFAULT_CRW_PREFIX}${DEFAULT_OPERATOR_IMAGE_NAME}:${DEFAULT_OPERATOR_VERSION}"

DEFAULT_IDENTITY_PROVIDER_IMAGE="${DEFAULT_RH_REGISTRY}/${DEFAULT_IDENTITY_PROVIDER_IMAGE_PATH_TAG}"
DEFAULT_POSTGRES_IMAGE="${DEFAULT_RH_REGISTRY}/${DEFAULT_POSTGRES_IMAGE_PATH_TAG}"
DEFAULT_PVC_JOBS_IMAGE="${DEFAULT_RH_REGISTRY}/${DEFAULT_PVC_JOBS_IMAGE_PATH_TAG}"

HELP="

How to use this script to migrate from CRW 1.1 to ${DEFAULT_SERVER_VERSION}:
-p=,    --project=            | REQUIRED: CodeReady Workspaces project to migrate;      default: ${DEFAULT_OPENSHIFT_PROJECT}

        --rh-registry=        | Alternate RH registry, like registry.access.redhat.com; default: ${DEFAULT_RH_REGISTRY}
        --crw-registry=       | Alternate CRW container registry, like quay.io;         default: ${DEFAULT_CRW_REGISTRY}
        --crw-prefix=         | Alternate registry path (organization), eg., crw/;      default: ${DEFAULT_CRW_PREFIX}
        --no-crw-prefix       | Use this flag to remove registry path (organization)

        --server-version=     | Alternate CRW server version;                           default: ${DEFAULT_SERVER_VERSION}
        --operator-version=   | Alternate CRW operator version;                         default: ${DEFAULT_OPERATOR_VERSION}

        --server-image=       | Alt. CRW server image; eg., quay.io/crw/server-rhel8;   default: ${DEFAULT_SERVER_IMAGE}
        --operator-image=     | Alt. CRW operator; eg., quay.io/crw/operator-rhel8:1.2; default: ${DEFAULT_OPERATOR_IMAGE}

  --identity-provider-image=  | Alternate Identity Provider (RH SSO, Keycloak) image;   default: ${DEFAULT_IDENTITY_PROVIDER_IMAGE}
        --postgres-image=     | Alternate PostgreSQL image;                             default: ${DEFAULT_POSTGRES_IMAGE}
        --pvc-jobs-image=     | Alternate PVC Jobs image;                               default: ${DEFAULT_PVC_JOBS_IMAGE}

        --verbose             | more console output
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

    --rh-registry=*)
      RH_REGISTRY="${key#*=}"
      shift
      ;;
    --crw-registry=*)
      CRW_REGISTRY="${key#*=}"
      shift
      ;;
    --crw-prefix=*)
      CRW_PREFIX="${key#*=}"
      shift
      ;;
    --no-crw-prefix)
      NO_CRW_PREFIX=1
      shift
      ;;

    --server-version=*)
      SERVER_VERSION="${key#*=}"
      shift
      ;;
    --operator-version=*)
      OPERATOR_VERSION="${key#*=}"
      shift
      ;;

    --server-image=*)
      SERVER_IMAGE="${key#*=}"
      shift
      ;;
    --operator-image=*)
      OPERATOR_IMAGE="${key#*=}"
      shift
      ;;

    --identity-provider-image=*)
      IDENTITY_PROVIDER_IMAGE="${key#*=}"
      shift
      ;;
    --postgres-image=*)
      POSTGRES_IMAGE="${key#*=}"
      shift
      ;;
    --pvc-jobs-image=*)
      PVC_JOBS_IMAGE="${key#*=}"
      shift
      ;;

    --verbose)
      FOLLOW_LOGS="true"
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

# required to get colours
export TERM=xterm

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

if [ -x "$(command -v oc)" ]; then
  if [[ "${FOLLOW_LOGS}" == "true" ]]; then printInfo "Found oc client in PATH"; fi
  export OC_BINARY="oc"
else
  printError "Command line tool ${OC_BINARY} (https://docs.openshift.org/latest/cli_reference/get_started_cli.html) not found. Download oc client and add it to your \$PATH."
  exit 1
fi

# if using quay.io, operator is simply operator-rhel8; if using RHCC, it's server-operator-rhel8
if [[ ${CRW_REGISTRY} == "quay.io" ]]; then OPERATOR_CONTAINER="operator-rhel8"; fi

export OPENSHIFT_PROJECT=${OPENSHIFT_PROJECT:-${DEFAULT_OPENSHIFT_PROJECT}}

export RH_REGISTRY=${RH_REGISTRY:-${DEFAULT_RH_REGISTRY}}
export CRW_REGISTRY=${CRW_REGISTRY:-${DEFAULT_CRW_REGISTRY}}
if [[ ${NO_CRW_PREFIX} -eq 1 ]]; then
  export CRW_PREFIX=""
else 
  export CRW_PREFIX=${CRW_PREFIX:-${DEFAULT_CRW_PREFIX}}
fi

export SERVER_VERSION=${SERVER_VERSION:-${DEFAULT_SERVER_VERSION}}
export OPERATOR_VERSION=${OPERATOR_VERSION:-${DEFAULT_OPERATOR_VERSION}}

export SERVER_IMAGE=${SERVER_IMAGE:-${CRW_REGISTRY}/${CRW_PREFIX}${DEFAULT_SERVER_IMAGE_NAME}}
export OPERATOR_IMAGE=${OPERATOR_IMAGE:-${CRW_REGISTRY}/${CRW_PREFIX}${DEFAULT_OPERATOR_IMAGE_NAME}:${OPERATOR_VERSION}}

export IDENTITY_PROVIDER_IMAGE=${IDENTITY_PROVIDER_IMAGE:-${RH_REGISTRY}/${DEFAULT_IDENTITY_PROVIDER_IMAGE_PATH_TAG}}
export POSTGRES_IMAGE=${POSTGRES_IMAGE:-${RH_REGISTRY}/${DEFAULT_POSTGRES_IMAGE_PATH_TAG}}
export PVC_JOBS_IMAGE=${PVC_JOBS_IMAGE:-${RH_REGISTRY}/${DEFAULT_PVC_JOBS_IMAGE_PATH_TAG}}

if [[ "${FOLLOW_LOGS}" == "true" ]]; then printInfo "
OPENSHIFT_PROJECT=${OPENSHIFT_PROJECT}

RH_REGISTRY=${RH_REGISTRY}
CRW_REGISTRY=${CRW_REGISTRY}
CRW_PREFIX=${CRW_PREFIX}

SERVER_VERSION=${SERVER_VERSION}
OPERATOR_VERSION=${OPERATOR_VERSION}

SERVER_IMAGE=${SERVER_IMAGE}
OPERATOR_IMAGE=${OPERATOR_IMAGE}

IDENTITY_PROVIDER_IMAGE=${IDENTITY_PROVIDER_IMAGE}
POSTGRES_IMAGE=${POSTGRES_IMAGE}
PVC_JOBS_IMAGE=${PVC_JOBS_IMAGE}

"; fi

# check `${OC_BINARY} project` for a selected project
status="$(${OC_BINARY} project 2>&1)"
if [[ $status == *"error"* ]]; then
	echo "$status" && exit 1
fi

# check if oc client has an active session
isLoggedIn() {
  printInfo "Checking if you are currently logged in..."
  ${OC_BINARY} whoami > /dev/null
  OUT=$?
  if [ ${OUT} -ne 0 ]; then
    printError "Log in to your OpenShift cluster: ${OC_BINARY} login --server=yourServer"
    exit 1
  else
    CONTEXT=$(${OC_BINARY} whoami -c)
    printInfo "Active session found. Your current context is: ${CONTEXT}"
      ${OC_BINARY} get customresourcedefinitions > /dev/null 2>&1
      OUT=$?
      if [ ${OUT} -ne 0 ]; then
        printWarning "Creation of a CRD and RBAC rules requires cluster-admin privileges. Login in as user with cluster-admin role"
        printWarning "The installer will continue, however deployment is likely to fail"
    fi
  fi
}

# check if we already have a name=registryredhatio or type=kubernetes.io/dockerconfigjson secret
checkAuthenticationWithRegistryRedhatIo()
{
  if [[ "$(oc get secret registryredhatio 2>&1)" == *"No resources found"* ]] || \
     [[ "$(oc get secret --field-selector='type=kubernetes.io/dockerconfigjson' 2>&1)" == *"No resources found"* ]]; then
    echo "You must authenticate with registry.redhat.io in order for this script to proceed.

      Steps:

      0. Log in to openshift:

          oc login https://your.ip.address.here:8443 -u your_username -p your_password

      1. Get a login for the registry.   Details: https://access.redhat.com/RegistryAuthentication#getting-a-red-hat-login-2

      2. Log in using your new username. Details: https://access.redhat.com/RegistryAuthentication#using-authentication-3

      To keep your registry.redhat.io login secret in a separate file, such as in /path/to/some/folder/config.json:

          docker --config /path/to/some/folder/ login https://registry.redhat.io

      Otherwise your secret will be stored in ~/.docker/config.json, and all your secrets will be imported to openshift in the next step.

      3. Add your secret to your openshift:

          oc create secret generic registryredhatio --type=kubernetes.io/dockerconfigjson \\
             --from-file=.dockerconfigjson=/path/to/some/folder/config.json
          oc secrets link default registryredhatio --for=pull
          oc secrets link builder registryredhatio

      4. If successful, this query will show your new secret:

          oc get secret registryredhatio

      5. Rerun this script. If it still fails, see https://access.redhat.com/RegistryAuthentication#allowing-pods-to-reference-images-from-other-secured-registries-9
"
    exit 1
  fi
}

isLoggedIn
for image in ${SERVER_IMAGE} ${OPERATOR_IMAGE} ${IDENTITY_PROVIDER_IMAGE} ${POSTGRES_IMAGE} ${PVC_JOBS_IMAGE}; do
  if [[ "${image}" == "registry.redhat.io/"* ]]; then
    if [[ "${FOLLOW_LOGS}" == "true" ]]; then printInfo "Check authentication for ${image} ..."; fi
    checkAuthenticationWithRegistryRedhatIo
    break
  fi
done

DB_PASSWORD=$(${OC_BINARY} get deployment keycloak -o=jsonpath={'.spec.template.spec.containers[0].env[?(@.name=="DB_PASSWORD")].value'} -n=$OPENSHIFT_PROJECT)

# update to latest defaults
PATCH_JSON=$(cat << EOF
{
  "spec": {
    "database": {
      "postgresImage": "${POSTGRES_IMAGE}"
    },
    "storage": {
      "pvcJobsImage": "${PVC_JOBS_IMAGE}"
    },
    "auth": {
      "identityProviderImage": "${IDENTITY_PROVIDER_IMAGE}",
      "identityProviderPostgresPassword":"${DB_PASSWORD}"
    },
    "server": {
      "cheImage":"${SERVER_IMAGE}",
      "cheImageTag":"${SERVER_VERSION}"
    }
  }
}
EOF
)

echo; printInfo "Patch checluster CR with:"; echo ${PATCH_JSON}

if [[ "${FOLLOW_LOGS}" == "true" ]]; then printInfo "Unpatched checluster CR:"; echo "============>"; ${OC_BINARY} get checluster codeready -o json; echo "<============"; fi

${OC_BINARY} patch checluster codeready -p "${PATCH_JSON}" --type merge -n ${OPENSHIFT_PROJECT}
#  echo $?

if [[ "${FOLLOW_LOGS}" == "true" ]]; then printInfo "Patched checluster CR:"; echo "============>>"; ${OC_BINARY} get checluster codeready -o json; echo "<<============"; fi

waitForDeployment()
{
  deploymentName=$1
  DEPLOYMENT_TIMEOUT_SEC=300
  POLLING_INTERVAL_SEC=5
  printInfo "Waiting for the deployment/${deploymentName} to be scaled to 1. Timeout ${DEPLOYMENT_TIMEOUT_SEC} seconds"
  DESIRED_REPLICA_COUNT=1
  UNAVAILABLE=1
  end=$((SECONDS+DEPLOYMENT_TIMEOUT_SEC))
  while [[ "${UNAVAILABLE}" -eq 1 ]] && [[ ${SECONDS} -lt ${end} ]]; do
    UNAVAILABLE=$(${OC_BINARY} get deployment/${deploymentName} -n="${OPENSHIFT_PROJECT}" -o=jsonpath='{.status.unavailableReplicas}')
    if [[ "${FOLLOW_LOGS}" == "true" ]]; then printInfo "Deployment is in progress...(Unavailable replica count=${UNAVAILABLE}, ${timeout_in} seconds remain)"; fi
    sleep 3
  done
  if [[ "${UNAVAILABLE}" == 1 ]]; then
    printError "Deployment timeout. Aborting."
    printError "Check deployment logs and events:"
    printError "${OC_BINARY} logs deployment/${deploymentName} -n ${OPENSHIFT_PROJECT}"
    printError "${OC_BINARY} get events -n ${OPENSHIFT_PROJECT}"
    exit 1
  fi

  CURRENT_REPLICA_COUNT=-1
  while [[ "${CURRENT_REPLICA_COUNT}" -ne "${DESIRED_REPLICA_COUNT}" ]] && [[ ${SECONDS} -lt ${end} ]]; do
    CURRENT_REPLICA_COUNT=$(${OC_BINARY} get deployment/${deploymentName} -o=jsonpath='{.status.availableReplicas}')
    timeout_in=$((end-SECONDS))
    if [[ "${FOLLOW_LOGS}" == "true" ]]; then printInfo "Deployment in progress...(Current replica count=${CURRENT_REPLICA_COUNT}, ${timeout_in} seconds remain)"; fi
    sleep ${POLLING_INTERVAL_SEC}
  done

  if [[ "${CURRENT_REPLICA_COUNT}" -ne "${DESIRED_REPLICA_COUNT}" ]]; then
    printError "CodeReady Workspaces ${deploymentName} deployment failed. Aborting. Run command '${OC_BINARY} logs deployment/${deploymentName}' to get more details."
    exit 1
  elif [ ${SECONDS} -ge ${end} ]; then
    printError "Deployment timeout. Aborting."
    exit 1
  fi
  elapsed=$((DEPLOYMENT_TIMEOUT_SEC-timeout_in))
  printInfo "Codeready Workspaces deployment/${deploymentName} started in ${elapsed} seconds"
}

${OC_BINARY} scale deployment/codeready --replicas=0
${OC_BINARY} scale deployment/keycloak --replicas=0

echo; printInfo "Update operator image to ${OPERATOR_IMAGE}:"
${OC_BINARY} set image deployment/codeready-operator *=${OPERATOR_IMAGE} -n $OPENSHIFT_PROJECT
echo; printInfo "Successfully updated running deployment ${OPENSHIFT_PROJECT}."

waitForDeployment codeready-operator

${OC_BINARY} scale deployment/keycloak --replicas=1
waitForDeployment keycloak

${OC_BINARY} scale deployment/codeready --replicas=1
waitForDeployment codeready

# for some reason minishift dies for a minute or two here, so give it time to recover
sleep 60s

echo; printInfo "Update postgres image"
${OC_BINARY} set image deployment/postgres "*=${POSTGRES_IMAGE}" -n $OPENSHIFT_PROJECT
${OC_BINARY} scale deployment/postgres --replicas=0
${OC_BINARY} scale deployment/postgres --replicas=1
waitForDeployment postgres

echo; printInfo "Successfully updated running deployment ${OPENSHIFT_PROJECT}."
echo
