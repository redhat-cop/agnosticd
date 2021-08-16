```shell
ansible-playbook \ 
    -e @ansible/configs/ansible-workshops/default_vars.yml \ 
    -e @ansible/configs/ansible-workshops/sample_vars.yml \
    ansible/main.yml --skip-tags create_inventory,create_ssh_config,wait_ssh,set_hostname
```

Includes changes up to asd including `ansible/workshops#bf22a28295b78cd444e718067631eb53e000df52`.
