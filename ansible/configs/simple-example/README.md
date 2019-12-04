# Simple example

A simple deplyoment creating a bastion host and two *worker nodes*. It can't get more simplier.

## Setup

### Supported cloud providers

The following cloud providers are supported:

* AWS
* Azure

### Environment variables

Deployment is controlled by two configuration files: 

* env_vars.yml
* sample_vars.yml

`env_vars.yml` specifies all available configuration parameters that COULD be modified, whereas `sample_vars.yml` provides a *template* for all environment specific values that HAVE to be changed.

Start by creating a copy of `sample_vars.yml` and name it e.g. `my_sample_vars.yml`. Then modifiy all parameters to match your environment.

#### Secrets

Some deployments need **secrets** e.g. your AWS credentials or other API access tokens. 

DO NOT add these to git !

Instead create a file called e.g. `my_secret_vars.yml` and place all *secrets* in there.

NOTE:  

Both `my_sample_vars.yml` `my_secret.vars.yml` are in the `.gitignore` configuration which SHOULD protect you from adding them to git.

## Run the Ansible playbooks

From the ./ansible directory run following commands:

To deploy

```shell
ansible-playbook main.yml -e @configs/simple-example/my_sample_vars.yml -e @my_secret_vars.yml
```

To undeploy

```shell
ansible-playbook destroy.yml -e @configs/simple-example/my_sample_vars.yml -e @my_secret_vars.yml
```
