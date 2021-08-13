ansible-playbook 
-e @ansible/configs/ansible-workshops/default_vars.yml 
-e @ansible/configs/ansible-workshops/sample_vars.yml 
ansible/main.yml --skip-tags create_inventory,create_ssh_config,wait_ssh,set_hostname
