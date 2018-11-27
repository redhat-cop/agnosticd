ocp-infra-nexus
=========

This role installs a Sonatype Nexus 3 on an OpenShift Cluster.

Requirements
------------

Running OpenShift 3.9 or higher Cluster

Role Variables
--------------

All variables are optional. If a variable is not passed when calling the role the defaults are being used.

|Variable Name|Required|Default Value
|------------ |----------- |-----------
|*nexus_project*|Yes|nexus
|*nexus_project_display_name*|Yes|Sonatype Nexus
|*nexus_volume_capacity*|Yes|10Gi
|*nexus_memory_request*|Yes|2Gi
|*nexus_memory_limit*|Yes|6Gi
|*nexus_cpu_request*|Yes|1
|*nexus_cpu_limit*|Yes|4
|*nexus_version*|Yes|3.12.1

Example Playbook
----------------

    - hosts: masters
      run_once: true
      roles:
        - { role: "ocp-infra-nexus", nexus_project: "sonatype-nexus" }
