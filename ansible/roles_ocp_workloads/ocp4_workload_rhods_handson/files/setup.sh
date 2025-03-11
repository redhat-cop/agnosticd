#! /bin/bash

function oc::wait::object::availability() {
    local cmd=$1 # Command whose output we require
    local interval=$2 # How many seconds to sleep between tries
    local iterations=$3 # How many times we attempt to run the command

    ii=0

    while [ $ii -le $iterations ]
    do

        token=$($cmd) && returncode=$? || returncode=$?
        if [ $returncode -eq 0 ]; then
            break
        fi

        ((ii=ii+1))
        if [ $ii -eq 100 ]; then
            echo $cmd "did not return a value"
            exit 1
        fi
        sleep $interval
    done
}

export CATALOG_SOURCE_IMAGE=${1:-quay.io/modh/rhods-catalog:v1.1.1-58}

oc new-project redhat-ods-operator
oc new-project redhat-ods-applications
oc new-project redhat-ods-monitoring
oc create -f /home/cloud-user/olminstall/modh-reader-secret.yaml -n redhat-ods-operator
oc create -f /home/cloud-user/olminstall/modh-reader-secret.yaml -n redhat-ods-applications
oc apply -f /home/cloud-user/olminstall/modh-idh-cluster-image-puller-secret.yml --namespace=openshift-marketplace

envsubst < /home/cloud-user/olminstall/catalogsource.yaml.tpl | oc apply -f -

oc::wait::object::availability "oc get project redhat-ods-monitoring" 2 60
oc create -f /home/cloud-user/olminstall/fakesecret.yaml
oc create -f /home/cloud-user/olminstall/deadmansnitch-secret.yaml -n redhat-ods-monitoring

# If you want an openldap server running inside your cluster (handy for OSD), you can uncomment the following 3 lines
#oc create secret generic ldap-bind-password --from-literal=bindPassword=adminpassword -n openshift-config || echo "ldap secret exists"
#oc apply -f /home/cloud-user/olminstall/ldap.yaml
#oc apply -f /home/cloud-user/olminstall/oauthldaplocal.yaml

# You may want to change the userlist in each of these commands to suit your own needs
oc adm groups new rhods-admins ${USER} opentlc-mgr admin1 aasthana@redhat.com croberts@redhat.com || echo "rhods-admins group already exists"
oc adm groups new rhods-users testuser1 aasthana@redhat.com croberts@redhat.com || echo "rhods-users group already exists"

#If you'd rather not deal with the JH groups at all, uncomment the following 2 lines
#oc::wait::object::availability "oc get configmap -n redhat-ods-applications rhods-groups-config" 2 60
#oc apply -f /home/cloud-user/olminstall/nogroups.yaml
