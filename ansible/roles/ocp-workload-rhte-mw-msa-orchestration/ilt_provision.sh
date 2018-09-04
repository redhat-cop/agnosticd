#!/bin/bash

START_PROJECT_NUM=1
END_PROJECT_NUM=1
WORKLOAD="ocp-workload-rhte-mw-msa-orchestration"
LOG_FILE=/tmp/$WORKLOAD
HOST_GUID=`oc whoami --show-server | cut -d'.' -f 2`
OCP_DOMAIN=$HOST_GUID.openshift.opentlc.com

PATH_TO_AAD_ROOT=$TRAINING/gpte/ansible_agnostic_deployer/ansible


for var in $@
do
    case "$var" in
        --START_PROJECT_NUM=*) START_PROJECT_NUM=`echo $var | cut -f2 -d\=` ;;
        --END_PROJECT_NUM=*) END_PROJECT_NUM=`echo $var | cut -f2 -d\=` ;;
        --PATH_TO_AAD_ROOT=*) PATH_TO_AAD_ROOT=`echo $var | cut -f2 -d\=` ;;
        -h) HELP=true ;;
        -help) HELP=true ;;
        --help) HELP=true ;;
    esac
done

function ensurePreReqs() {
    if [ "x$HOST_GUID" == "x" ]; then
            echo -en "must pass parameter: --HOST_GUID=<ocp host GUID> . \n\n"
            help
            exit 1;
    fi

    LOG_FILE=$LOG_FILE-$HOST_GUID-$START_PROJECT_NUM-$END_PROJECT_NUM.log
    echo -en "starting\n\n" > $LOG_FILE

    echo -en "\n\nProvision log file found at: $LOG_FILE\n";
}

function help() {
    echo -en "\n\nOPTIONS:";
    echo -en "\n\t--START_PROJECT_NUM=*     OPTIONAL: specify # of first OCP project to provision (defult = 1))"
    echo -en "\n\t--END_PROJECT_NUM=*       OPTIONAL: specify # of OCP projects to provision (defualt = 1))"
    echo -en "\n\t--PATH_TO_AAD_ROOT=*       OPTIONAL: (defualt = $PATH_TO_AAD_ROOT))"
    echo -en "\n\t-h                        this help manual"
    echo -en "\n\n\nExample:                ./roles/$WORKLOAD/ilt_provision.sh --HOST_GUID=dev39 --START_PROJECT_NUM=1 --END_PROJECT_NUM=1\n\n"
}


function login() {

    echo -en "\nHOST_GUID=$HOST_GUID\n" >> $LOG_FILE
    oc login https://master.$HOST_GUID.openshift.opentlc.com -u opentlc-mgr -p r3dh4t1!
}


function executeLoop() {

    echo -en "\nexecuteLoop() START_PROJECT_NUM = $START_PROJECT_NUM ;  END_PROJECT_NUM=$END_PROJECT_NUM" >> $LOG_FILE

    for (( c=$START_PROJECT_NUM; c<=$END_PROJECT_NUM; c++ ))
    do
        GUID=$c
        OCP_USERNAME=user$c
        executeAnsibleViaLocalhost
    done
}


function executeAnsibleViaLocalhost() {

    GUID=$PROJECT_PREFIX$GUID

    echo -en "\n\nexecuteAnsibleViaLocalhost():  Provisioning project with GUID = $GUID and OCP_USERNAME = $OCP_USERNAME\n" >> $LOG_FILE

    ansible-playbook -i localhost, -c local ./configs/ocp-workloads/ocp-workload.yml \
                    -e"ANSIBLE_REPO_PATH=`pwd`" \
                    -e"ocp_username=${OCP_USERNAME}" \
                    -e"ocp_workload=${WORKLOAD}" \
                    -e"guid=${GUID}" \
                    -e"ocp_user_needs_quota=True" \
                    -e"ocp_domain=$OCP_DOMAIN" \
                    -e"ACTION=create" >> $LOG_FILE

    if [ $? -ne 0 ];
    then
        echo -en "\n\n*** Error provisioning where GUID = $GUID\n\n " >> $LOG_FILE
        echo -en "\n\n*** Error provisioning where GUID = $GUID\n\n "
        exit 1;
    fi
}

if [ "x$HELP" == "xtrue" ]; then
    help
    exit 0
fi

cd $PATH_TO_AAD_ROOT
ensurePreReqs
login
executeLoop

