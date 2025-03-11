#!/usr/bin/bash

# Following gitlab command will generate token
gitlab-rails runner "\
token = User.find_by_username('root').personal_access_tokens.create(scopes: [:api], name: 'Automation token')
token.set_token('{{ gitlab_server_root_token }}')
token.save!
"
