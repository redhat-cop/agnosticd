#!/usr/bin/bash

# Following gitlab command will reset root admin password
gitlab-rails runner  -e production "\
user = User.where(id: 1).first
user.password = '{{ gitlab_server_root_token }}'
user.password_confirmation = '{{ gitlab_server_root_token }}'
user.save!
"