awx_pod
=======

This Ansible role sets up Ansible AWX server using containers. It uses podman
to do it.

See this blog how to use it: https://redhatnordicssa.github.io/ansible-podman-containers-2

![awx-pod](https://redhatnordicssa.github.io/assets/images/awx-pod.png)

Requirements
------------

Role is tested on Fedora server.

Role Variables
--------------

Set AWX credentials and storage paths is ```defaults/main.yml``` file.

Dependencies
------------

Role depends on
[ikke_t.podman_container_systemd](https://galaxy.ansible.com/ikke_t/podman_container_systemd)
role.


Example Playbook
----------------

```
- name: run AWX on host
  hosts: all
  tasks:
    - name: import awx_pod role to install it all
      vars:
        admin_user: admin
        admin_password: foobar
        awx_podman_dir: /tmp
        awx_host_port: 8052
        container_state: running
      import_role:
        name: awx_pod
```

License
-------

GPLv3

Author Information
------------------

Ilkka Tengval
