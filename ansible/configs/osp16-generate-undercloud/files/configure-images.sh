mkdir images
sudo yum -y install rhosp-director-images
tar -C images -xvf /usr/share/rhosp-director-images/overcloud-full-latest.tar
tar -C images -xvf /usr/share/rhosp-director-images/ironic-python-agent-latest.tar
source ~/stackrc
openstack overcloud image upload --image-path ~/images
