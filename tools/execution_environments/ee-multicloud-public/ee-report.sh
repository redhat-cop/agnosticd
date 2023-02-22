#!/usr/bin/env bash

# sum of the entrypoint as it's added from ansible-runner devel branch
sha256sum /usr/local/bin/entrypoint

echo -e "\n# Ansible\n"
ansible --version
echo
ansible-galaxy --version
echo
ansible-galaxy collection list --format yaml
echo

echo -e "\n# Python\n"
python --version
pip --version

echo "---------------- pip freeze ----------------"
pip freeze
echo "--------------------------------------------"

echo -e "\n# Packages\n"
dnf list installed

echo -e "\n# Alternatives\n"
alternatives --list
