#!/bin/bash
pushd ~/idm/certbot/config/renewal-hooks/deploy
ansible-playbook ./deploy_certs.yml \
  -e "_certbot_domain={{ idm_dns_name }}" \
  -e 'idm_dm_password={{ idm_dm_password }}'
popd
