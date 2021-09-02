## `ansible-workshops-agnosticd`

This is the Ansible Workshops config deployed directly through agnosticd, as opposed to `ansible-workshops`, which
uses a downstream provisioner from ansible/workshops.

To pick a workshop, change the `workshop_type` variable. By default, this runs the `rhel` workshop.

### How to run

```shell
ansible-playbook \ 
    -e @ansible/configs/ansible-workshops-agnosticd/default_vars.yml \ 
    -e @ansible/configs/ansible-workshops-agnosticd/sample_vars.yml \
    ansible/main.yml --skip-tags create_inventory,create_ssh_config,wait_ssh,set_hostname
```

Modify `sample_vars.yml` with your AWS credentials and RHAAP-download-able RH offline token, along with
other changes you might want. You can also override the variables with your own vars file by adding a new
`-e @path/to.file` parameter.

To generate an `offline_token`, go to https://access.redhat.com/management/api and log in with your Red Hat account.


### Sync status with ansible/workshops

Includes changes up to and including `ansible/workshops#6b2823e861b8af370bc3d97f0f670426cc43ce77`.
