Role Name
=========

host-lets-encrypt-certs

Requirements
------------

Request Let's Encrypt Certificates for a host. Supports Wildcard certificates of AWS Credentials are provided.

If static certificates are requested this role needs to run on the host for which certificates are being requested. If wildcard certificates are not involved then the role *must* be run on the host that is requesting the certificates. And that host *must* respond to the DNS address the certificates are requested for. There can not be a web server running on the host that will serve the domain. Otherwise the request will fail.

If Wildcard certificates are involved the role can run on any (AWS) host because validation of the domain will happen via AWS Access Credentials to the Route53 entry for which wildcard certificates are being requested.


Role Variables
--------------

|Variable Name|Required|Default Value|Description
|------------ |----------- |-----------|-----------
|*acme_domain*|Yes|"" |Domain name for which to request a certificate. _Limitation_: Curently only *one* domain name can be requested.
|*acme_wildcard_domain*|No|""|Wildcard domain name for which to request a certificate
|*acme_aws_access_key*|No |"" |AWS Access Key for Route53 (Only for Wildcard Domains)
|*acme_aws_secret_access_key*|No| "" |AWS Secret Access Key for Route53  (Only for Wildcard Domains)
|*acme_additional_args*|No |"" |Additional arguments for the Acme script
|*acme_remote_dir*|Yes| "/root"| The directoroy on the remote host in which to install acme.sh
|*acme_install_dir*|Yes| "/root/certificates"| The directory on the remote host in which to install the requested certificates into
|*acme_cache_cert_file*|Yes| "/tmp/ssl.cert"| Local Cache File for Certificate
|*acme_cache_key_file*|Yes| "/tmp/ssl.key"|Local Cache File for Key
|*acme_cache_ca_file*|Yes| "/tmp/ssl_ca.cer"|Local Cache File for CA Certificate
|*acme_cache_fullchain_file*|Yes| "/tmp/fullchain.cer"|Local Cache File for the Fullchain Certificate
|*acme_cache_archive_file*|Yes| "/tmp/acme.tar.gz"| Local (to the host ansible is running on) cache of certificates. Prevents re-requesting certificates for later runs of the playbook when the domains haven't changed. acme.tar.gz will contain the entire .acme.sh directory so that it can be restored for future runs on new machines with the same domain names.
|*acme_production*|Yes|False|Use the Production Let's Encrypt Server. Leave to False for testing runs to prevent issues with the Let's Encrypt rate limits
|*acme_renew_automatically*|Yes|False|Install a cron job to automatically renew Certificates. Checks once a day.
|*acme_force_issue*|Yes|False|Force the creation of new certificates even if there are certificates already on the host or certificates in the local cache


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
    - acme_domain: "master.example.opentlc.com"
    - acme_production: False
    - acme_remote_dir: "/root"
    - acme_cache_cert_file: "/tmp/server.cert"
    - acme_cache_key_file: "/tmp/server.key"
    - acme_cache_ca_file: "/tmp/server_ca.cer"
    - acme_cache_fullchain_file: "/tmp/fullchain.cer"
    - acme_cache_archive_file: "/tmp/acme.tar.gz"
    - acme_renew_automatically: False
    - acme_force_issue: False

- name: Request Let's Encrypt Wildcard Certificates
  hosts: quay
  gather_facts: False
  tasks:
  - name: Call Role
    include_role:
      name: ../ansible/roles/host-lets-encrypt-certs
    vars:
    - acme_wildcard_domain: "*.apps.example.opentlc.com"
    - acme_aws_access_key: "<AWS ACCESS KEY>"
    - acme_aws_secret_access_key: "<AWS_SECRET_ACCESS_KEY>"
    - acme_production: False
    - acme_remote_dir: "/root"
    - acme_cache_cert_file: "/tmp/server.cert"
    - acme_cache_key_file: "/tmp/server.key"
    - acme_cache_ca_file: "/tmp/server_ca.cer"
    - acme_cache_fullchain_file: "/tmp/fullchain.cer"
    - acme_cache_archive_file: "/tmp/acme.tar.gz"
    - acme_renew_automatically: False
    - acme_force_issue: False

- name: Request Both Let's Encrypt Static and Wildcard Certificates
  hosts: quay
  gather_facts: False
  tasks:
  - name: Call Role
    include_role:
      name: ../ansible/roles/host-lets-encrypt-certs
    vars:
    - acme_domain: "master.example.opentlc.com"
    - acme_wildcard_domain: "*.apps.example.opentlc.com"
    - acme_aws_access_key: "<AWS ACCESS KEY>"
    - acme_aws_secret_access_key: "<AWS_SECRET_ACCESS_KEY>"
    - acme_production: False
    - acme_remote_dir: "/root"
    - acme_cache_cert_file: "/tmp/server.cert"
    - acme_cache_key_file: "/tmp/server.key"
    - acme_cache_ca_file: "/tmp/server_ca.cer"
    - acme_cache_fullchain_file: "/tmp/fullchain.cer"
    - acme_cache_archive_file: "/tmp/acme.tar.gz"
    - acme_renew_automatically: False
    - acme_force_issue: False
```
