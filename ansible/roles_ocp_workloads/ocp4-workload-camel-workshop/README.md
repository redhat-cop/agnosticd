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

<br/>

## How to maintain this workload

You will need to have an RHDP cluster available.

You can test and troubleshoot the workload in 2 different scenarios:
1. Using an environment with the workshop pre-deployed.
2. Using a brand new OpenShift enviroment where the workshop hasn't been deployed yet.

<br/>

If you need to make changes to the workload, ensure you cover the following points:
 - Run `provision` and `remove` iteratively as many times as needed.
 - If you made changes to the scritps and need to push and merge, run first `yamllint` to validate the sources (see below for details).

<br/>

## Prepare a cluster

1. To prepare a cluster and automatically provision the workshop, use the following RHDP item:
    * [**Day in the Life Camel**](https://catalog.demo.redhat.com/catalog?item=babylon-catalog-prod/openshift-cnv.dil-camel-cnv.prod&utm_source=webapp&utm_medium=share-link)

    Note: you can also search in RHDP filtering by `camel`

   <br/>

1. To prepare an empty OpenShift cluster to manually deploy the workshop, use the following RHDP item:
    * [**Red Hat OpenShift Container Platform Cluster**](https://catalog.demo.redhat.com/catalog?item=babylon-catalog-dev/openshift-cnv.ocpmulti-wksp-cnv.dev)

    Note: you can also search in RHDP filtering by `openshift cluster`

   <br/>

1. Alternatively, if you don't have access to RHDP, ensure you have an OpenShift environment available meeting the following pre-requisites:

    * Red Hat OpenShift (4.20.5)
    * OpenShift Data Foundation (4.19.8-rhodf provided by Red Hat)

    The deployment scripts will add everything else on top.

<br/>



## How to deploy the workshop

The instructions below assume:
* You either have _Docker_, _Podman_ or `ansible-playbook` installed on your local environment.
* You have provisioned an OCP instance using RHDP.

<br/>


#### Installation

1. Clone this GitHub repository:

    ```sh
    git clone https://github.com/redhat-cop/agnosticd.git
    ```

1. Change to the root directory of the project.

    ```sh
    cd agnosticd
    ```

    <br/>


1. When running with Ansible Playbook (installed on your machine)

    1. Login into your OpenShift cluster from the `oc` command line.

        For example with: 
        ```sh
        oc login --username="admin" --server=https://(...):6443 --insecure-skip-tls-verify=true
        ```
        (Replace the `--server` url with your own cluster API endpoint)

    2. Run Ansible Playbook
        ```sh
        ANSIBLE_ALLOW_BROKEN_CONDITIONALS=1 \
        ansible-playbook ./ansible/main.yml \
        -e '{"openshift_workloads": [{"name": "ocp4-workload-camel-workshop"}]}' \
        -e env_type=ocp-workloads \
        -e cloud_provider=none \
        -e ACTION=provision
        ```

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
            -e ACTION=provision
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
            -e ACTION=provision
            ```
    <br/>

<br/>

## How to undeploy the Workshop

If you wish to undeploy the workshop, use the same commands as above, but with:
 - `-e ACTION=remove`

Instead of:
 - ~~`-e ACTION=provision`~~

<br/>

## Validate before you merge

The merging process in AgnosticD runs a set of rules to validate the syntax of your source files using `yamllint`.

If you plan to contribute to AgnosticD, it is highly recommended to run `yamllint` locally rather than relying on the remote merging workflow. This will save time for both you and the RHDP reviewers.

Simply run the command below to validate your code:

```sh
yamllint -c tests/static/.yamllint \
ansible/roles_ocp_workloads/ocp4-workload-camel-workshop/
```

The example below shows you what errors look like:

<pre style="background-color: #000000; color: #cccccc; padding: 15px; font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace; font-size: 13px; line-height: 1.4; border-radius: 6px; overflow-x: auto;">
<span style="color: #00ff00; text-decoration: underline;">ansible/roles_ocp_workloads/ocp4-workload-camel-workshop/tasks/provision_streams.yaml</span>
  <span style="color: #0C6207;">24:4</span>       <span style="color: #C23720;">error</span>    <span style="color: #00ff00;">wrong indentation: expected 4 but found 3  </span><span style="color: #0C6207;">(indentation)</span>
  <span style="color: #0C6207;">27:9</span>       <span style="color: #C23720;">error</span>    <span style="color: #00ff00;">trailing spaces</span><span style="color: #0C6207;">  (trailing-spaces)</span>
  <span style="color: #0C6207;">29:151</span>     <span style="color: #C23720;">error</span>    <span style="color: #00ff00;">line too long (179 > 150 characters)  </span><span style="color: #0C6207;">(line-length)</span>
  <span style="color: #0C6207;">42:9</span>       <span style="color: #C23720;">error</span>    <span style="color: #00ff00;">trailing spaces  </span><span style="color: #0C6207;">(trailing-spaces)</span>
</pre>

Fix the problems until no errors are listed. When done, the scripts will be ready to push and merge.
