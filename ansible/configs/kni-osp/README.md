# KNI Baremetal Lab

## Overview

KNI Lab leverages openstackbmc component to create "baremetal" nodes that can be used by the kni ansible playbooks It will also make an ideal base infrastructure to build on and can easily be extended via it's `env_vars.yml` to less or more machines and also to different operating system images.

image::topology.png[width=100%]

## Supported Cloud Providers

- OSP

## Review the Env_Type variable file

The link:./env_vars.yml[./env_vars.yml] file contains all the variables you need to define to control the deployment of your environment.

This includes the ability to:

- Change the number of machines deployed
- Changed the operating system image (e.g. Ansible AMI or similar)
- Change the tags carried by any instances
- Change the base packages installed
- Change/set the `ansible_user` and `remote_user`

These can be over-ridden at `ansible-playbook` runtime via `-e` options or perhaps more compactly by overriding vars in your own var file and invoking via `-e @my_env_vars.yml`

## Environment Overview

This environment is used to deploy any number of RHEL nodes for generic use. It is also used as an example for new contributors to Agnostic D as an example

## Review the Env_Type variable file

- This file link:./env_vars.yml[./env_vars.yml] contains all the variables you need to define to control the deployment of your environment.

## To Delete an environment

```
ansible-playbook -e @configs/kni-osp/sample_vars.yml -e ~/configs.yaml
```
