podman-container-systemd
========================

Role sets up container(s) to be run on host with help of systemd.
[Podman](https://podman.io/) implements container events but does not control
or keep track of the life-cycle. That's job of external tool as
[Kubernetes](https://kubernetes.io/) in clusters, and
[systemd](https://freedesktop.org/wiki/Software/systemd/) in local installs.

I wrote this role in order to help managing podman containers life-cycle on
my personal server which is not a cluster. Thus I want to use systemd for
keeping them enabled and running over reboots.

What role does:

 * installs Podman
 * pulls required images
 * on consecutive runs it pulls image again,
   and restarts container if image changed (not for pod yet)
 * creates systemd file for container or pod
 * creates kubernetes yaml for pod
 * creates volume directories for containers if they do not exist. (for pod use DirectoryOrCreate)
 * set's container or pod to be always automatically restarted if container dies.
 * makes container or pod enter run state at system boot
 * adds or removes containers exposed ports to firewall.
 * It takes parameter for running rootless containers under given user

For reference, see these two blogs about the role:
* [Automate Podman Containers with Ansible 1/2](https://redhatnordicssa.github.io/ansible-podman-containers-1)
* [Automate Podman Containers with Ansible 2/2](https://redhatnordicssa.github.io/ansible-podman-containers-2)

Blogs describe how you can single container, or several containers as one pod
using this module.

## Note for running rootless containers:

* You need to have the user created prior running this role.
* The user should have entries in /etc/sub[gu]id files for namespace range.
  If not, this role adds some variables there in order to get something going,
  but preferrably you check them.
* Some control things like memory or other resource limit's won't work as user.
* You want to increase ```systemd_TimeoutStartSec``` heavily, as we can not
  prefetch the images before systemd unit start. So systemd needs to wait
  for podman to pull images prior it starts container. Might take minutes
  depending on your network connection, and container image size.

Requirements
------------

Requires system which is capable of running podman, and that podman is found
from package repositories. Role installs podman. Role also installs firewalld
if user has defined ```container_firewall_ports``` -variable. Installs kubeval
for a pod if ```container_pod_yaml_template_validation: true```.

Role Variables
--------------

Role uses variables that are required to be passed while including it. As
there is option to run one container separately or multiple containers in pod,
note that some options apply only to other method.

- ```container_image_list``` - list of container images to run.
  If more than one image is defined, then the containers will be run in a pod.
  It is possible to define it as a dictionary to include authentication information per image, like so:
``` 
container_image_list:
  - image: docker.io/imagename
    user: exampleuser
    password: examplepw
  - image: docker.io/imagename2
```
- ```container_image_user``` - optional default username to use when authenticating
  to remote registries
- ```container_image_password``` - optional default password to use when authenticating
  to remote registries
- ```container_name``` - Identify the container in systemd and podman commands.
  Systemd service file be named container_name--container-pod.service. This can be overwritten with service_name.
- ```container_run_args``` - Anything you pass to podman, except for the name
  and image while running single container. Not used for pod.
- ```container_cmd_args``` - Any command and arguments passed to podman-run after specifying the image name. Not used for pod.
- ```container_run_as_user``` - Which user should systemd run container as.
  Defaults to root.
- ```container_run_as_group``` - Which group should systemd run container as.
  Defaults to root.
- ```container_dir_owner``` - Which owner should the volume dirs have.
  Defaults to container_run_as_user.
  If you use :U as a volume option podman will set the permissions for the user inside the container automatically.
  Quote: The :U suffix tells Podman to use the correct host UID and GID based on the UID and GID within the container, to change recursively the owner and group of the source volume. Warning use with caution since this will modify the host filesystem.
- ```container_dir_group``` - Which group should the volume dirs have.
  Defaults to container_run_as_group.
- ```container_dir_mode``` - Which permissions should the volume dirs have.
  Defaults to '0755'.
- ```container_state``` - container is installed and run if state is
  ```running```, and stopped and systemd file removed if ```absent```
- ```container_firewall_ports``` - list of ports you have exposed from container
  and want to open firewall for. When container_state is absent, firewall ports
  get closed. If you don't want firewalld installed, don't define this.
- ```systemd_TimeoutStartSec``` - how long does systemd wait for container to start?
- ```systemd_tempdir``` - Where to store conmon-pidfile and cidfile for single containers.
  Defaults to ``%T`` on systems supporting this specifier (see man 5 systemd.unit) ``/tmp``
  otherwise.
- ```service_name``` - How the systemd service files are named.
  Defaults to ```"{{ container_name }}-container-pod-{{ container_run_as_user }}.service"```.
- ```service_files_dir``` - Where to store the systemd service files.
  Defaults to ```/usr/local/lib/systemd/system``` for root and ```"{{ user_info.home }}/.config/systemd/user``` for a rootless user
- ```service_files_owner``` - Which user should own the systemd service files.
  Defaults to root.
- ```service_files_group``` - Which group should own the systemd service files.
  Defaults to root.
- ```service_files_mode``` - Which permissions should the systemd service files have.
  Defaults to 0644.
- ```container_pod_yaml``` - Path to the pod yaml file. Required for a pod.
- ```container_pod_yaml_deploy``` - Wheter to deploy the pod yaml file. Defaults to ``false``
- ```container_pod_yaml_template``` - Template to use for pod yaml deploy.
  As the template doesn't include every possible configuration option it is possible to overwrite it with your own template.
  Defaults to ``templates/container-pod-yaml.j2``.
- ```container_pod_yaml_template_validation``` - Wheter to validate the deployed pod yaml file. Defaults to ``false``.
- ```container_pod_labels``` - Defines labels for ```container_pod_yaml_deploy```.
- ```container_pod_volumes``` - Defines volumes for ```container_pod_yaml_deploy```.
- ```container_pod_containers``` - Defines containers for ```container_pod_yaml_deploy```.

This playbook doesn't have python module to parse parameters for podman command.
Until that you just need to pass all parameters as you would use podman from
command line. See ```man podman``` or
[podman tutorials](https://github.com/containers/libpod/tree/master/docs/tutorials)
for info.

If you want your
[images to be automatically updated](http://docs.podman.io/en/latest/markdown/podman-auto-update.1.html),
add this label to container_cmd_args: ```--label "io.containers.autoupdate=image"```

Never use `ansible.builtin.import_role` to execute this role if you intend to use it more
than once per playbook, or you will fall in
[this anti-pattern](https://medium.com/opsops/ansible-anti-pattern-import-role-task-with-task-level-vars-a9f5c752c9c3).

Dependencies
------------

* [containers.podman](https://galaxy.ansible.com/containers/podman) (collection)
* [ansible.posix](https://galaxy.ansible.com/ansible/posix) (collection)

Example Playbook
----------------

See the tests/main.yml for sample. In short, include role with vars.

Root container:

```
- name: tests container
  vars:
    container_image_list: 
      - sebp/lighttpd:latest
    container_name: lighttpd
    container_run_args: >-
      --rm
      -v /tmp/podman-container-systemd:/var/www/localhost/htdocs:Z,U
      --label "io.containers.autoupdate=image"
      -p 8080:80
    #container_state: absent
    container_state: running
    container_firewall_ports:
      - 8080/tcp
      - 8443/tcp
  ansible.builtin.include_role:
    name: podman-container-systemd
```

Rootless container:

```
- name: ensure user
  user:
    name: rootless_user
    comment: I run sample container

- name: tests container
  vars:
    container_run_as_user: rootless_user
    container_run_as_group: rootless_user
    container_image_list: 
      - sebp/lighttpd:latest
    container_name: lighttpd
    container_run_args: >-
      --rm
      -v /tmp/podman-container-systemd:/var/www/localhost/htdocs:Z,U
      -p 8080:80
    #container_state: absent
    container_state: running
    container_firewall_ports:
      - 8080/tcp
      - 8443/tcp
  ansible.builtin.include_role:
    name: podman-container-systemd
```

Rootless Pod:

```
- name: ensure user
  user:
    name: rootless_user
    comment: I run sample container

- name: tests pod
  vars:
    container_run_as_user: rootless_user
    container_run_as_group: rootless_user
    container_image_list:
      - sebp/lighttpd:latest
    container_name: lighttpd-pod
    container_pod_yaml: /home/rootless_user/lighttpd-pod.yml
    container_pod_yaml_deploy: true
    container_pod_yaml_template_validation: true
    container_pod_labels:
      app: "{{ container_name }}"
      io.containers.autoupdate: 'image(1)'
    container_pod_volumes:
      - name: htdocs
        hostPath:
          path: /tmp/podman-container-systemd
          type: DirectoryOrCreate
    container_pod_containers:
      - name: lighttpd
        image: sebp/lighttpd:latest
        volumeMounts:
          - name: htdocs
            mountPath: /var/www/localhost/htdocs:Z
        ports:
          - containerPort: 80
            hostPort: 8080
    container_state: running
    container_firewall_ports:
      - 8080/tcp
      - 8443/tcp
  ansible.builtin.include_role:
    name: podman-container-systemd
```

License
-------

GPLv3

Author Information
------------------

Ilkka Tengvall <ilkka.tengvall@iki.fi>
