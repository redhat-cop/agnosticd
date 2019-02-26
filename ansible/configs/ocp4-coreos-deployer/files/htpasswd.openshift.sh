# feature:  htpasswd - usage and workaround
# based on: https://gist.github.com/derekwaynecarr/3dd461be62213fa9c62edb5244b841d5

# Enable managed authentication
oc patch authenticationoperatorconfigs cluster -n openshift-authentication-operator --type=merge -p "{\"spec\":{\"managementState\": \"Managed\"}}"

# configure HTPasswd IDP
oc apply -f - <<EOF
apiVersion: config.openshift.io/v1
kind: OAuth
metadata:
  name: cluster
spec:
  identityProviders:
  - name: htpassidp
    challenge: true
    login: true
    mappingMethod: claim
    type: HTPasswd
    htpasswd:
      fileData:
        name: htpass-secret
EOF

# then load in the 100 users
oc create -f htpasswd.openshift.yaml

# kill console pods to pick up auth setup [bug that team will fix]
oc delete pods -n openshift-console --all

# now test authentication
# $ oc login -u=user2  -p='r3dh4t1!'  --insecure-skip-tls-verify=true --certificate-authority='./tls/journal-gatewayd.crt'
# Login successful.
