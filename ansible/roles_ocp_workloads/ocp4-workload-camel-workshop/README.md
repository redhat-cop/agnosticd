# DIL Camel workshop 

This repository contains the deployment scripts for the workshop.

<br/>

## Tested with

* Red Hat OpenShift (4.20.5)
* OpenShift Data Foundation (4.19.8-rhodf provided by Red Hat)
* Streams for Apache Kafka (3.0.1-7 provided by Red Hat)
* OpenShift Dev Spaces (3.24.1 provided by Red Hat)
* Camel JBang 4.16
* Kaoto 2.8


## Deployment instructions

### 1. Provision an OpenShift environment

1. Provision the following RHDP item:
    * [**Day in the Life Camel**](https://catalog.demo.redhat.com/catalog?item=babylon-catalog-prod/openshift-cnv.dil-camel-cnv.prod&utm_source=webapp&utm_medium=share-link)

    Note: you can also search in RHDP filtering by `camel`

   <br/>

1. Alternatively, if you don't have access to RHDP, ensure you have an OpenShift environment available meeting the following pre-requisites:

    * Red Hat OpenShift (4.20.5)
    * OpenShift Data Foundation (4.19.8-rhodf provided by Red Hat)

    The deployment scripts will add everything else on top.

<br/>

### 2. Deploy the Workshop

The instructions below assume:
* You either have _Docker_, _Podman_ or `ansible-playbook` installed on your local environment.
* You have provisioned an OCP instance using RHDP.

<br/>


#### Installation

1. Clone this GitHub repository:

    ```sh
    git clone https://github.com/redhat-cop/agnosticd.git
    ```

1. Change to root directory of the project.

    ```sh
    cd agnosticd
    ```

    <br/>

1. When running with _Docker_ or _Podman_
    
    1. Configure the `KUBECONFIG` file to use (where kube details are set after login).

        ```sh
        export KUBECONFIG=./ansible/kube-demo
        ```

    1. Login into your OpenShift cluster from the `oc` command line.

        ```sh
        oc login --username="admin" --server=https://(...):6443 --insecure-skip-tls-verify=true
        ```

        Replace the `--server` url with your own cluster API endpoint.

    1. Run the Playbook

        1. With Podman:
        
            ```sh
            podman run -i -t --rm --entrypoint /usr/local/bin/ansible-playbook \
            -v $PWD:/runner \
            -v $PWD/ansible/kube-demo:/home/runner/.kube/config \
            quay.io/agnosticd/ee-multicloud:v0.0.11 \
            ./ansible/main.yml \
            -e '{"openshift_workloads": [{"name": "ocp4-workload-camel-workshop"}]}' \
            -e env_type=ocp-workloads \
            -e cloud_provider=none \
            -e "ACTION=provision"
            ```

        1. With Docker:
        
            ```sh
            docker run -i -t --rm --entrypoint /usr/local/bin/ansible-playbook \
            -v $PWD:/runner \
            -v $PWD/ansible/kube-demo:/home/runner/.kube/config \
            quay.io/agnosticd/ee-multicloud:v0.0.11 \
            ./ansible/main.yml \
            -e '{"openshift_workloads": [{"name": "ocp4-workload-camel-workshop"}]}' \
            -e env_type=ocp-workloads \
            -e cloud_provider=none \
            -e "ACTION=provision"
            ```
        
    <br/>

1. When running with Ansible Playbook (installed on your machine)

    1. Login into your OpenShift cluster from the `oc` command line.

        For example with: \
        ```sh
        oc login --username="admin" --server=https://(...):6443 --insecure-skip-tls-verify=true
        ```
        (Replace the `--server` url with your own cluster API endpoint)

    1. Set the following property:
        ```
        TARGET_HOST="lab-user@bastion.b9ck5.sandbox1880.opentlc.com"
        ```
    2. Run Ansible Playbook
        ```sh
        ansible-playbook -i $TARGET_HOST,ansible/inventory/openshift.yaml ./ansible/install.yaml
        ```

<br/>

### 3. Undeploy the Workshop

If you wish to undeploy the demo, use the same commands as above, but with:
 - `-e "ACTION=remove"`

Instead of:
 - ~~`-e "ACTION=provision"`~~
