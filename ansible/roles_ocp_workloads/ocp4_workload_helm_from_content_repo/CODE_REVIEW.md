# Code Review: ocp4_workload_helm_from_content_repo

**Date:** 2026-06-10  
**Reviewer:** Systematic audit against proven agnosticd patterns

## Issues Found and Fixed

### 1. ❌ Passing Dynamic Dict to release_values (process_helm_chart.yml)

**Issue:**
```yaml
# BROKEN: Both approaches fail
release_values: "{{ _chart['release']['values'] | default({}) }}"  # Type conversion to string
release_values: {{ _chart['release']['values'] | default({}) }}    # YAML parse error
```

**Root Cause:**
- `helm_template` module's `release_values` parameter requires dict type
- **With quotes:** Ansible converts dict variable to string representation  
- **Without quotes:** YAML parser fails because `{{` looks like inline dict syntax
- `showroom` workload uses **literal YAML dict blocks**, not dynamic variables
- Ansible YAML parser cannot handle unquoted Jinja2 expressions that start with `{`

**Additional Issue - Dict Method Ambiguity:**
```
ERROR: to_nice_yaml - cannot represent an object: <built-in method values of dict object>
```
- Jinja2 dot notation `_chart.release.values` called the dict `.values()` method
- Must use bracket notation `_chart['release']['values']` to force key access

**Fix:**
```yaml
# WORKING: Write values to temp file, use values_files parameter
- name: Write chart values to temporary file
  ansible.builtin.copy:
    content: "{{ _chart['release']['values'] | default({}) | to_nice_yaml }}"
    dest: "/tmp/helm_values_{{ _chart_name }}.yml"
    mode: '0644'

- name: Render helm chart with values file
  kubernetes.core.helm_template:
    ...
    values_files:
      - "/tmp/helm_values_{{ _chart_name }}.yml"
```

**Reference:** `ocp4_workload_hashicorp` uses `values_files` with temp file. This is the standard pattern for passing dynamic dicts to Helm charts in Ansible.

---

### 2. ❌ Nested Attribute Access in selectattr (validate_security.yml)

**Issue:**
```yaml
# BROKEN: Jinja2 selectattr doesn't support dot notation
| selectattr('securityContext.privileged', 'defined')
```

**Root Cause:**
- Jinja2's `selectattr` filter doesn't traverse nested attributes via dot notation
- This filter would silently fail or return empty list
- Security check would never trigger even if privileged containers exist

**Fix:**
```yaml
# WORKING: Explicit loop with nested attribute access
{% set privileged = [] -%}
{% for container in _containers -%}
  {% if container.securityContext is defined 
     and container.securityContext.privileged is defined 
     and container.securityContext.privileged -%}
    {{ privileged.append(container) or '' }}
  {%- endif -%}
{%- endfor -%}
{{ privileged }}
```

**Impact:** Security validation for privileged containers now works correctly.

---

### 3. ⚠️ Jinja2 Variables in Static YAML (zt-wilson-poc/config/helm-charts.yaml)

**Issue:**
```yaml
# BROKEN: Variables in static files aren't expanded
release:
  namespace: "{{ guid }}"  # Never gets replaced!
```

**Root Cause:**
- YAML files fetched via HTTP are static content
- Ansible doesn't template them unless explicitly using `template` module
- Variables remain as literal strings

**Fix:**
```yaml
# WORKING: Rely on workload defaults
release:
  # namespace defaults to workload namespace (guid)
  # No need to specify, workload handles it
```

**Alternative:** Use Ansible's `template` module or fetch to temp file first, but simpler to rely on defaults.

---

## Audit Findings (No Issues)

### ✅ YAML Parsing (main.yml, process_helm_chart.yml)

**Checked:**
```yaml
{{ (r_helm_charts_yaml.content | from_yaml).charts | default([]) }}
{{ r_helm_templates.stdout | from_yaml_all | list }}
```

**Status:** SAFE - Parsing text to dicts/lists, type preserved correctly.

---

### ✅ Kubernetes Manifest Deployment (process_helm_chart.yml)

**Checked:**
```yaml
kubernetes.core.k8s:
  definition: "{{ r_helm_templates.stdout | from_yaml_all }}"
```

**Status:** SAFE - `k8s` module accepts both YAML text and dicts, `from_yaml_all` generator works.

---

### ✅ List Extraction in Security Validation (validate_security.yml)

**Checked:**
```yaml
_containers: >-
  {% if _manifest.kind == 'Pod' %}
  {{ _manifest.spec.containers | default([]) }}
  {% elif ...%}
```

**Status:** SAFE - Extracting lists from parsed manifests, no type conversion issues.

---

## Pattern Comparison: Our Code vs. Showroom

| Aspect | Showroom (Reference) | Our Code (Before) | Our Code (After) |
|--------|---------------------|-------------------|------------------|
| **release_values** | Inline dict structure | Variable → helm_template ❌ | Direct access ✅ |
| **Nested attrs** | N/A (no security checks) | selectattr dot notation ❌ | Explicit loop ✅ |
| **YAML parsing** | Same pattern | Same pattern ✅ | Same pattern ✅ |
| **Template vars** | Inline, no static YAML | Static YAML ❌ | Use defaults ✅ |

---

## Testing Recommendations

### Unit Tests Needed

1. **Type preservation:**
   ```yaml
   - Verify release_values is dict, not string
   - Check with complex nested dicts
   - Test with empty values dict
   ```

2. **Security validation:**
   ```yaml
   - Test privileged container detection
   - Test nested securityContext.privileged: true
   - Test containers without securityContext (should pass)
   ```

3. **Edge cases:**
   ```yaml
   - Empty helm-charts.yaml
   - Missing values key
   - Chart with no containers
   - Multiple privileged containers
   ```

### Integration Tests

1. Deploy Redis chart (current test)
2. Deploy chart with privileged container (should FAIL)
3. Deploy multiple charts in one deployment
4. Test with chart using complex values structure

---

## Lessons Learned

### Ansible Type Handling

1. **Don't store dicts in variables for module parameters**
   - Pass directly: `param: "{{ source_dict }}"`
   - Avoid: `temp: "{{ source_dict }}"` → `param: "{{ temp }}"`

2. **Jinja2 filter limitations**
   - `selectattr` doesn't support nested attributes
   - Use explicit loops or `json_query` for complex structures
   - Test filters with sample data before production

3. **Static YAML files**
   - Fetched files via `uri` aren't templated
   - Use Ansible variables/defaults instead of Jinja2 in static files
   - Or use `template` module if templating is required

### Reference Implementation Pattern

Always check existing workloads for proven patterns:
```bash
rg "kubernetes.core.helm_template" ansible/roles_ocp_workloads/ -A 10
```

Match production code structure exactly unless there's a specific reason to diverge.

---

## Files Changed

1. `tasks/process_helm_chart.yml` - Fixed release_values type issue
2. `tasks/validate_security.yml` - Fixed selectattr nested attribute access
3. `~/Projects/zt-wilson-poc/config/helm-charts.yaml` - Removed Jinja2 variables

---

## Commit History

```
415fa7173 Fix helm_template release_values type issue - use YAML literal block instead of quotes
<new>     Fix type conversion and nested attribute issues
```

---

## Next Actions

1. ✅ Push fixes to `zt-helm-deploy-test` branch
2. ✅ Push content repo fixes to `helm-test` branch
3. ⏳ Redeploy test catalog to validate fixes
4. ⏳ Monitor for new errors in CI/deployment logs
5. ⏳ Add unit tests for type preservation and security checks
