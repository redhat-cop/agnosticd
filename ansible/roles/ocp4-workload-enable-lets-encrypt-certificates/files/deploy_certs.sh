#!/bin/bash -l
cd ${HOME}/certbot/renewal-hooks/deploy/
ansible-playbook ./deploy_certs.yml
