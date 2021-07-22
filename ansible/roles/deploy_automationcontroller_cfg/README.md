**LOCAL COPY** DO NOT USE!!!

deploy_automationcontroller
=========

Installs, and licenses via manifest, Ansible Automation controller.
Whilst a more natural naming convention might be `deploy_automation_controller` the Red Hat installer itself etc calls it `automationcontroller`.
Testing and development was done primarily using a clustered config (3 automation controller nodes and 1 database).
All in one deployments are known to work but, currently, will require additions to templates.
Currently does **not** add signed certs.


> NOTE
Currently Ansible Automation controller is **pre-release software**, therefore:
- Role may include _hacky_ fixes to the installers `setup` process
- The user will have to supply their own `deploy_automationcontroller_installer_url`
- Initial deploys are for a cluster (tweak ) 

You will need, for a clustered install of `automationcontroller`
- 3 or more RHEL 8 hosts in an ansible group `automationcontroller`
- 1 RHEL host in the group `automationcontroller_database`
    
> NOTE the config `ansible-multi-nodes` contains a fully working `sample_vars` file.
It can be deployed via:

```
ansible-playbook main.yml \
  -e @configs/ansible-multi-node/sample_vars/automationcontroller_cluster.yml \   <1>
  -e@~/secrets/openstack-red-secret.yml \                                        <2>
  -e @~/secrets/satellite-rhel8-latest.yml \                                     <3>
  -e @secrets-automationcontroller.yml \                                         <4>
  -e guid=1234
```

1. A sample vars files defining instances in the group 
* `automationcontroller`
* `automationcontroller_database`
2. Cloud secrets - get from your cluster admin
3. Repo method secrets e.g satellite, RHN (Red hat Network), file (see the docs)
4. See **Role Variables** below, but you must provide at a minimum

```
deploy_automationcontroller_installer_url:  <LINK-TO_GZIPPED-AUTOMATION-CONTROLLER-INSTALLER>
deploy_automationcontroller_manifest_path:  <PATH-TO-AUTOMATION-CONTROLLERMANIFEST>
```
Everything else has safe defaults.

Invoking this role

* Simply call as a role via `role`, `import_role`, `include_role`:

```
- name: Deploy Ansible Automation controller
  hosts: bastions[0]
  gather_facts: false
  become: true

  roles:
    - deploy_automationcontroller
```

The tag `deploy_automationcontroller_installer` can be skipped to avoid going again through the cluster installation, which takes the longest time (for test purposes).

Requirements
------------

Make sure in your inventory that the cluster nodes are in the group "automationcontroller", and that the (optional) database node is in the group "automationcontroller_database".

Role Variables
--------------

You will need to update the first 2 vars, typically supplied via `-e` or `-e @secret-vars.yml`

```
# Supply first 2 vars

deploy_automationcontroller_installer_url: "" # e.g. http://example.com/ansible-automation-platform-setup-bundle-latest.tar.gz"
deploy_automationcontroller_manifest_path: "~/secrets/automationcontroller_manifest.zip" # 

# All vars from here set to safe defaults
deploy_automationcontroller_admin_user: 
deploy_automationcontroller_admin_password: 

deploy_automationcontroller_pip_packages:

deploy_automationcontroller_dnf_packages:

deploy_automationcontroller_dnf_gpgcheck: 0

```

Dependencies
------------

None

Example Playbook
----------------

```yaml

- name: Install Ansible automation controller
  hosts: bastions[0]
  gather_facts: false
  become: true

  tasks:

    - name: Install Ansible automation controller
      include_role:
        name: deploy_automationcontroller


- name: Install Ansible controller
  hosts: bastions[0]
  become: true
  gather_facts: false

  roles:
     - deploy_automationcontroller
```

> NOTE `hosts` reflects the deployment host and not usually a automationcontroller node.
Some work to the `templates/automationcontroller_inventory.j2` is *currently* required to allow an all-in-one deployment. 

License
-------

BSD

Author Information
------------------

Original author: Tony Kay (tok) tok@redhat.com 
Much work borrowed from IPvSean https://github.com/IPvSean
