Role Name
=========

host-lets-encrypt-certs-certs

Requirements
------------

EPEL needs to be installed on the target host that this role is run on.

Request Let's Encrypt Certificates for a host. Supports wildcard certificates if Cloud DNS credentials are provided.

Currently only AWS is supported for wildcard certificates. AWS credentials have to be in $HOME/.aws/credentials on the host that this role is run on.

If static certificates are requested this role needs to run on the host for which certificates are being requested. If wildcard certificates are not involved then the role *must* be run on the host that is requesting the certificates. And that host *must* respond to the DNS address the certificates are requested for. There can not be a web server running on the host that will serve the domain. Otherwise the request will fail.

If Wildcard certificates are involved the role can run on any host because validation of the domain will happen via Cloud Credentials to the Cloud Provider's DNS entry for which wildcard certificates are being requested.


Role Variables
--------------

|Variable Name|Required|Default Value|Description
|------------ |----------- |-----------|-----------
|*_certbot_domain*|Yes|"" |Domain name for which to request a certificate. _Limitation_: Curently only *one* domain name can be requested.
|*_certbot_wildcard_domain*|No|""|Wildcard domain name for which to request a certificate
|*_certbot_dns_provider*|No|route53|DNS Provider for use with wildcard certificates.
|*_certbot_le_email*|Yes|rhpds-admins@redhat.com|E-mail address to register with Let's Encrypt
|*_certbot_additional_args*|No |"" |Additional arguments for Certbot
|*_certbot_remote_dir*|Yes| "/root"| The directory on the remote host in which to store Certbot files 
|*_certbot_install_dir*|Yes| "/root/certificates"| The directory on the remote host in which to install the requested certificates into
|*_certbot_cache_archive_file*|Yes| "/tmp/certbot.tar.gz"| Local (to the host ansible is running on) cache of certificates. Prevents re-requesting certificates for later runs of the playbook when the domains haven't changed. certbot.tar.gz will contain the entire `{{_cerbot_remote_dir}}/certbot` directory so that it can be restored for future runs on new machines with the same domain names.
|*_certbot_production*|Yes|False|Use the Production Let's Encrypt Server. Leave to False for testing runs to prevent issues with the Let's Encrypt rate limits
|*_certbot_renew_automatically*|Yes|False|Install a cron job to automatically renew Certificates. Checks once a day.
|*_certbot_force_issue*|Yes|False|Force the creation of new certificates even if there are certificates already on the host or certificates in the local cache


Dependencies
------------

None

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

```
- name: Request Let's Encrypt Static Certificates
  hosts: server
  gather_facts: False
  tasks:
  - name: Call Role
    include_role:
      name: ../../roles/host-lets-encrypt-certs
    vars:
    - _certbot_domain: "master.example.opentlc.com"
    - _certbot_production: False
    - _certbot_remote_dir: "/root"
    - _certbot_cache_cert_file: "/tmp/server.cert"
    - _certbot_cache_key_file: "/tmp/server.key"
    - _certbot_cache_ca_file: "/tmp/server_ca.cer"
    - _certbot_cache_fullchain_file: "/tmp/fullchain.cer"
    - _certbot_cache_archive_file: "/tmp/acme.tar.gz"
    - _certbot_renew_automatically: False
    - _certbot_force_issue: False

- name: Request Let's Encrypt Wildcard Certificates
  hosts: quay
  gather_facts: False
  tasks:
  - name: Call Role
    include_role:
      name: ../ansible/roles/host-lets-encrypt-certs
    vars:
    - _certbot_wildcard_domain: "*.apps.example.opentlc.com"
    - _certbot_production: False
    - _certbot_remote_dir: "/root"
    - _certbot_cache_cert_file: "/tmp/server.cert"
    - _certbot_cache_key_file: "/tmp/server.key"
    - _certbot_cache_ca_file: "/tmp/server_ca.cer"
    - _certbot_cache_fullchain_file: "/tmp/fullchain.cer"
    - _certbot_cache_archive_file: "/tmp/certbot.tar.gz"
    - _certbot_renew_automatically: False
    - _certbot_force_issue: False

- name: Request Both Let's Encrypt Static and Wildcard Certificates
  hosts: quay
  gather_facts: False
  tasks:
  - name: Call Role
    include_role:
      name: ../ansible/roles/host-lets-encrypt-certs
    vars:
    - _certbot_domain: "master.example.opentlc.com"
    - _certbot_wildcard_domain: "*.apps.example.opentlc.com"
    - _certbot_production: False
    - _certbot_remote_dir: "/root"
    - _certbot_cache_cert_file: "/tmp/server.cert"
    - _certbot_cache_key_file: "/tmp/server.key"
    - _certbot_cache_ca_file: "/tmp/server_ca.cer"
    - _certbot_cache_fullchain_file: "/tmp/fullchain.cer"
    - _certbot_cache_archive_file: "/tmp/certbot.tar.gz"
    - _certbot_renew_automatically: False
    - _certbot_force_issue: False
```
