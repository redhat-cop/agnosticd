#!/bin/bash

# need to wait here until cloud-init does it's thing, usually around 10 seconds.
echo "Waiting for cloud-init to finish startup"
sleep 15

API_URL=$(curl -s http://169.254.169.254/openstack/latest/meta_data.json|jq -r ".meta.api_url")
API_USER=$(curl -s http://169.254.169.254/openstack/latest/meta_data.json|jq -r ".meta.api_user")
API_PASS=$(curl -s http://169.254.169.254/openstack/latest/meta_data.json|jq -r ".meta.api_pass")
PROJECT_NAME=$(curl -s http://169.254.169.254/openstack/latest/meta_data.json|jq -r ".meta.project_name")

python /usr/local/bin/ravellobmc-wrap.py $API_URL $API_USER $API_PASS $PROJECT_NAME

