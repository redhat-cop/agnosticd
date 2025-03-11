Ansible Role: Maistra and OpenShift Service Mesh (Istio, Kiali and Jaeger)
[![Build Status](https://travis-ci.org/siamaksade/ansible-openshift-maistra.svg?branch=master)](https://travis-ci.org/siamaksade/ansible-openshift-maistra)
=========

Ansible Role for deploying [Maistra](http://maistra.io/) and OpenShift Service Mesh on OpenShift which deploys the 
following components:

* Istio
* Jaeger
* Prometheus
* Grafana
* Kiali

Role Variables
------------

|Variable                  | Default Value                       |          | Description   |
|--------------------------|-------------------------------------|----------|---------------|
|`openshift_master_public` | -                                   | Required | OpenShift master public url (required) |
|`maistra_version`         | maistra-0.1.0-ocp-3.1.0-istio-1.0.0 | Optional | Maistra version to deploy |
|`kiali_username`          | `admin`                             | Optional | Kiali username |
|`kiali_password`          | `admin`                             | Optional | Kiali password |
|`openshift_cli`           | oc                                  | Optional | OpenShift CLI command and arguments (e.g. auth) |

Example Playbook
------------

```
name: Example Playbook
hosts: localhost
tasks:
- import_role:
    name: siamaksade.openshift_maistra
  vars:
    openshift_master_public: https://master.openshift.mydomain.com
```