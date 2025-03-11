Role Name
=========

ocp-dynamic-nfs-provisioner

Install the Kubernetes Dynamic NFS Provisioner on an OpenShift Cluster.

Requirements
------------

This role needs to run on a host that has the oc binary installed and where the oc is logged into the cluster as a user with system:admin privileges.

It is probably easiest to run this role on a Master.

Role Variables
--------------

|Variable Name|Required|Default Value|Description
|------------ |----------- |-----------|-----------
|*nfs_provisioner_project*|No|"nfs-provisioner" |Name of the project for the NFS Provisioner
|*nfs_provisioner_storage_class_name*|No|"nfs-storage"|Name of the storage class associated with the NFS Provisioner
|*nfs_provisioner_storage_class_is_default*|No |False |Set to True if the NFS Provisioner Storage Class should be created as he default storage class in the cluster. Usually this is set to True if NFS is the only storage in the cluster
|*nfs_provisioner_storage_class_archiveOnDelete*|No|False |Should Volumes be archived upon deletion of a PVC
|*nfs_provisioner_storage_class_provisioner_name*|No |"nfs-storage" |Name of the NFS Storage Class Provisioner
|*nfs_provisioner_nfs_server_hostname*|Yes| "support1.GUID.internal"| The hostname (or IP Address) of the NFS Server
|*nfs_provisioner_server_directory*|Yes| "/srv/nfs/dynamic"| The top-level directory on the NFS Server under which the dynamically provisioned NFS volumes are to be created

Dependencies
------------

- NFS Server
- A directory on the NFS Server that exists with "nfsnobody:nfsnobody" and 0777 permissions (e.g. '/srv/nfs/kubernetes')


Example Playbook
----------------

```
- name: Set up Dynamic NFS Provisioning
  hosts: masters
  run_once: true
  gather_facts: False
  tasks:
  - name: Set up Dynamic NFS Provisioning
      include_role:
        name: "ocp-dynamic-nfs-provisioner"
      vars:
        nfs_provisioner_nfs_server_hostname: "support.GUID.internal"
        nfs_provisioner_storage_class_is_default: True
```
