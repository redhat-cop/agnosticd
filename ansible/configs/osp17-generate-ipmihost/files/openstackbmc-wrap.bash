#!/bin/bash

echo "Waiting 120 seconds before to continue"
sleep 120 
curl https://www.opentlc.com/download/novello/openstackbmc/jq -o /usr/local/bin/jq
chmod u+x /usr/local/bin/jq
hash -r
if mount /dev/sr0 /mnt; then
API_URL=$(cat /mnt/openstack/latest/meta_data.json|jq -r ".meta.api_url")
API_USER=$(cat /mnt/openstack/latest/meta_data.json|jq -r ".meta.api_user")
API_PASS=$(cat /mnt/openstack/latest/meta_data.json|jq -r ".meta.api_pass")
PROJECT_NAME=$(cat /mnt/openstack/latest/meta_data.json|jq -r ".meta.project_name")
PXE_IMAGE=$(cat /mnt/openstack/latest/meta_data.json|jq -r ".meta.pxe_image")
umount /mnt

else
API_URL=$(curl -s http://169.254.169.254/openstack/latest/meta_data.json|jq -r ".meta.api_url")
API_USER=$(curl -s http://169.254.169.254/openstack/latest/meta_data.json|jq -r ".meta.api_user")
API_PASS=$(curl -s http://169.254.169.254/openstack/latest/meta_data.json|jq -r ".meta.api_pass")
PROJECT_NAME=$(curl -s http://169.254.169.254/openstack/latest/meta_data.json|jq -r ".meta.project_name")
PXE_IMAGE=$(curl -s http://169.254.169.254/openstack/latest/meta_data.json|jq -r ".meta.pxe_image")
fi

python /usr/local/bin/openstackbmc-wrap.py $API_URL $API_USER $API_PASS $PROJECT_NAME $PXE_IMAGE
