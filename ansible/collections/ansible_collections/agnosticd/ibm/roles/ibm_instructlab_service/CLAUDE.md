# IBM InstructLab Service COS Permissions Guide

## Overview

This document captures critical learnings about IBM Cloud Object Storage (COS) permissions for the InstructLab service, discovered through extensive testing and troubleshooting. This knowledge is essential for maintaining the working COS permission model and troubleshooting access issues.

## Critical COS Permission Model

### The Working Solution (3-Policy Model)

For full IBM Cloud console functionality with InstructLab COS access, you need **exactly 3 IAM policies** with **identical permission levels**:

1. **Resource Group Policy**: `Writer + Viewer + Manager` on COS service scoped to resource group
2. **Instance-Level Policy**: `Writer + Viewer + Manager` on specific COS instance  
3. **Bucket-Specific Policy**: `Writer + Viewer + Manager` on specific bucket with `resourceType: "bucket"`

### Critical Requirements

- **All policies MUST have identical roles**: `Writer + Viewer + Manager`
- **Manager role is essential** for bucket visibility in IBM Cloud console
- **Bucket policy MUST include `resourceType: "bucket"`** for console visibility
- **Permission hierarchy must be consistent** to avoid IAM conflicts

## Terraform Implementation

### Resource Group Policy
```hcl
resource "ibm_iam_trusted_profile_policy" "instructlab_cos_rg_policy" {
  profile_id = ibm_iam_trusted_profile.instructlab_trusted_profile.id
  roles      = ["Writer", "Viewer", "Manager"]

  resources {
    service           = "cloud-object-storage"
    resource_group_id = local.resource_group_id
  }
}
```

### Instance-Level Policy
```hcl
resource "ibm_iam_trusted_profile_policy" "instructlab_cos_policy" {
  profile_id = ibm_iam_trusted_profile.instructlab_trusted_profile.id
  roles      = ["Writer", "Viewer", "Manager"]

  resources {
    service              = "cloud-object-storage"
    resource_instance_id = ibm_resource_instance.instructlab_cos_instance.id
  }
}
```

### Bucket-Specific Policy
```hcl
resource "ibm_iam_trusted_profile_policy" "instructlab_cos_bucket_policy" {
  profile_id = ibm_iam_trusted_profile.instructlab_trusted_profile.id
  roles      = ["Writer", "Viewer", "Manager"]

  resources {
    service              = "cloud-object-storage"
    resource_instance_id = ibm_resource_instance.instructlab_cos_instance.id
    resource_type        = "bucket"
    resource             = ibm_cos_bucket.instructlab_bucket.bucket_name
  }
}
```

## Troubleshooting Console Access Issues

### Symptom: Cannot see any COS instances in console
**Cause**: Missing or insufficient resource group permissions  
**Solution**: Add resource group policy with `Writer + Viewer + Manager` roles

### Symptom: Can see COS instance but not buckets
**Cause**: Missing bucket-specific policy or wrong resource type  
**Solution**: Add bucket policy with `resourceType: "bucket"` and `Writer + Viewer + Manager` roles

### Symptom: Console freezes or becomes unresponsive
**Cause**: IAM permission hierarchy conflicts between policies  
**Solution**: Ensure ALL COS policies have identical permission levels

### Symptom: Can see buckets but cannot access them
**Cause**: Missing Manager role or permission conflicts  
**Solution**: Verify all policies include Manager role

## Failed Approaches (DO NOT USE)

### ❌ Viewer + Operator at Resource Group Level
- **Problem**: Insufficient permissions for bucket visibility
- **Result**: Can see COS instances but not buckets

### ❌ Instance-Level Only (No Resource Group Policy)
- **Problem**: No console visibility of COS instances
- **Result**: Cannot see any COS instances in the console

### ❌ Resource Group + Instance (No Bucket Policy)
- **Problem**: Missing bucket-specific access
- **Result**: Can see instances but not buckets

### ❌ Mixed Permission Levels
- **Problem**: IAM hierarchy conflicts
- **Result**: Console freezes or unexpected behavior

## Testing Methodology

### Manual CLI Testing Process
1. **Create policies incrementally**: Start with resource group, add instance, add bucket
2. **Test console access**: Verify each level of functionality
3. **Check CLI access**: Use `ibmcloud cos list-buckets` to verify programmatic access
4. **Validate permissions**: Use `ibmcloud iam trusted-profile-policies` to inspect policies

### CLI Commands for Verification
```bash
# Check trusted profile policies
ibmcloud iam trusted-profile-policies instructlab-{guid}-tp

# List buckets in COS instance
ibmcloud cos list-buckets --ibm-service-instance-id {cos-instance-id}

# Check authorization policies
ibmcloud iam authorization-policies | grep instructlab
```

## Key IBM Cloud Behaviors

### IAM Policy Hierarchy
- **Instance-level policies override bucket-level policies** when in conflict
- **Higher permission levels mask lower permission levels**
- **Consistent permission levels prevent conflicts**

### Console Requirements
- **Resource group visibility**: Requires resource group-scoped COS policy
- **Instance visibility**: Requires instance-level COS policy  
- **Bucket visibility**: Requires bucket-specific policy with `resourceType: "bucket"`
- **Manager role**: Essential for bucket operations and visibility

### Service-to-Service Authorization
- **Authorization policy required**: InstructLab service → COS with Writer role
- **Uses GUID references**: Source and target use instance GUIDs, not IDs
- **Independent of user policies**: Service authorization is separate from user/trusted profile policies

## Bucket Naming Strategy

### Timestamp-Based Uniqueness
```hcl
cos_bucket_name = "${local.name_prefix}-${local.deployment_id}-bucket-${formatdate("YYYYMMDDHHMM", timestamp())}"
```

- **Prevents naming conflicts**: Global bucket names must be unique
- **Enables multiple deployments**: Same user can have multiple active deployments
- **Sortable by creation time**: Timestamp format allows chronological sorting

## Best Practices

### Policy Creation Order
1. **Resource Group Policy**: First for console navigation
2. **Instance Policy**: Second for instance access
3. **Bucket Policy**: Last for specific bucket access

### Security Considerations
- **Scope to specific resource group**: Prevents access to other deployments
- **Use instance-specific policies**: Avoid account-wide permissions
- **Implement trusted profiles**: Better security than direct user policies

### Automation Guidelines
- **Always create all 3 policies**: Never rely on partial permission sets
- **Use consistent roles**: Always `Writer + Viewer + Manager`
- **Include proper dependencies**: Ensure resources exist before creating policies
- **Handle policy conflicts**: Delete conflicting policies before recreating

## Manual Fix Commands

### If deployment succeeds but console access fails:

```bash
# Get resource details
GUID="your-guid"
TP_NAME="instructlab-${GUID}-tp"
RG_ID=$(ibmcloud resource groups --output json | jq -r '.[] | select(.name | startswith("instructlab-'$GUID'")) | .id')
COS_GUID=$(ibmcloud resource service-instances --service-name cloud-object-storage --output json | jq -r '.[] | select(.name | startswith("instructlab-'$GUID'")) | .guid')
BUCKET_NAME=$(ibmcloud cos list-buckets --ibm-service-instance-id "crn:v1:bluemix:public:cloud-object-storage:global:a/ACCOUNT_ID:${COS_GUID}::" --output json | jq -r '.Buckets[0].Name')

# Add missing policies
ibmcloud iam trusted-profile-policy-create $TP_NAME --roles Writer,Viewer,Manager --service-name cloud-object-storage --resource-group-id $RG_ID

ibmcloud iam trusted-profile-policy-create $TP_NAME --roles Writer,Viewer,Manager --service-name cloud-object-storage --service-instance $COS_GUID

ibmcloud iam trusted-profile-policy-create $TP_NAME --roles Writer,Viewer,Manager --service-name cloud-object-storage --service-instance $COS_GUID --resource-type bucket --resource $BUCKET_NAME
```

## Version History

- **Initial Version**: Basic COS access with minimal permissions
- **v2 (This Version)**: Complete 3-policy model with full console access
- **Key Evolution**: Discovered Manager role requirement and policy hierarchy rules

## Contributing

When modifying COS permissions:
1. **Test incrementally**: Add one policy at a time
2. **Verify console access**: Test both instance and bucket visibility
3. **Document changes**: Update this file with any new discoveries
4. **Test end-to-end**: Full destroy/provision cycle before merging

## Support

For COS permission issues:
1. **Check this document first**: Common issues and solutions documented above
2. **Use CLI verification**: Commands provided in testing methodology
3. **Test manually**: Create policies via CLI to isolate issues
4. **Document new issues**: Add findings to this document for future reference