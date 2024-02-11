cd /root/
oc create configmap custom-ca \
     --from-file=ca-bundle.crt=chain1.pem \
     -n openshift-config || true

oc create secret tls letsencrypt \
     --cert=cert1.pem \
     --key=privkey1.pem \
     -n openshift-ingress || true

oc patch proxy/cluster \
  --type=merge --patch='{"spec":{"trustedCA":{"name":"custom-ca"}}}' \
  -n openshift-config || true

oc patch ingresscontroller.operator default \
     --type=merge -p \
     '{"spec":{"defaultCertificate": {"name": "letsencrypt"}}}' \
     -n openshift-ingress-operator || true

oc create namespace openshift-cnv || true

oc create configmap custom-ca \
     --from-file=ca-bundle.crt=chain1.pem \
     -n openshift-cnv || true


