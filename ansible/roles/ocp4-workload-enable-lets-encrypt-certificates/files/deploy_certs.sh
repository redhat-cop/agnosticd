#!/bin/bash
pushd ~/certbot/config/renewal-hooks/deploy
ansible-playbook ./deploy_certs.yml
popd
