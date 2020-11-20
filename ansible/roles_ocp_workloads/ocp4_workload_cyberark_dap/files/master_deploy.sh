#!/bin/bash
exec 1>cyberark_setup/master-deploy.log 2>&1

# This scripts configures a DAP primary node and sets it up to act as both Primary and Follower.
# A worker node is selected to host the Primary and pinned to it using a nodeSelector.
# This greatly simplifies lab setup by making each lab cluster self-contained.

cd cyberark_setup

export CYBERARK_NAMESPACE_NAME=$1
export DAP_ADMIN_PASSWORD=$2

source ./dap_service_rhpds.config

if [ -z "${AUTHN_USERNAME}" ]; then
  echo "You must set values for env vars AUTHN_USERNAME and AUTHN_PASSWORD."
  exit -1
fi

main() {
  label_node
  start_master
  MASTER_POD_NAME=$(oc get pods -n $CYBERARK_NAMESPACE_NAME | grep dap-service-node | grep Running | awk '{print $1}')
  init_cluster_authn
  enable_authn_on_master
  initialize_verify_k8s_api_secrets
  create_configmaps
  init_secrets
}

########################
label_node() {
  echo "Labeling node for master..."
  # list worker nodes, get name of first one, label it as the master host
  first_worker="$(oc get nodes | grep worker | cut -d " " -f 1 | head -n 1)"
  oc label nodes $first_worker $DAP_MASTER_NODE_LABEL=true
}

########################
start_master() {
  echo "Starting and configuring primary..."
  oc create route passthrough --service=dap-service-node --port=https -n $CYBERARK_NAMESPACE_NAME
  conjur_follower_route=$(oc get routes | grep conjur-follower | awk '{ print $2 }')
  FOLLOWER_ALTNAME="$FOLLOWER_ALTNAMES,$conjur_follower_route"

  cat ./templates/master-deployment-manifest.template			\
  | sed -e "s#{{ CONJUR_APPLIANCE_IMAGE }}#$REGISTRY_APPLIANCE_IMAGE#g" 	\
  | sed -e "s#{{ DAP_MASTER_NODE_LABEL }}#$DAP_MASTER_NODE_LABEL#g" 		\
  > ./master-deployment-manifest.yaml
  oc apply -f ./master-deployment-manifest.yaml -n $CYBERARK_NAMESPACE_NAME

  MASTER_POD_NAME=""				# variable used globally
  while [[ "$MASTER_POD_NAME" == "" ]]; do	# wait till pod is running
    echo -n "."
    sleep 3
    MASTER_POD_NAME=$(oc get pods -n $CYBERARK_NAMESPACE_NAME | grep dap-service-node | grep Running | awk '{print $1}')
  done
  echo

  oc exec -it $MASTER_POD_NAME -n $CYBERARK_NAMESPACE_NAME -- \
	evoke configure master				\
		-h $CONJUR_FOLLOWER_SERVICE_NAME	\
		-p $DAP_ADMIN_PASSWORD			\
		--accept-eula				\
		$CONJUR_ACCOUNT

  wait_till_node_is_responsive
}

########################
init_cluster_authn() {
  echo "Initializing authentication..."
  cat ./templates/master-authenticator-policy.template		\
    | sed -e "s#{{ CLUSTER_AUTHN_ID }}#$CLUSTER_AUTHN_ID#g" 		\
    | sed -e "s#{{ CYBERARK_NAMESPACE_NAME }}#$CYBERARK_NAMESPACE_NAME#g" \
    > master-authenticator-policy.yaml
  ./load_policy.sh root ./master-authenticator-policy.yaml
}

########################
enable_authn_on_master() {
  echo "Enabling authentication..."
  oc exec $MASTER_POD_NAME -n $CYBERARK_NAMESPACE_NAME --		\
	evoke variable set CONJUR_AUTHENTICATORS authn-k8s/$CLUSTER_AUTHN_ID

  oc exec $MASTER_POD_NAME -n $CYBERARK_NAMESPACE_NAME --		\
	chpst -u conjur conjur-plugin-service possum 			\
        rake authn_k8s:ca_init["conjur/authn-k8s/$CLUSTER_AUTHN_ID"]

  wait_till_node_is_responsive
}

########################
initialize_verify_k8s_api_secrets() {
  echo "Initializing cluster API URL & credentials..."
  SA_TOKEN_NAME="$(oc get secrets -n $CYBERARK_NAMESPACE_NAME	\
    | grep "dap-authn-service.*service-account-token"		\
    | head -n1 \
    | awk '{print $1}')" && echo $SA_TOKEN_NAME

  # using SA_TOKEN_NAME from above step…
  echo "Adding DAP service account token as secret..."
  ./get_set.sh set \
     conjur/authn-k8s/$CLUSTER_AUTHN_ID/kubernetes/service-account-token \
     $(oc get secret -n $CYBERARK_NAMESPACE_NAME $SA_TOKEN_NAME -o json\
     | jq -r .data.token \
     | $BASE64D)

  # using SA_TOKEN_NAME from above step…
  echo
  echo
  echo "Adding ca cert as secret..."
  ./get_set.sh set \
    conjur/authn-k8s/$CLUSTER_AUTHN_ID/kubernetes/ca-cert \
    "$(oc get secret -n $CYBERARK_NAMESPACE_NAME $SA_TOKEN_NAME -o json \
      | jq -r '.data["ca.crt"]' \
      | $BASE64D)"

  echo
  echo
  echo "Adding k8s API URL as secret..."
  ./get_set.sh set \
    conjur/authn-k8s/$CLUSTER_AUTHN_ID/kubernetes/api-url \
    "$(oc config view --minify -o yaml | grep server | awk '{print $2}')"

  echo
  echo
  echo "Validating K8s API values." 
  echo
  echo "Get k8s cert..."
  echo "$(./get_set.sh get conjur/authn-k8s/$CLUSTER_AUTHN_ID/kubernetes/ca-cert)" > k8s.crt
  echo
  echo "Get DAP service account token..."
  TOKEN=$(./get_set.sh get conjur/authn-k8s/$CLUSTER_AUTHN_ID/kubernetes/service-account-token)
  echo
  echo
  echo "Get K8s API URL..."
  API=$(./get_set.sh get conjur/authn-k8s/$CLUSTER_AUTHN_ID/kubernetes/api-url)
  echo
  echo
  echo -n "Verified if 'ok': "
  curl -s --cacert k8s.crt --header "Authorization: Bearer ${TOKEN}" $API/healthz && echo
  rm k8s.crt && unset API TOKEN SA_TOKEN_NAME
}

########################
create_configmaps() {
  echo "Creating config map..."
  cat ./templates/dap-config-map-manifest.template 			\
    | sed -e "s#{{ CONJUR_ACCOUNT }}#$CONJUR_ACCOUNT#g" 				\
    | sed -e "s#{{ CONJUR_MASTER_HOSTNAME }}#$CONJUR_MASTER_HOSTNAME#g" 	\
    | sed -e "s#{{ CYBERARK_NAMESPACE_NAME }}#$CYBERARK_NAMESPACE_NAME#g"	\
    | sed -e "s#{{ CLUSTER_AUTHN_ID }}#$CLUSTER_AUTHN_ID#g" 			\
    > ./dap-cm-manifest.yaml

  # append entries for master & follower certs
  echo "  CONJUR_MASTER_CERTIFICATE: |" >> dap-cm-manifest.yaml
  ./get_cert_REST.sh $CONJUR_MASTER_HOSTNAME $CONJUR_MASTER_PORT	\
    | awk '{ print "    " $0 }'						\
    >> dap-cm-manifest.yaml

  echo "  CONJUR_FOLLOWER_CERTIFICATE: |" >> dap-cm-manifest.yaml
  ./get_cert_REST.sh $CONJUR_MASTER_HOSTNAME $CONJUR_MASTER_PORT	\
    | awk '{ print "    " $0 }'						\
    >> dap-cm-manifest.yaml

  oc apply -f ./dap-cm-manifest.yaml -n $CYBERARK_NAMESPACE_NAME
}

########################
init_secrets() {
  echo "Initializing secrets..."
  cat ./templates/master-secrets-policy.template			\
    | sed -e "s#{{ VAULT_NAME }}#$VAULT_NAME#g"		 		\
    | sed -e "s#{{ LOB_NAME }}#$LOB_NAME#g" 				\
    | sed -e "s#{{ SAFE_NAME }}#$SAFE_NAME#g" 			\
    | sed -e "s#{{ ACCOUNT_NAME }}#$ACCOUNT_NAME#g" 			\
    > master-secrets-policy.yaml
  ./load_policy.sh root ./master-secrets-policy.yaml delete

  ./get_set.sh set $VAULT_NAME/$LOB_NAME/$SAFE_NAME/$ACCOUNT_NAME/username $MYSQL_USERNAME
  ./get_set.sh set $VAULT_NAME/$LOB_NAME/$SAFE_NAME/$ACCOUNT_NAME/password $MYSQL_PASSWORD
}

############################
wait_till_node_is_responsive() {
  set +e
  node_is_healthy=""
  while [[ "$node_is_healthy" == "" ]]; do
    sleep 2
    node_is_healthy=$(curl -sk $CONJUR_APPLIANCE_URL/health | grep "ok" | tail -1 | grep "true")
  done
  set -e
}

main "$@"
