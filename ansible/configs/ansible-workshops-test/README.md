ansible-playbook -e @ansible/configs/ansible-workshops-test/default_vars.yml 
-e @ansible/configs/ansible-workshops-test/default_vars_ec2.yml 
-e @ansible/configs/ansible-workshops-test/sample_vars_ec2.yml 
ansible/main.yml --skip-tags create_inventory,create_ssh_config,wait_ssh,set_hostname
