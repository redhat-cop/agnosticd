# Project Mercury demo deployment

These files define all resources for deploying the Project Mercury demo artifacts in an OpenShift cluster. The Ansible role defined through AgnosticD as part of this source repository will read these files to apply the deployment.

Below are instructions for manual deployment and configuration, so you can skip using automated form and have control over the deployment to your cluster.

## TOC

- [1. Pre-requisites](#1-pre-requisites)
- [2. Project setup and configurations](#2-project-setup-and-configurations)
- [3. Deploy demo artifacts](#3-deploy-demo-artifacts)
- [4. Access the demo UI and components](#4-access-the-demo-ui-and-components)

# 1. Pre-requisites

The following accesses and resources will be required to fully deploy the Project Mercury demo:
  * OpenShift 4.4+
    * _Version primary used in Project Mercury development, but this instructions should work on OpenShift 3.11 as well_
  * OpenShift Client (`oc` command line)
    * _You should be logged in and have enough permission to administer a project_
  * Access to Project Mercury GitHub repositories
    * rh-mercury/mercury-camel-sd
    * rh-mercury/product-eligibility-DMN
    * rh-mercury/servicing-order-ui
  * [GitHub API Token (OAuth) to your account](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)

You can create a fork of the projects you have accessed and keep them separate. Keep in mind to have the same level of access permission that you have been granted.

Some customization will be required in these resource definition files for deployment from the source code in your fork.

# 2. Project setup and configurations

First, create the project namespace where the demo will be deployed.

    $ oc new-project mercury


The business object model definitions used on the demo are imported from the GitHub Packages repo. Downloading pre-built dependencies simplifies this initial setup process (Nexus not required or building these artifacts as part of this procedure).

In order to use the GitHub Packages we're setting up a custom Maven `settings.xml` used when building the container images from the source code (S2I). Create the `configmap` that holds the Maven settings file available on this current directory:

    $ curl -o build-mvn-settings.xml https://raw.githubusercontent.com/rmarins/agnosticd/development/ansible/roles/ocp4-workload-mercury/files/deployment/build-mvn-settings.xml

    $ oc create configmap "settings-mvn" -n mercury \
        --from-file settings.xml=build-mvn-settings.xml

    configmap/settings-mvn created

This Maven settings file is using two environment variables that need are referenced in the artifacts deployment resource definition: `GITHUBUSER` and `GITHUBTOKEN`. We'll define another secret to retrieve these sensitive information and define it as needed. To do so, create a [GitHub API Token (OAuth) to your account](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).

Create the `github-token-secret` as below, replacing with your GitHub _username_ and generated _token_:

    $ oc create secret generic "github-token-secret" -n mercury \
        --from-literal token=<my_GitHub_api_token> \
        --from-literal user=<my_GitHub_username>

    secret/github-token-secret created

# 3. Deploy demo artifacts

## Product Deployment SD

    $ oc create -f https://raw.githubusercontent.com/rmarins/agnosticd/development/ansible/roles/ocp4-workload-mercury/files/deployment/app-product-deployment.yaml -n mercury

    imagestream.image.openshift.io/product-deployment created
    buildconfig.build.openshift.io/product-deployment created
    deploymentconfig.apps.openshift.io/product-deployment created
    service/product-deployment created
    route.route.openshift.io/product-deployment created

## Product Directory SD

    $ oc create -f https://raw.githubusercontent.com/rmarins/agnosticd/development/ansible/roles/ocp4-workload-mercury/files/deployment/app-product-directory.yaml -n mercury

    imagestream.image.openshift.io/product-directory created
    buildconfig.build.openshift.io/product-directory created
    deploymentconfig.apps.openshift.io/product-directory created
    service/product-directory created
    route.route.openshift.io/product-directory created

## Customer Offer SD

    $ oc create -f https://raw.githubusercontent.com/rmarins/agnosticd/development/ansible/roles/ocp4-workload-mercury/files/deployment/app-customer-offer.yaml -n mercury

    imagestream.image.openshift.io/customer-offer created
    buildconfig.build.openshift.io/customer-offer created
    deploymentconfig.apps.openshift.io/customer-offer created
    service/customer-offer created
    route.route.openshift.io/customer-offer created

## Customer Product and Service Eligibility SD

    $ oc create -f https://raw.githubusercontent.com/rmarins/agnosticd/development/ansible/roles/ocp4-workload-mercury/files/deployment/app-customer-eligibility.yaml -n mercury

    imagestream.image.openshift.io/customer-eligibility created
    buildconfig.build.openshift.io/customer-eligibility created
    deploymentconfig.apps.openshift.io/customer-eligibility created
    service/customer-eligibility created
    route.route.openshift.io/customer-eligibility created

## Servicing Order UI

    $ oc create -f https://raw.githubusercontent.com/rmarins/agnosticd/development/ansible/roles/ocp4-workload-mercury/files/deployment/app-servicing-order-ui.yaml -n mercury

    imagestream.image.openshift.io/openjdk-11 created
    imagestream.image.openshift.io/servicing-order-ui created
    buildconfig.build.openshift.io/servicing-order-ui created
    deploymentconfig.apps.openshift.io/servicing-order-ui created
    service/servicing-order-ui created
    route.route.openshift.io/servicing-order-ui created

# 4. Access the demo UI and components

Get service domains' URL to access the Swagger UI typing the following:

    $ echo "http://$( oc get routes/product-directory -n mercury -o jsonpath='{.spec.host}' )/swagger-ui"
    http://product-directory-mercury.apps.your-cluster.domain.com/swagger-ui

_Replace with other Service Domain in the above command to get all access._

The Servicing Order UI provides an initial web page as entry point for the demo, to get the URL do the following:

    $ echo "http://$( oc get routes/servicing-order-ui -n mercury -o jsonpath='{.spec.host}' )/calculator.html"
    http://servicing-order-ui-mercury.apps.your-cluster.domain.com/calculator.html

