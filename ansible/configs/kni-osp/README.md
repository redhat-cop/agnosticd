# KNI Baremetal Lab

## Overview

KNI Lab leverages openstackbmc component to create "fake baremetal" nodes that can be used by the Openshift Baremetal IPI mechanism. It creates 2 networks : appnet that have routing enabled and can get floating IPs, and pxenet used for nodes provisioning. It will also make an ideal base infrastructure to build on and can easily be extended via it's `env_vars.yml` to less or more machines and also to different operating system images. default_vars options have also been added to be able to enable or disable port security for appnet on a per-node/port basis to allow for nested virtualization networking to flow correctly on provision and worker nodes for CNV labs

## Supported Cloud Providers

- OSP

## Review the Env_Type variable file

The link:./env_vars.yml[./env_vars.yml] file contains all the variables you need to define to control the deployment of your environment.

This includes the ability to:

- Change the number of machines deployed
- Change the operating system image (e.g. Ansible AMI or similar)
- Change the tags carried by any instances
- Change the base packages installed
- Change/set the `ansible_user` and `remote_user`

These can be over-ridden at `ansible-playbook` runtime via `-e` options or perhaps more compactly by overriding vars in your own var file and invoking via `-e @my_env_vars.yml`

## Environment Overview

This environment is used to deploy any number of Fake BM nodes for Openshift Baremetal IPI and Openshift Virtualization use. It may also be used as an example for other Fake BM needing labs (OpenStack, RHV, ...)

## Review the Env_Type variable file

- This file link:./env_vars.yml[./env_vars.yml] contains all the variables you need to define to control the deployment of your environment.

## To Delete an environment

```
ansible-playbook -e @configs/kni-osp/env_vars.yml -e ~/configs.yaml
```
