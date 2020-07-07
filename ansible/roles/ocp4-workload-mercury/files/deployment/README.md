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
  * [SSH key access to your GitHub account](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)
  * [GitHub API Token (OAuth) to your account](https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account)

You can create a fork of the projects you have accessed and keep them separate. Keep in mind to have the same level of access permission that you have been granted.

Some customization will be required in these resource definition files for deployment from the source code in your fork.

# 2. Project setup and configurations

First, create the project namespace where the demo will be deployed.

    $ oc new-project mercury


The GitHub key based authentication requires a SSH key pairs. Refer to [SSH key access to your GitHub account](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).

Before using the SSH key to access the Project Mercury repository, create the secret:

    $ oc create secret generic "github-secret" -n mercury \
        --from-file ssh-privatekey=<path/to/ssh/private/key> \
        --type kubernetes.io/ssh-auth

The business object model definitions used on the demo are imported from the GitHub Packages repo. Downloading pre-built dependencies simplifies this initial setup process (Nexus not required or building these artifacts as part of this procedure).

In order to use the GitHub Packages we're setting up a custom Maven `settings.xml` used when building the container images from the source code (S2I). Create the `configmap` that holds the Maven settings file available on this current directory:

    $ oc create configmap "settings-mvn" -n mercury \
        --from-file settings.xml=<path/to/build-mvn-settings.xml>

This Maven settings file is using two environment variables that need are referenced in the artifacts deployment resource definition: `GITHUBUSER` and `GITHUBTOKEN`. We'll define another secret to retrieve these sensitive information and define it as needed. To do so, create a [GitHub API Token (OAuth) to your account](https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account).

Create the `mvnrepo-token-secret` as below, replacing with your GitHub _username_ and generated _token_:

    $ oc create secret generic "mvnrepo-token-secret" -n mercury \
        --from-literal token=<my_GitHub_api_token> \
        --from-literal user=<my_GitHub_username>

# 3. Deploy demo artifacts

## Product Deployment SD

    $ oc create -f <path/to/app-product-deployment.yaml> -n mercury

    imagestream.image.openshift.io/product-deployment created
    buildconfig.build.openshift.io/product-deployment created
    deploymentconfig.apps.openshift.io/product-deployment created
    service/product-deployment created
    route.route.openshift.io/product-deployment created

## Product Directory SD

    $ oc create -f <path/to/app-product-directory.yaml> -n mercury

    imagestream.image.openshift.io/product-directory created
    buildconfig.build.openshift.io/product-directory created
    deploymentconfig.apps.openshift.io/product-directory created
    service/product-directory created
    route.route.openshift.io/product-directory created

## Customer Offer SD

    $ oc create -f <path/to/app-customer-offer.yaml> -n mercury

    imagestream.image.openshift.io/customer-offer created
    buildconfig.build.openshift.io/customer-offer created
    deploymentconfig.apps.openshift.io/customer-offer created
    service/customer-offer created
    route.route.openshift.io/customer-offer created

## Customer Product and Service Eligibility SD

    $ oc create -f <path/to/app-customer-eligibility.yaml> -n mercury

    imagestream.image.openshift.io/customer-eligibility created
    buildconfig.build.openshift.io/customer-eligibility created
    deploymentconfig.apps.openshift.io/customer-eligibility created
    service/customer-eligibility created
    route.route.openshift.io/customer-eligibility created

To get the URL for the Swagger UI type the following:

    $ echo "http://$( oc get routes/customer-eligibility -n mercury -o jsonpath='{.spec.host}' )/swagger-ui"
    
    http://customer-eligibility-mercury.apps.your-cluster.domain.com/swagger-ui

## Servicing Order UI

    $ oc create -f <path/to/app-servicing-order-ui.yaml> -n mercury

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

