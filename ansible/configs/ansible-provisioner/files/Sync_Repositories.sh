# This script documents the process taken to reposync the OpenShift repos for the latest version.
# make sure you set the correct REPOVERSION and that your environment isn't set to shutdown automatically.



# from www.opentlc.com
#From you workstation host, run the following command to download/sync the repos down to the REPOSYNC_HOST
# Your workstation needs to be able to authenticate to both the REPOSYNC_HOST and the TARGET_HOST

export REPOVERSION="$1"
export REPOMINORVERSION="$2"
export REPOLIST="rhel-7-fast-datapath-rpms rhel-7-server-extras-rpms rhel-7-server-optional-rpms rhel-7-server-ose-${REPOVERSION}-rpms rhel-7-server-rpms rhel-7-server-rh-common-rpms"
export CLASS="ocp"
export REPODIR="/var/www/html/repos/"
export REPOPATH="${REPODIR}/${CLASS}/${REPOMINORVERSION}"
echo "REPOLIST is: $REPOLIST"
echo "REPOVERSION is: ${REPOVERSION}"
echo "CLASS is: $CLASS"
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

mkdir -p ${REPOPATH}

cd ${REPOPATH}
for repo_name in ${REPOLIST} ;
  do
    echo "Processing repo: ${repo_name}"
    echo "reposync -r ${repo_name}  -n -m -p ."
    sudo reposync -r ${repo_name}  -n -m -p .
    cd ${repo_name}
    sudo createrepo .
    cd ..
    #sudo tar -zcvf ${repo_name}.tar.gz ${repo_name}
    echo "Completed processing of: ${repo_name}"
  done

ln -s ${REPOPATH} ${REPODIR}/${CLASS}/${REPOVERSION}
