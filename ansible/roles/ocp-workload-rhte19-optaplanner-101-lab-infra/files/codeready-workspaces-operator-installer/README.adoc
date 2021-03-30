## Operator installer README

This document explains how to use the Operator installer (deployment script).

### Prerequisites

* a running OpenShift or link:https://docs.okd.io/latest/minishift/index.html[Minishift] instance
* an active session (you should be logged in)
* cluster-admin privileges to register CRD and grant Operator service account cluster admin permissions
```
oc login --server=https://your.ip.address.here:8443 -u developer -p developer
```

### Required Permissions

To successfully deploy CodeReady Workspaces using this script, cluster-admin privileges are required. The table below lists objects and required permissions:

[%autowidth]
|===
| *Kind*             | *Name*                          | *Description*                                                    | *Permissions*
| CRD                |                                 | Custom Resource definition - CheCluster                          | cluster-admin
| CR                 | codeready                       | Custom Resource of CheCluster Kind                               | cluster-admin. Alternatively, a clusterrole can be created
| ServiceAccount     | codeready-operator              | Operator uses this SA to reconcile CRW objects                   | edit role in a target namespace
| Role               | codeready-operator              | Scope of permissions for operator service account                | cluster-admin
| RoleBinding        | codeready-operator              | Assign role to service account                                   | edit role in a target namespace
| Deployment         | codeready-operator              | Deployment with operator image in template spec                  | edit role in a target namespace
| ClusterRole        | codeready-operator              | ClusterRole that lets create, update, delete oAuthClients        | cluster-admin
| ClusterRoleBinding | ${NAMESPACE}-codeready-operator | ClusterRoleBinding that lets create, update, delete oAuthClients | cluster-admin
| Role               | secret-reader                   | Role that lets read secrets in router namespace                  | cluster-admin
| RoleBinding        | ${NAMESPACE}-codeready-operator | RoleBinding that lets read secrets in router namespace           | cluster-admin
|===

By default, operator service account gets privileges to list, get, watch, create, update and delete ingresses, routes, service accounts, roles,
rolebindings, pvcs, deployments, configmaps, secrets, as well as run execs into pods, watch events and read pod logs in a target namespace.

With self signed certificates support enabled, the operator service account will get privileges to read secrets in an OpenShift router namespace.

With OpenShift oAuth enabled, the operator service account will get privileges to get, list, create, update and delete oAuthclients at a cluster scope.

### Quickstart

The simplest way to run the script is to use all the defaults.

The following command will grab config from custom-resource.yaml and start an installer image:

```
./deploy.sh --deploy
```

### Installation Configuration

The installer script will use command line args and `link:custom-resource.yaml[custom-resource.yaml]` file to populate Operator CR spec fields.

#### Configuration

You can override default envs. Not all configuration parameters are available as flags. Run `./deploy.sh --help` to get a list of all available arguments.

`link:custom-resource.yaml[custom-resource.yaml]` is a template with CR object holding spec fields that instruct the Operator on how exactly to deploy and configure CodeReady Workspaces.

#### Examples

##### Deploy with all defaults

The following command will grab config from custom-resource.yaml and start an installer image:

```
./deploy.sh --deploy
```
Specify a project/namespace:

```
./deploy.sh --deploy -p=mynamespace
```

#### Deploy without support of self signed certs, OpenShift OAuth and a custom server-image

```
./deploy.sh --deploy --server-image=myserver/image --version=latest --public-certs
```

##### Deploy with external Red Hat SSO:

In `link:custom-resource.yaml[custom-resource.yaml]`:

```
auth:
  externalIdentityProvider: true
  identityProviderURL: 'https://my-keycloak.com'
  identityProviderRealm: 'myrealm'
  identityProviderClientId: 'myClient'

```

##### Deploy with external Red Hat SSO and Postgres DB:

In `link:custom-resource.yaml[custom-resource.yaml]`:

```
database:
  externalDb: true
  chePostgresHostname: 'http://postgres'
  chePostgresPort: '5432'
  chePostgresUser: 'myuser'
  chePostgresPassword: 'mypass'
  chePostgresDb: 'mydb'

....
auth:
  externalIdentityProvider: true
  identityProviderAdminUserName: 'https://my-keycloak.com'
  identityProviderRealm: 'myrealm'
  identityProviderClientId: 'myClient'
```

### External DB and RH SSO Support

You can connect to external DB and RH SSO instances. The installer supports the following combinations:

* DB + RH SSO
* RH SSO alone

External DB + bundled RH SSO isn't currently supported. Provisioning of database and Keycloak realm and client happens only with bundled resources,
i.e. if you are connecting your own DB or Keycloak you need to pre-create resources. Refer to installation docs for more details.


## Upgrade from 1.0.1 to 1.1

### Prerequisites

These are the same Prerequisites as above.

* a running OpenShift or link:https://docs.okd.io/latest/minishift/index.html[Minishift] instance
* an active session (you should be logged in)
* cluster-admin privileges to register CRD and grant Operator service account cluster admin permissions
```
oc login --server=https://your.ip.address.here:8443 -u developer -p developer
```

### Migration

CodeReady Workspaces 1.1.0 introduces an Operator that uses controller to watch custom resources. There is no direct upgrade path from CodeReady Workspaces 1.0.1 to CodeReady Workspaces 1.1.0. If you do not have any important workspaces and projects in an existing 1.0.1 namespace, we recommend deleting the 1.0.1 installation and deploying CodeReady Workspaces 1.1.0.

However, if you want to keep an existing 1.0.1 installation, it is possible to upgrade by deploying the new operator to an existing namespace.

#### Automated method

. Run `link:migrate.sh[migrate.sh]` using the name of your existing deployed project / `$targetNamespace`.

. Check changes in `link:custom-resource.yaml[custom-resource.yaml]`.

. Run `link:deploy.sh[deploy.sh]` using the parameters for your environment.

#### Manual method

. Obtain the current Postgres password (`POSTGRESQL_PASSWORD`) from the existing Postgres deployment environment, or run the following `oc` command against your `$targetNamespace`:

```
oc get deployment postgres -o=jsonpath={'.spec.template.spec.containers[0].env[?(@.name=="POSTGRESQL_PASSWORD")].value'} -n $targetNamespace
```

[start=2]
. Obtain the current Keycloak administrator username and password (`SSO_ADMIN_USERNAME` and `SSO_ADMIN_PASSWORD`) from the existing Keycloak deployment environment, or run the following `oc` command:

```
oc get deployment keycloak -o=jsonpath={'.spec.template.spec.containers[0].env[?(@.name=="SSO_ADMIN_USERNAME")].value'} -n $targetNamespace
oc get deployment keycloak -o=jsonpath={'.spec.template.spec.containers[0].env[?(@.name=="SSO_ADMIN_PASSWORD")].value'} -n $targetNamespace
```

If you have changed the RH SSO administrator password, provide an actual password instead of fetching it from the environment variables.

[start=3]
. Replace the following values in the `link:custom-resource.yaml[custom-resource.yaml]` file with values you have obtained:

```
spec:
  database:
    chePostgresPassword: 'password'
  auth:
    keycloakAdminUserName: 'username'
    keycloakAdminPassword: 'password'
```

[start=4]
. Optional. If you have configured OpenShift oAuth, obtain the oAuth secret and set its value in the `link:custom-resource.yaml[custom-resource.yaml]` file:

To obtain the secret, take the following steps.

[start=a]
.. Run the following command as the cluster administrator:


```
oc get oauthclient openshift-identity-provider-h2fh -o=jsonpath={'.secret'}
```

[start=b]
.. Add the following fields to the `spec.auth` section of the `link:custom-resource.yaml[custom-resource.yaml]` file. Replace `$secret` with an actual secret. Set `oAuthClientName` to `'openshift-identity-provider-h2fh'` if not already set.

```
spec:
  auth:
    oAuthClientName: 'openshift-identity-provider-h2fh'
    oAuthSecret: 'secret'

```

[start=5]
. Save `link:custom-resource.yaml[custom-resource.yaml]`

[start=6]
. Run the `link:deploy.sh[deploy.sh]` script using parameters for your environment.

## Uninstall

There's no dedicated function in the `link:deploy.sh[deploy.sh]` script that can uninstall CodeReady Workspaces.

However, you can delete a custom resource, which will delete all associated objects:

```
oc delete checluster/codeready -n $targetNamespace
```

where `$targetNamespace` is an OpenShift project with deployed CodeReady Workspaces (`workspaces` by default).
