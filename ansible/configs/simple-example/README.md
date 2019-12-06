# Simple example

A simple deplyoment creating a bastion host and two worker nodes. It can't get simpler ...

### Environment variables

Deployment is controlled by two configuration files: 

* env_vars.yml
* sample_vars.yml

`env_vars.yml` defines all configuration parameters that COULD be modified, whereas `sample_vars.yml` is a *template* for all environment specific values that HAVE to be changed.

Start by creating a copy of `sample_vars.yml` and rename it (e.g. `my_sample_vars.yml`). Then modifiy all parameters to match your environment.

#### Secrets

Some deployments need **secrets** e.g. your AWS credentials or API tokens. 

DO NOT add these to git !

Instead create a file called e.g. `./ansible/my_secret_vars.yml` and store all secrets etc. there. This file can also be reused for other deplyoments.

NOTE:  

Both `my_sample_vars.yml` `my_secret.vars.yml` are in the `.gitignore` configuration which SHOULD protect you from adding them to git!

### Run the Ansible playbooks

Run follwoing commands from the `./ansible` folder:

#### Install

```shell
ansible-playbook main.yml -e @configs/simple-example/my_sample_vars.yml -e @my_secret_vars.yml
```

#### Uninstall

```shell
ansible-playbook destroy.yml -e @configs/simple-example/my_sample_vars.yml -e @my_secret_vars.yml
```
