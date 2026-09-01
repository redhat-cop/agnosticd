# Workload Tasks Overview (5G Core Lab)

The `workload.yml` file deploys **only the Hub cluster and ArgoCD** for the 5G Core lab. It does **not** deploy the MNO cluster or install operators on the MNO. After workload completes, you deploy the MNO yourself using **ClusterInstance** and **PolicyGenerators** from the **5g-core-deployments-on-ocp-lab** repository.

## What Workload Does

### 1. Hub Cluster Deployment
- Hub cluster creation with kcli using the **local disconnected registry** pre-populated by oc-mirror in pre_workload.
- `disconnected_update: false` — kcli does not perform its own image mirroring; all OCP release and operator images (4.18/4.19/4.20) are already available at `infra.5g-deployment.lab:8443`.
- Manifests from **5g-core-deployments-on-ocp-lab** (hub-related).
- Hub kubeconfig retrieval and login.

### 2. Hub Cluster Configuration
- Remove kubeadmin, patch ArgoCD for ZTP, ClusterRoleBinding, wait for ArgoCD.

### 3. Hub Operators
- Hub operators via ArgoCD applications, LVMCluster, default storage class, operator readiness.

### 4. Multi-Cluster Management
- MultiClusterHub, MultiClusterEngine, readiness.

### 5. ArgoCD Applications (Hub)
- Applications from the 5G Core lab repo (no SNO/MNO deployment by this role).
- **sno1-argoapp.yaml** is not used; MNO is deployed by the user.

### 6. Workload Complete
- Final message: **Hub and ArgoCD are ready; deploy the MNO cluster using ClusterInstance and PolicyGenerators from the 5g-core-deployments-on-ocp-lab repo.**

## What Workload Does Not Do

- **No** MNO cluster deployment.
- **No** MNO kubeconfig extraction.
- **No** Telco Core RDS configuration on MNO nodes.

MNO operators (ODF, NMState, SR-IOV, PTP, MetalLB, Numaresources, Logging) and PerformanceProfile, SCTP, etc. are intended to be applied by you via the lab repo's **PolicyGenerators** and **ClusterInstance** flow, not by this role's workload phase.

## Key Components (Hub only)

- OpenShift Hub cluster (e.g. 4.20).
- ArgoCD (GitOps / ZTP support).
- LVM storage, Multi-Cluster Hub, Multi-Cluster Engine.
- Lab content and ArgoCD apps from **rhsyseng/5g-core-deployments-on-ocp-lab**.

## After Workload

1. **Hub** and **ArgoCD** are ready.
2. **12 MNO VMs** are created and defined (pre_workload); they are **not** installed by this role.
3. You install the **MNO** cluster using the lab repo's **ClusterInstance** and **PolicyGenerators** (no SiteConfig/PolicyGenTemplates in this role).

## Time and Prerequisites

- **Duration**: Hub plus MCH/MCE typically 45 to 90 minutes.
- **Prerequisites**: Pre-workload completed, pull secret, network and DNS (including mno entries) from the 5G Core repo.
