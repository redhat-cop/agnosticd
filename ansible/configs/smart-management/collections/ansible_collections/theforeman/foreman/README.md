# Foreman Ansible Modules ![Build Status](https://github.com/theforeman/foreman-ansible-modules/workflows/CI/badge.svg)

Ansible modules for interacting with the Foreman API and various plugin APIs such as Katello.

## Documentation

A list of all modules and their documentation can be found at [theforeman.org/plugins/foreman-ansible-modules](https://theforeman.org/plugins/foreman-ansible-modules/).

## Support

### Supported Foreman and plugins versions

Modules should support any currently stable Foreman release and the matching set of plugins.
Some modules have additional features/arguments that are only applied when the corresponding plugin is installed.

We actively test the modules against the latest stable Foreman release and the matching set of plugins.

### Supported Ansible Versions

The supported Ansible versions are aligned with currently maintained Ansible versions that support Collections (2.8+).
You can find the list of maintained Ansible versions [here](https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#release-status).

### Supported Python Versions

Starting with Ansible 2.7, Ansible only supports Python 2.7 and 3.5 (and higher). These are also the only Python versions we develop and test the modules against.

### Known issues

* Some modules, e.g. `repository_sync` and `content_view_version`, trigger long running tasks on the server side. It might be beneficial to your playbook to wait for their completion in an asynchronous manner.
  As Ansible has facilities to do so, the modules will wait unconditionally. See the [Ansible documentation](https://docs.ansible.com/ansible/latest/user_guide/playbooks_async.html) for putting tasks in the background.

* `compute_resource` can leak sensitive data if used within a loop. According to [Ansible documentation](https://docs.ansible.com/ansible/latest/user_guide/playbooks_loops.html), using loop over Ansible resources can leak sensitive data. You can prevent this by using `no_log: yes` on the task.
  
  eg:
   ```yaml
   - name: Create compute resources
     compute_resource:
       server_url: https://foreman.example.com
       username: admin
       password: changeme
       validate_certs: yes
       name: "{{ item.name }}"
       organizations: "{{ item.organizations | default(omit) }}"
       locations: "{{ item.locations | default(omit) }}"
       description: "{{ item.description | default(omit) }}"
       provider: "{{ item.provider }}"
       provider_params: "{{ item.provider_params | default(omit) }}"
       state: "{{ item.state | default('present') }}"
     loop: "{{ compute_resources }}"
     no_log: yes
   ```

## Installation

There are currently two ways to use the modules in your setup: install from Ansible Galaxy or via RPM.

### Installation from Ansible Galaxy

You can install the collection from [Ansible Galaxy](https://galaxy.ansible.com/theforeman/foreman) by running `ansible-galaxy collection install theforeman.foreman` (Ansible 2.9 and later) or `mazer install theforeman.foreman` (Ansible 2.8).

After the installation, the modules are available as `theforeman.foreman.<module_name>`. Please see the [Using Ansible collections documentation](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for further details.

### Installation via RPM

The collection is also available as `ansible-collection-theforeman-foreman` from the `client` repository on `yum.theforeman.org`.

After installing the RPM, you can use the modules in the same way as when they are installed directly from Ansible Galaxy.

## Dependencies

These dependencies are required for the Ansible controller, not the Foreman server. 

* `PyYAML`
* [`apypie`](https://pypi.org/project/apypie/)
* [`ipaddress`](https://pypi.org/project/ipaddress/) for the `subnet` module on Python 2.7
* `rpm` for the RPM support in the `content_upload` module
* `debian` for the DEB support in the `content_upload` module
