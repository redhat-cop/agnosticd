# ocp-workload-rhte-keynote-ai-apps - RHTE 2019 Keynote AI Demo

## How to install

- **Important:** you'll want to give this some time before the keynote, because of steps you'll need to do later to show data drift.
- From a checkout of this repository, `cd ansible`
- Log in to your RHPDS bastion host and add an `authorized_keys` file, like this:
  - `mkdir -p .ssh`
  - `chmod 700 .ssh`
  - `curl https://github.com/${YOUR_GITHUB_HANDLE}.keys >> .ssh/authorized_keys`
- `export RHPDS_GUID=...`, where "..." is your GUID
- `export RHPDS_USER=...`, where "..." is your RHPDS username
- Install the infrastructure role:
  - `ansible-playbook -i bastion.${RHPDS_GUID}.open.redhat.com, -u ${RHPDS_USER} configs/ocp-workloads/ocp-workload.yml -e"ansible_user=${RHPDS_USER}" -e"ocp_username=opentlc-mgr" -e"ocp_workload=ocp4-workload-rhte-keynote-ai-infra" -e"silent=True" -e"guid=$RHPDS_GUID" -e"ACTION=create" -e"num_users=3"`
- Install the ODH role in each of three projects:
  - `ansible-playbook -i bastion.${RHPDS_GUID}.open.redhat.com, -u ${RHPDS_USER} configs/ocp-workloads/ocp-workload.yml -e"ansible_user=${RHPDS_USER}" -e"ocp_username=opentlc-mgr" -e"ocp_workload=ocp4-workload-rhte-keynote-ai-odh-setup" -e"silent=True" -e"guid=$RHPDS_GUID" -e"ACTION=create" -e"num_users=3"`
- Install the notebook image and Kafka apps:
  - `ansible-playbook -i bastion.${RHPDS_GUID}.open.redhat.com, -u ${RHPDS_USER} configs/ocp-workloads/ocp-workload.yml -e"ansible_user=${RHPDS_USER}" -e"ocp_username=opentlc-mgr" -e"ocp_workload=ocp4-workload-rhte-keynote-ai-apps" -e"silent=True" -e"guid=$RHPDS_GUID" -e"ACTION=create" -e"num_users=3"`

## How to set up for a run

### At least 1 hour before the demo

- Log in to one of the three projects, accepting certificate warnings
- Load the Jupyterhub route, accepting certificate warnings
  - Spawn a notebook with `ml-workflows-notebook:latest` as the notebook image
- Load the Prometheus route, accepting certificate warnings
  - Query the Prometheus UI for a graph of the following expression:  `ln(sum(pipeline_predictions_total) by (app, value))`

### At least 1/2 hour before the demo

- Scale the `flood-filter` DC to 2-4 replicas.  Your goal here is to see obvious movement in the curves on the Prometheus graphs, so watch the graph and definitely scale it to more if necessary!
- Make sure no pods are stuck in crash loops.  The Kafka producers and consumers will sometimes fail to connect to a broker; scaling them down and back up should fix it.
- Preload the following browser tabs in order to play through the demo:
  - the `workflows.ipynb` notebook from Jupyterhub,
  - The ODH operator page from the installed operators tab in the Openshift console, 
  - The `rhte-demo-notebooks` directory from jupyterhub home, 
  - either `rendered/feature-engineering.ipynb` or the version in `rhte-demo-notebooks` (if the latter, run all cells before the demo), 
  - either `rendered/model.ipynb` or the version in `rhte-demo-notebooks` (if the latter, run all cells before the demo),
  - The `pipeline` build config from the OpenShift console (you'll click in to the environment here), 
  - The `pipeline` build from the OpenShift console (you'll click in to the log), 
  - The deployment configs from the OpenShift console (show that `pipeline` is scaled out),
  - The `services.ipynb` notebook, 
  - Prometheus with `ln(sum(pipeline_predictions_total) by (app, value))` in the query window (extra credit:  add another graph with `sum(kafka_log_log_size)` to show how many messages are on Kafka topics)
