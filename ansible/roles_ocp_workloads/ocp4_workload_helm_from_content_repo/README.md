# ocp4_workload_helm_from_content_repo

## Description

Generic Helm chart deployment workload for RHDP zerotouch catalog items. Deploys Helm charts from content git repositories with security validation and lifecycle management.

**Key Features:**
- ✅ Deploy Helm charts from remote chart repositories
- ✅ Security validation (cluster-scoped blocking, privileged detection, resource limits)
- ✅ Automatic readiness waiting with comprehensive failure reporting
- ✅ Backwards compatible with existing VMs-only labs
- ✅ Reusable across all catalog items

**Based on proven pattern:** Uses the same `kubernetes.core.helm_template` + `kubernetes.core.k8s` pattern as the production `ocp4_workload_showroom` workload.

---

## Prerequisites

- OpenShift cluster with namespace created
- Helm chart repository accessible via HTTPS
- Content git repository with `config/helm-charts.yaml`

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
| `ocp4_workload_helm_from_content_repo_namespace` | `{{ guid }}` | Target namespace for deployments |
| `ocp4_workload_helm_from_content_repo_git_repo` | `""` | Content git repository URL |
| `ocp4_workload_helm_from_content_repo_git_ref` | `main` | Git branch/tag/commit |
| `ocp4_workload_helm_from_content_repo_wait_enabled` | `true` | Wait for pods to be Ready |
| `ocp4_workload_helm_from_content_repo_wait_timeout` | `600` | Maximum wait time (seconds) |

### helm-charts.yaml Schema

#### Chart Definition

```yaml
charts:
  - name: string                    # Chart identifier (required)
    enabled: boolean                # Deploy this chart (required)
    source:                         # Chart source (required)
      type: repository | url        # Source type
      url: string                   # Chart repository URL
      chart_ref: string             # Chart name in repository
      version: string               # Chart version (optional)
    
    release:                        # Helm release config (required)
      name: string                  # Release name (required)
      namespace: string             # Target namespace (optional, defaults to workload namespace)
      values: dict                  # Chart values (optional)
    
    security:                       # Security constraints (optional)
      allowClusterScopedResources: boolean  # Allow ClusterRole, etc (default: false)
      allowPrivileged: boolean              # Allow privileged containers (default: false)
      allowHostPath: boolean                # Allow hostPath volumes (default: false)
      maxCpuLimit: string                   # Max CPU limit per container (default: 4000m)
      maxMemoryLimit: string                # Max memory limit per container (default: 8Gi)
      maxStorageClaim: string               # Max PVC size (default: 10Gi)
    
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
| **NetworkPolicy** | WARN if chart creates one | N/A (warning only) |
| **Resource limits** | INFO (enforced by quota) | Set `maxCpuLimit`, `maxMemoryLimit` |

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
1. Fetch config/helm-charts.yaml from content git repo
   ↓
2. Filter for enabled: true charts
   ↓
3. For each chart:
   ├─ Render via kubernetes.core.helm_template
   ├─ Parse manifests for security validation
   ├─ Check cluster-scoped, privileged, hostPath
   ├─ Deploy via kubernetes.core.k8s
   └─ Wait for pods Ready (with failure reporting)
   ↓
4. Report deployment summary
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

- **Base pattern:** `ocp4_workload_showroom` workload
- **Platform docs:** `~/Projects/cursor-revisit/platform/showroom-deployer-helm-reference.md`
- **Design doc:** `~/Projects/cursor-revisit/platform/foreman-generic-helm-workload-security-design.md`
- **Research:** `~/Projects/cursor-revisit/operations/foreman-poc-progress.md`
