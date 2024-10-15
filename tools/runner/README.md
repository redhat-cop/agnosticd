# AgnosticD runner

This folder contains scripts to deploy an OpenShift cluster with AgnosticD from your local machine.

Once the cluster is deployed, you can use the same scripts to deploy any of the [roles_ocp_workloads](../../ansible/roles/roles_ocp_workloads) on that cluster.

## Podman

Podman is required as the Ansible Playbooks are executed in a container using an execution environment.

If you wish to use Docker instead, create an alias from podman to docker:

```bash
alias podman=docker
```

## AgnosticD Home

Please set the environment variable `AGNOSTICD_HOME` to the root of the AgnosticD repository.

```bash
export AGNOSTICD_HOME=<path to AgnosticD>
```

It may be convenient to add this to your `.bashrc` or `.zshrc` file.

## AWS Credentials

As the scripts will deploy an OpenShift cluster on AWS, have your credentials and sanbox number ready.

## Usage

For every new cluster run (example of value for sandbox: "sandbox123"):

```bash
$AGNOSTICD_HOME/tools/runner/init.sh <aws access key> <aws secret key> <sandbox>
```

The first time you run you will get a warning about the secrets.yml file being created. It is expected that you add the `satelite` and `ocp-pull-secrets` there.

To deploy an OpenShift cluster:

```bash
$AGNOSTICD_HOME/tools/runner/run.sh ocp4-cluster
```

To deploy workloads:

```bash
$AGNOSTICD_HOME/tools/runner/run.sh ocp-workloads /path/to/infra-workloads.yml
```

Example of `infra-workloads.yml`:
```yaml
# -------------------------------------------------------------------
# Workloads
# -------------------------------------------------------------------
infra_workloads:
- ocp4_workload_openshift_gitops
- ocp4_workload_gitops_bootstrap

# -------------------------------------------------------------------
# Workload: ocp4_workload_openshift_gitops
# -------------------------------------------------------------------
ocp4_workload_openshift_gitops_channel: gitops-1.9

ocp4_workload_openshift_gitops_use_catalog_snapshot: true
ocp4_workload_openshift_gitops_catalog_snapshot_image: quay.io/gpte-devops-automation/olm_snapshot_redhat_catalog
ocp4_workload_openshift_gitops_catalog_snapshot_image_tag: v4.13_2023_06_26

ocp4_workload_openshift_gitops_setup_cluster_admin: true
ocp4_workload_openshift_gitops_update_route_tls: true

ocp4_workload_openshift_gitops_rbac_update: true
ocp4_workload_openshift_gitops_rbac_policy: |
  g, admin, role:admin
ocp4_workload_openshift_gitops_rbac_scopes: '[name,groups]'

# -------------------------------------------------------------------
# ocp4_workload_gitops_bootstrap
# -------------------------------------------------------------------
ocp4_workload_gitops_bootstrap_repo_url: https://github.com/OpenShiftDemos/coolstore-portfolio
ocp4_workload_gitops_bootstrap_repo_revision: main
ocp4_workload_gitops_bootstrap_repo_path: helm/coolstore
```

## Tips and Tricks

Create alias for the scripts, so you never forget to `source` the init script as well as you can use the `caffeinate` command to prevent your machine from going to sleep.

```bash
alias agd-init=source $AGNOSTICD_HOME/tools/runner/init.sh
alias agd-run=caffeinate -disu $AGNOSTICD_HOME/tools/runner/run.sh
```
