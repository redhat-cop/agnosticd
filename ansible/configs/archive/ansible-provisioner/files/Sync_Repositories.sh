#!/bin/bash
# This script documents the process taken to reposync the OpenShift repos for the latest version.
# make sure you set the correct REPOVERSION and that your environment isn't set to shutdown automatically.

# from www.opentlc.com
#From you workstation host, run the following command to download/sync the repos down to the REPOSYNC_HOST
# Your workstation needs to be able to authenticate to both the REPOSYNC_HOST and the TARGET_HOST

# Set dynamic from command line:
export REPOVERSION="$1"
export REPOMINORVERSION="$2"

# for version 3.4 of ocp
#export REPOMINORVERSION="3.4.1.12"
#export REPOVERSION="3.4"

# for version 3.5 of ocp
# export REPOVERSION="3.5"
# export REPOMINORVERSION="3.5.5.5"
#

# for version 3.6 of ocp
# export REPOVERSION="3.6"
# export REPOMINORVERSION="3.6.173.0.49"
#

# for version 3.7 of ocp
# export REPOVERSION="3.7"
# export REPOMINORVERSION="3.7.9"

export REPOLIST="rhel-7-server-rpms rhel-7-server-extras-rpms rhel-7-server-ose-${REPOVERSION}-rpms rhel-7-fast-datapath-rpms rhel-7-server-optional-rpms rhel-7-server-rh-common-rpms"
#export REPOLIST="rhel-7-fast-datapath-rpms rhel-7-server-extras-rpms rhel-7-server-optional-rpms rhel-7-server-ose-${REPOVERSION}-rpms rhel-7-server-rpms rhel-7-server-rh-common-rpms"
#export REPOLIST="rhel-7-server-ose-${REPOVERSION}-rpms"

export CLASS="ocp"
export REPOBASE="/srv/repos/"
export REPOPATH="${REPOBASE}/${CLASS}/${REPOMINORVERSION}"
echo "REPOLIST is: $REPOLIST"
echo "REPOVERSION is: ${REPOVERSION}"
echo "CLASS is: $CLASS"

if [ -d ${REPOPATH} ]; then
  cp -r ${REPOPATH} ${REPOPATH}.$(date +%Y%m%d)
fi

mkdir -p ${REPOPATH}

cd ${REPOPATH}
time for repo_name in ${REPOLIST} ;
  do
    subscription-manager repos --enable="${repo_name}"
    mkdir ${repo_name}
    echo "Processing repo: ${repo_name}"
    echo "reposync -r ${repo_name}  -n -m -p ."
    sudo reposync -r ${repo_name}  -n -m -p .
    cd ${repo_name}
    sudo createrepo .
    cd ..
    echo "Completed processing of: ${repo_name}"
  done

#ln -s ${REPOBASE}/${CLASS}/${REPOMINORVERSION} ${REPOBASE}/${CLASS}/${REPOVERSION}


  #
  #
  # subscription-manager register --username=${RHNID} --password=${RHNPASS}
  # subscription-manager list --available
  # subscription-manager attach --pool=${RHNPOOL}
  # subscription-manager repos --disable="*"
  # subscription-manager repos \
  #    --enable="rhel-7-server-rpms" \
  #    --enable="rhel-7-server-extras-rpms" \
  #    --enable="rhel-7-server-ose-${REPOVERSION}-rpms" \
  #    --enable="rhel-7-server-optional-rpms" \
  #    --enable="rhel-7-server-rh-common-rpms" \
  #    --enable="rhel-7-fast-datapath-rpms"
  # yum install -y yum-utils createrepo tmux
  # yum clean all ; yum repolist

  # cd $REPOBASE
  # rm -rf $REPOBASE
  # mkdir -p $REPOBASE
  # cd $REPOBASE
