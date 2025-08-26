
service_vm_jupyter_lab
=========

This role installs and configures JupyterLab with SSL certificates on a service VM.

The role:
- Installs Certbot and obtains SSL certificates
- Configures JupyterLab with SSL and security settings
- Sets up JupyterLab as a systemd service
- Configures CORS and iframe embedding support

Requirements
------------

- RHEL/CentOS/Fedora system
- Python virtual environment with JupyterLab installed
- DNS record pointing to the server

Role Variables
--------------

Required variables:
```
    service_vm_jupyter_lab_domain_name: Domain name for JupyterLab (default: "bastion.{{ guid }}{{ subdomain_base_suffix }}")
    service_vm_jupyter_lab_jupyter_user: Linux user to run JupyterLab (default: "{{ student_name }}")
    service_vm_jupyter_lab_certbot_email: Email for Let's Encrypt notifications
```

Optional variables:
```
    service_vm_jupyter_lab_jupyter_group: Linux group for JupyterLab user (default: "users")
    service_vm_jupyter_lab_jupyter_directory: Working directory for JupyterLab (default: "/home/{{ student_name }}/lab")
    service_vm_jupyter_lab_jupyter_ssl_dir: Directory for SSL certificates (default: "/home/{{ service_vm_lab_juypter_user }}/.jupyter/ssl")
    service_vm_jupyter_lab_jupyter_port: Port for JupyterLab (default: 9443)
    service_vm_jupyter_lab_jupyter_theme: JupyterLab theme (default: 'JupyterLab Dark')
```

Dependencies
------------

None

Example Playbook
----------------
```
- hosts: jupyter_servers
  roles:
    - role: service_vm_jupyter_lab
      vars:
        service_vm_jupyter_lab_domain_name: "jupyter.example.com"
        service_vm_jupyter_lab_jupyter_user: "jupyter"
        service_vm_jupyter_lab_certbot_email: "admin@example.com"
        service_vm_jupyter_lab_jupyter_port: 8888
```