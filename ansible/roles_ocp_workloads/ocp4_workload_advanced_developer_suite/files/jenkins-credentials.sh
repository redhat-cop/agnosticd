# Jenkins server details
JENKINS__URL=$(oc get -n tssc secrets/tssc-jenkins-integration -o json | jq -r '.data.baseUrl' | base64 -d)
JENKINS__USERNAME=$(oc get -n tssc secrets/tssc-jenkins-integration -o json | jq -r '.data.username' | base64 -d)
JENKINS__TOKEN=$(oc get -n tssc secrets/tssc-jenkins-integration -o json | jq -r '.data.token' | base64 -d)

COSIGN_SECRET_PASSWORD=$(oc get -n openshift-pipelines secrets/signing-secrets -o json | jq -r '.data["cosign.password"]')
COSIGN_SECRET_KEY=$(oc get -n openshift-pipelines secrets/signing-secrets -o json | jq -r '.data["cosign.key"]')
COSIGN_PUBLIC_KEY=$(oc get -n openshift-pipelines secrets/signing-secrets -o json | jq -r '.data["cosign.pub"]')
GITOPS_AUTH_USERNAME=root
GITOPS_GIT_TOKEN=$(oc get -n tssc secrets/tssc-gitlab-integration -o json | jq -r '.data.token' | base64 -d)
QUAY_USERNAME=$(oc get -n tssc secret tssc-quay-integration -o json | jq -r '.data[".dockerconfigjson"]' | base64 --decode | jq -r '.. | objects | select(has("username")) | .username')
QUAY_PASSWORD=$(oc get -n tssc secret tssc-quay-integration -o json | jq -r '.data[".dockerconfigjson"]' | base64 --decode | jq -r '.. | objects | select(has("password")) | .password')
ACS_TOKEN=$(oc get -n tssc secret tssc-acs-integration -o json | jq -r '.data.token' | base64 --decode)
ACS_ENDPOINT=$(oc get -n tssc secret tssc-acs-integration -o json | jq -r '.data.endpoint' | base64 --decode)

# SBOM automatic upload creds
TRUSTIFICATION_BOMBASTIC_API_URL=$(oc get -n tssc secrets/tssc-trustification-integration --template={{.data.bombastic_api_url}} | base64 -d)
TRUSTIFICATION_OIDC_ISSUER_URL=$(oc get -n tssc secrets/tssc-trustification-integration --template={{.data.oidc_issuer_url}} | base64 -d)
TRUSTIFICATION_OIDC_CLIENT_ID=$(oc get -n tssc secrets/tssc-trustification-integration --template={{.data.oidc_client_id}} | base64 -d)
TRUSTIFICATION_OIDC_CLIENT_SECRET=$(oc get -n tssc secrets/tssc-trustification-integration --template={{.data.oidc_client_secret}} | base64 -d)
TRUSTIFICATION_SUPPORTED_CYCLONEDX_VERSION=$(oc get -n tssc secrets/tssc-trustification-integration --template={{.data.supported_cyclonedx_version}} | base64 -d)


# Arrays of credential details
CREDENTIAL_IDS=("ROX_API_TOKEN" "ROX_CENTRAL_ENDPOINT" "GITOPS_AUTH_USERNAME" "GITOPS_AUTH_PASSWORD" "COSIGN_SECRET_PASSWORD" "COSIGN_SECRET_KEY" "COSIGN_PUBLIC_KEY" "TRUSTIFICATION_BOMBASTIC_API_URL" "TRUSTIFICATION_OIDC_ISSUER_URL" "TRUSTIFICATION_OIDC_CLIENT_ID" "TRUSTIFICATION_OIDC_CLIENT_SECRET" "TRUSTIFICATION_SUPPORTED_CYCLONEDX_VERSION")
SECRETS=($ACS_TOKEN $ACS_ENDPOINT $GITOPS_AUTH_USERNAME $GITOPS_GIT_TOKEN $COSIGN_SECRET_PASSWORD $COSIGN_SECRET_KEY $COSIGN_PUBLIC_KEY $TRUSTIFICATION_BOMBASTIC_API_URL $TRUSTIFICATION_OIDC_ISSUER_URL $TRUSTIFICATION_OIDC_CLIENT_ID $TRUSTIFICATION_OIDC_CLIENT_SECRET $TRUSTIFICATION_SUPPORTED_CYCLONEDX_VERSION)

# Function to add a single credential
add_secret() {
    local id=$1
    local secret=$2

    local json=$(cat <<EOF
{
  "": "0",
  "credentials": {
    "scope": "GLOBAL",
    "id": "${id}",
    "secret": "${secret}",
    "description": "",
    "\$class": "org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl"
  }
}
EOF
)

    create_credentials "$json"
}

add_username_with_password() {
    local id=$1
    local username=$2
    local password=$3

    local json=$(cat <<EOF
{
  "": "0",
  "credentials": {
    "scope": "GLOBAL",
    "id": "${id}",
    "username": "${username}",
    "password": "${password}",
    "description": "",
    "\$class": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl"
  }
}
EOF
)

    create_credentials "$json"
}

create_credentials() {
    local json=$1

    curl -X POST "$JENKINS__URL/credentials/store/system/domain/_/createCredentials" \
    --user "$JENKINS__USERNAME:$JENKINS__TOKEN" \
    --data-urlencode "json=$json"
}


# Add multiple credentials
for i in "${!CREDENTIAL_IDS[@]}"; do
    add_secret "${CREDENTIAL_IDS[$i]}" "${SECRETS[$i]}"
    echo "Credential ${CREDENTIAL_IDS[$i]} is set"
done

# Add usernames with passwords
add_username_with_password "QUAY_IO_CREDS" $QUAY_USERNAME $QUAY_PASSWORD
add_username_with_password "GITOPS_CREDENTIALS" $GITOPS_AUTH_USERNAME $GITOPS_GIT_TOKEN