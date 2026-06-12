# ocp4_workload_helm_from_content_repo

## Description

Generic Helm chart deployment workload for RHDP zerotouch catalog items. Deploys Helm charts from content git repositories with security validation and lifecycle management.

**Key Features:**
- Deploy Helm charts from repository, URL, or local path sources
- Security validation (cluster-scoped, privileged, hostPath, hostNamespace, hostPort)
- Comprehensive error diagnostics (pod logs, container states, failure reasons)
- Automatic readiness waiting with configurable timeout
- Resource cleanup on catalog item destruction
- OpenShift Route creation with TLS and iframe support
- CNV and non-CNV deployment support (k8s_auth or kubeconfig)
- Backwards compatible with existing VMs-only labs

**Based on proven pattern:** Uses the same `kubernetes.core.helm_template` + `kubernetes.core.k8s` pattern as the production `ocp4_workload_showroom` workload.

---

## Prerequisites

- OpenShift cluster with namespace created
- Kubernetes authentication (CNV: API token, AWS/Azure: kubeconfig)
- Content git repository with `config/helm-charts.yaml`
- Helm chart repository accessible via HTTPS (for repository/URL sources)

---

## Usage in Catalog Items

### 1. Add to catalog item's `common.yaml`

```yaml
# Include base component
#include /includes/common/zt-rhel-bu-lab-developer-cnv.yaml

# Configure content repository
ocp4_workload_helm_from_content_repo_git_repo: https://github.com/example/my-lab-content.git
ocp4_workload_helm_from_content_repo_git_ref: main

# CNV/Babylon: Deploy to sandbox namespace where service account has permissions
ocp4_workload_helm_from_content_repo_namespace: "{{ sandbox_openshift_namespace }}"
# CNV cluster API authentication
ocp4_workload_helm_from_content_repo_k8s_auth_host: "{{ sandbox_openshift_api_url }}"
ocp4_workload_helm_from_content_repo_k8s_auth_api_key: "{{ sandbox_openshift_api_key }}"
ocp4_workload_helm_from_content_repo_validate_certs: false

# Add workload to post_software phase
post_software_workloads:
  localhost:
    - ocp4_workload_helm_from_content_repo
```

**Alternative: AWS/Azure (kubeconfig-based authentication)**

```yaml
# Configure content repository
ocp4_workload_helm_from_content_repo_git_repo: https://github.com/example/my-lab-content.git
ocp4_workload_helm_from_content_repo_git_ref: main

# AWS/Azure: Use kubeconfig file
ocp4_workload_helm_from_content_repo_namespace: "{{ guid }}"
ocp4_workload_helm_from_content_repo_kubeconfig: "{{ hostvars[groups['bastions'][0]]['ansible_env']['HOME'] }}/.kube/config"
ocp4_workload_helm_from_content_repo_validate_certs: true

# Add workload to post_software phase
post_software_workloads:
  localhost:
    - ocp4_workload_helm_from_content_repo
```

### 2. Create `config/helm-charts.yaml` in content repository

```yaml
---
charts:
  - name: postgresql
    enabled: true
    source:
      type: repository
      url: https://charts.bitnami.com/bitnami
      chart_ref: postgresql
      version: "12.5.0"
    
    release:
      name: myapp-db
      namespace: "{{ guid }}"  # Uses catalog namespace
      values:
        auth:
          postgresPassword: "{{ postgres_password }}"
        primary:
          persistence:
            size: 5Gi
    
    security:
      allowClusterScopedResources: false
      maxCpuLimit: 2000m
      maxMemoryLimit: 4Gi
      maxStorageClaim: 10Gi
    
    wait:
      enabled: true
      timeout: 600

  - name: redis
    enabled: false  # Optional chart, disabled by default
    source:
      type: repository
      url: https://charts.bitnami.com/bitnami
      chart_ref: redis
      version: "17.0.0"
    
    release:
      name: myapp-cache
      values:
        networkPolicy:
          enabled: false  # Required: sandbox service account lacks RBAC
        master:
          persistence:
            size: 2Gi
```

---

## Configuration Reference

### Workload Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ocp4_workload_helm_from_content_repo_namespace` | `{{ guid }}` | Target namespace (CNV: override to `{{ sandbox_openshift_namespace }}`) |
| `ocp4_workload_helm_from_content_repo_git_repo` | `""` | Content git repository URL |
| `ocp4_workload_helm_from_content_repo_git_ref` | `main` | Git branch/tag/commit |
| `ocp4_workload_helm_from_content_repo_k8s_auth_host` | `""` | Kubernetes API host (CNV deployments) |
| `ocp4_workload_helm_from_content_repo_k8s_auth_api_key` | `""` | Kubernetes API token (CNV deployments) |
| `ocp4_workload_helm_from_content_repo_kubeconfig` | `""` | Path to kubeconfig file (non-CNV deployments) |
| `ocp4_workload_helm_from_content_repo_validate_certs` | `true` | Validate TLS certificates |
| `ocp4_workload_helm_from_content_repo_wait_enabled` | `true` | Wait for pods to be Ready |
| `ocp4_workload_helm_from_content_repo_wait_timeout` | `600` | Maximum wait time (seconds) |
| `ocp4_workload_helm_from_content_repo_wait_retries` | `60` | Number of retry attempts for readiness checks |

### helm-charts.yaml Schema

#### Chart Definition

```yaml
charts:
  - name: string                    # Chart identifier (required)
    enabled: boolean                # Deploy this chart (required)
    source:                         # Chart source (required)
      type: repository | url | path # Source type
      # For repository type:
      url: string                   # Chart repository URL
      chart_ref: string             # Chart name in repository
      version: string               # Chart version (optional)
      # For url type:
      url: string                   # Direct URL to chart tarball
      # For path type:
      path: string                  # Relative path in content repo
    
    release:                        # Helm release config (required)
      name: string                  # Release name (required)
      namespace: string             # Target namespace (optional, defaults to workload namespace)
      values: dict                  # Chart values (optional)
    
    security:                       # Security constraints (optional)
      allowClusterScopedResources: boolean  # Allow ClusterRole, etc (default: false)
      allowPrivileged: boolean              # Allow privileged containers (default: false)
      allowHostPath: boolean                # Allow hostPath volumes (default: false)
      allowHostNamespace: boolean           # Allow hostNetwork/IPC/PID (default: false)
      allowHostPort: boolean                # Allow hostPort in containers (default: false)
      maxCpuLimit: string                   # Advisory CPU limit (default: 4000m)
      maxMemoryLimit: string                # Advisory memory limit (default: 8Gi)
      maxStorageClaim: string               # Advisory storage limit (default: 10Gi)
    
    wait:                           # Wait configuration (optional)
      enabled: boolean              # Wait for readiness (default: true)
      timeout: integer              # Wait timeout in seconds (default: 600)
    
    routes:                         # OpenShift Routes for service exposure (optional)
      - name: string                # Route name (required)
        service: string             # Service name to route to (required)
        host: string                # Hostname prefix (optional, defaults to name)
        targetPort: int|string      # Service port to target (required)
        path: string                # URL path (optional, default: /)
        tls: boolean                # Enable TLS (optional, default: false)
        tls_termination: edge|reencrypt|passthrough  # TLS termination type (default: edge)
        tls_insecure_policy: Redirect|Allow|None     # HTTP redirect policy (default: Redirect)
        tls_destination_ca_cert: string              # CA cert for reencrypt (optional)
        remove_x_frame_options: boolean              # Allow iframe embedding (default: true)
```

**Note:** Route hostname pattern is `{host}-{guid}.{apps_domain}` (e.g., `redis-abc123.apps.cluster.com`)

---

## Security Model

### Automatic Protections

1. **Namespace Isolation**: All resources deployed into scoped namespace
2. **NetworkPolicy Enforcement**: Existing `firewall.yaml` rules apply to all pods
3. **SCC Restrictions**: OpenShift SCC enforces `runAsNonRoot`, capabilities
4. **RBAC Limits**: Namespace-scoped ServiceAccount, no cluster-wide permissions

### Workload-Level Validations

| Check | Default Behavior | Override |
|-------|------------------|----------|
| **Cluster-scoped resources** | FAIL if detected | `allowClusterScopedResources: true` |
| **Privileged containers** | FAIL if `privileged: true` | `allowPrivileged: true` |
| **hostPath volumes** | FAIL if detected | `allowHostPath: true` |
| **hostNamespace usage** | FAIL if hostNetwork/IPC/PID detected | `allowHostNamespace: true` |
| **hostPort binding** | FAIL if hostPort detected | `allowHostPort: true` |
| **NetworkPolicy** | WARN if chart creates one | N/A (warning only) |
| **Resource limits** | REPORT only (advisory limits) | Set `maxCpuLimit`, `maxMemoryLimit` |

**Fail-Fast Validation:** All charts are validated before any deployment occurs. If any chart violates security constraints, the workload fails with a comprehensive error report listing ALL violations across ALL charts. This prevents partial deployments that waste namespace quota.

**Note:** Resource limits (CPU, memory, storage) are advisory only. Actual enforcement is via namespace ResourceQuota configured by the platform.

### Security Best Practices

1. **Only use trusted chart repositories** (Bitnami, official vendors)
2. **Pin chart versions** in `helm-charts.yaml` to avoid supply chain drift
3. **Review chart templates** before deploying to production
4. **Keep cluster-scoped resources disabled** unless absolutely required
5. **Use content repo firewall.yaml** for network egress rules

---

## Examples

### Example 1: PostgreSQL Database

```yaml
# config/helm-charts.yaml
charts:
  - name: postgresql
    enabled: true
    source:
      type: repository
      url: https://charts.bitnami.com/bitnami
      chart_ref: postgresql
      version: "12.5.0"
    release:
      name: lab-db
      values:
        auth:
          postgresPassword: "{{ postgres_password }}"
        primary:
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 1000m
              memory: 1Gi
          persistence:
            size: 5Gi
```

### Example 2: Multiple Charts (App + Database)

```yaml
# config/helm-charts.yaml
charts:
  - name: postgresql
    enabled: true
    source:
      type: repository
      url: https://charts.bitnami.com/bitnami
      chart_ref: postgresql
      version: "12.5.0"
    release:
      name: backend-db
      values:
        auth:
          postgresPassword: "{{ db_password }}"

  - name: myapp
    enabled: true
    source:
      type: url
      url: https://example.com/charts/myapp-1.0.0.tgz
    release:
      name: myapp
      values:
        database:
          host: backend-db-postgresql
          port: 5432
          password: "{{ db_password }}"
        ingress:
          hostname: "myapp-{{ guid }}.{{ cluster_domain }}"
```

### Example 3: With Security Overrides

```yaml
# config/helm-charts.yaml
charts:
  - name: monitoring
    enabled: true
    source:
      type: repository
      url: https://prometheus-community.github.io/helm-charts
      chart_ref: kube-prometheus-stack
      version: "45.0.0"
    release:
      name: monitoring
      values:
        prometheus:
          prometheusSpec:
            storageSpec:
              volumeClaimTemplate:
                spec:
                  resources:
                    requests:
                      storage: 10Gi
    security:
      allowClusterScopedResources: true  # Prometheus Operator needs cluster roles
      maxStorageClaim: 20Gi                # Override default 10Gi limit
    wait:
      timeout: 900  # Prometheus takes longer to start
```

### Example 4: Web App with Route for Showroom Iframe

```yaml
# config/helm-charts.yaml
charts:
  - name: nginx
    enabled: true
    source:
      type: repository
      url: https://charts.bitnami.com/bitnami
      chart_ref: nginx
      version: "18.0.0"
    release:
      name: myapp-web
      values:
        global:
          compatibility:
            openshift:
              adaptSecurityContext: force  # Required for OpenShift
        networkPolicy:
          enabled: false  # Required in sandbox environments
    
    # Create Route for external access
    routes:
      - name: webapp
        service: myapp-web-nginx
        host: webapp
        targetPort: 8080
        tls: true
        tls_termination: edge
        remove_x_frame_options: true  # Allow Showroom iframe embedding
    
    wait:
      enabled: true
      timeout: 300
```

**Showroom integration:** Add to `content/modules/m1/ui-config.yml`:
```yaml
tabs:
  - title: Web App
    url: "https://webapp-${guid}.${apps_domain}/"
    external: false  # Iframe embed (X-Frame-Options removed)
```

### Example 5: Custom Chart from Content Repository (Path-Based)

For custom Helm charts stored in your lab content repository:

```yaml
# Content repository structure:
# /helm-chart/
#   Chart.yaml
#   values.yaml
#   templates/
#     deployment.yaml
#     service.yaml

# config/helm-charts.yaml
charts:
  - name: custom-app
    enabled: true
    source:
      type: path
      path: helm-chart  # Relative path in content repo
    
    release:
      name: custom-app
      values:
        image:
          repository: quay.io/myorg/custom-app
          tag: "1.0.0"
        replicaCount: 2
        service:
          port: 8080
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 100m
            memory: 128Mi
    
    routes:
      - name: app
        service: custom-app
        targetPort: 8080
        tls: true
        remove_x_frame_options: true
```

**Use case:** Deploy multi-container pods, custom application stacks, or specialized configurations not available in public chart repositories.

**Chart location:** The workload clones your content repository and renders the chart from the specified path. Changes to the chart are automatically deployed when you update the content repository.

---

## Integration with Existing Labs

### Backwards Compatibility

Existing labs with `instances.yaml` VMs work **unchanged**:

```yaml
# Content repo structure (no changes needed)
config/
  instances.yaml      # VMs - handled by zero-touch-base-rhel
  firewall.yaml       # NetworkPolicy - applied to all pods
  networks.yaml       # Network config
  helm-charts.yaml    # NEW: Helm charts (optional)
```

### Unified Deployment

One catalog item can deploy **both VMs and containers**:

```yaml
# Catalog common.yaml
post_software_workloads:
  localhost:
    - ocp4_workload_helm_from_content_repo  # Deploys charts
    # VMs created by zero-touch-base-rhel config
```

---

## Error Diagnostics

When chart deployment fails, the workload provides comprehensive diagnostic information to help identify the issue quickly.

### Automatic Failure Reporting

If pods fail to reach Ready state within the timeout period, the workload collects and displays:

1. **Pod Status Summary**
   - Current phase (Pending, CrashLoopBackOff, etc.)
   - Pod conditions with messages
   - Namespace and pod name

2. **Container Status Details**
   - Init container states (waiting/terminated reasons, exit codes)
   - Main container states (waiting/terminated reasons, exit codes)
   - Ready status for each container

3. **Complete Container Logs**
   - Last 200 lines from each init container
   - Last 200 lines from all main containers
   - Helps identify configuration errors, missing dependencies, connection failures

### Example Diagnostic Output

```
========================================================================
Chart postgresql pod 'lab-db-postgresql-0' failed to start
========================================================================

POD STATUS SUMMARY:
- Phase: Running
- Namespace: sandbox-abc123-zt-rhelbu
- Conditions:
  - Initialized: True - N/A
  - Ready: False - containers with unready status: [postgresql]
  - ContainersReady: False - containers with unready status: [postgresql]

CONTAINER STATUSES:
Init Containers:
- init-chmod-data:
  Ready: True
  State: terminated
  Terminated: Completed (exit 0)

Main Containers:
- postgresql:
  Ready: False
  State: waiting
  Waiting: CrashLoopBackOff

CONTAINER LOGS:
=== Init Container: init-chmod-data ===
Successfully set permissions on /bitnami/postgresql/data

=== Main Container Logs ===
postgresql: error: database system was interrupted
postgresql: FATAL: data directory "/bitnami/postgresql/data" has wrong ownership
========================================================================
```

This diagnostic output appears in Ansible task output and helps identify issues without manual `oc logs` or `oc describe` commands.

---

## Resource Cleanup

The workload supports cleanup of deployed Helm chart resources when catalog items are destroyed.

### Enabling Cleanup

Add the workload to `remove_workloads` in your catalog item configuration:

```yaml
# Catalog common.yaml
post_software_workloads:
  localhost:
    - ocp4_workload_helm_from_content_repo

# Enable cleanup on destroy
remove_workloads:
  - ocp4_workload_helm_from_content_repo
```

### Cleanup Process

When `ACTION=destroy`, the workload:

1. Fetches `config/helm-charts.yaml` from content repository
2. Filters for enabled charts
3. For each chart:
   - Renders chart with `helm_template` (to get resource list)
   - Deletes all resources using `kubernetes.core.k8s` with `state: absent`
   - Waits for resource deletion (300s timeout)
4. Cleans up temporary directories
5. Reports completion

Resources are deleted **before** namespace deletion, ensuring proper cleanup even if namespace deletion is delayed or prevented.

### Manual Cleanup

If you need to manually remove chart resources:

```bash
# List deployed resources
oc get all -n <namespace> -l app.kubernetes.io/instance=<release-name>

# Delete resources
oc delete all -n <namespace> -l app.kubernetes.io/instance=<release-name>

# Delete PVCs (if any)
oc delete pvc -n <namespace> -l app.kubernetes.io/instance=<release-name>
```

---

## Troubleshooting

### Chart fails to render

**Symptom:** `helm_template` task fails with "chart not found"

**Solution:**
- Verify `chart_repo_url` is accessible
- Check `chart_ref` spelling matches chart repository
- Ensure `version` exists in repository (or omit for latest)

### Security validation fails

**Symptom:** Task fails with "SECURITY VIOLATION: cluster-scoped resource"

**Solution:**
- Review chart templates for ClusterRole, ClusterRoleBinding, CRD
- If legitimate, add `allowClusterScopedResources: true` to chart config
- Otherwise, find alternative chart without cluster-scoped resources

### Pods not becoming Ready

**Symptom:** Wait timeout exceeded, pods stuck in Pending/CrashLoopBackOff

**Solution:**
1. Check events: `oc get events -n {{ namespace }} | grep {{ release_name }}`
2. Check pod status: `oc describe pod -n {{ namespace }} -l app.kubernetes.io/instance={{ release_name }}`
3. Check logs: `oc logs -n {{ namespace }} -l app.kubernetes.io/instance={{ release_name }}`
4. Common issues:
   - PVC not binding (check storage class)
   - Image pull errors (check registry credentials)
   - Resource limits too low (check chart values)

### NetworkPolicy permission denied

**Symptom:** Deployment fails with error like:
```
'networkpolicies.networking.k8s.io "chart-name" is forbidden: 
User "system:serviceaccount:namespace:sandbox" cannot get resource "networkpolicies"'
```

**Root cause:** In CNV/Babylon environments, the sandbox service account has limited RBAC permissions and cannot create NetworkPolicy resources in the namespace.

**Solution:** Disable NetworkPolicy creation in chart values:
```yaml
# config/helm-charts.yaml
charts:
  - name: redis
    release:
      values:
        networkPolicy:
          enabled: false  # Required for sandbox environments
```

**Note:** Most Bitnami charts (redis, postgresql, mysql, etc.) create NetworkPolicy resources by default. Always set `networkPolicy.enabled: false` for charts deployed in sandbox namespaces.

---

## Development

### Testing Locally

```bash
# Clone agnosticd
git clone https://github.com/redhat-cop/agnosticd.git
cd agnosticd

# Create test catalog item
cd ~/Projects/agnosticv_all/zt-rhelbu-agnosticv/zt-admins/
mkdir test-helm-deployment

# Test deploy
ansible-playbook ansible/main.yml \
  -e @test-vars.yml \
  -e guid=test01
```

### Contributing

This workload follows AgnosticD conventions:
- Use `become_override: false` (workload runs as unprivileged user)
- Use `agnosticd_user_info` for user-facing messages
- Use `ansible.builtin.debug` for debug messages
- Follow existing error reporting patterns from `ocp4_workload_showroom`

---

## Architecture

### Workflow

```
1. Validate required variables (pre_workload)
   ↓
2. Fetch config/helm-charts.yaml from content git repo
   ↓
3. Filter for enabled: true charts
   ↓
4. Clone content repo (if path-based charts exist)
   ↓
5. RENDER PHASE: For each chart:
   ├─ Render via kubernetes.core.helm_template
   ├─ Parse YAML to manifest objects
   └─ Store in _rendered_charts list
   ↓
6. VALIDATION PHASE: For ALL rendered charts:
   ├─ Check cluster-scoped resources (ClusterRole, CRD, etc.)
   ├─ Check privileged containers (securityContext.privileged)
   ├─ Check host namespace access (hostNetwork, hostIPC, hostPID)
   ├─ Check hostPath volumes
   ├─ Check hostPort bindings
   ├─ Accumulate violations across all charts
   └─ FAIL before deployment if ANY violations found
        (prevents partial deployments that waste quota)
   ↓
7. DEPLOYMENT PHASE: For each validated chart:
   ├─ Extract pod labels from rendered manifests
   ├─ Deploy via kubernetes.core.k8s
   ├─ Create OpenShift Routes (if defined)
   ├─ Wait for pods Ready using extracted labels
   └─ On failure: collect pod logs and container states
   ↓
8. Report deployment summary (post_workload)
   ↓
9. Cleanup temporary directories
```

### Why This Pattern?

**Client-side rendering** (`helm_template`) vs server-side (`helm install`):
- ✅ No Tiller/Helm backend required on cluster
- ✅ Security validation before deployment
- ✅ GitOps-friendly (manifests in git)
- ✅ Consistent with showroom workload pattern
- ⚠️ No automatic rollback (must handle manually)

---

## References

- **Base pattern:** `ocp4_workload_showroom` workload (RHDP Showroom deployment)
- **Helm documentation:** https://helm.sh/docs/
- **Kubernetes module docs:** https://docs.ansible.com/ansible/latest/collections/kubernetes/core/
- **OpenShift Security Context Constraints:** https://docs.openshift.com/container-platform/latest/authentication/managing-security-context-constraints.html
