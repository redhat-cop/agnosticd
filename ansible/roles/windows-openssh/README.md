windows-openssh
===============

This ansible role helps to install and configure OpenSSH server on Windows hosts. It deploys the [official OpenSSH
port for Windows by Microsoft](https://github.com/PowerShell/Win32-OpenSSH).

Requirements
------------

This role requires Ansible 2.0 or higher, and will only work against Windows 7 or higher hosts.

Role Variables
--------------

The variables that can be passed to this role and a brief description about them are as follows:

```yaml
openssh_download_url: "https://github.com/PowerShell/Win32-OpenSSH/releases/download/2_25_2016/OpenSSH-Win64.zip"
openssh_temporary_dir: "C:\\Temp"      # Where to download the archive. If you change it make sure it exists
openssh_archive_name: "OpenSSH-Win64"  # Name of the root folder contained in the archive
openssh_extract_dir: "C:\\OpenSSH"     # Where to extract the archive


### SSHD config file variables ###
openssh_sshd_ports: 
  - 22
openssh_sshd_listen_addresses: 
  - "0.0.0.0"
  - "::"
openssh_sshd_protocol: 2
openssh_sshd_host_keys:
  - \\ssh_host_rsa_key
  - \\ssh_host_dsa_key
  - \\ssh_host_ecdsa_key

openssh_sshd_syslog_facility: AUTH
openssh_sshd_log_level: INFO

openssh_sshd_login_grace_time: "2m"
openssh_sshd_permit_root_login: True
openssh_sshd_strict_modes: True
openssh_sshd_max_auth_tries: 6
openssh_sshd_max_sessions: 10
openssh_sshd_rsa_authentication: True
openssh_sshd_pubkey_authentication: True

openssh_sshd_authorized_keys_file: ".ssh/authorized_keys"
openssh_sshd_rhosts_rsa_authentication: False
openssh_sshd_host_based_authentication: False
openssh_sshd_ignore_user_known_hosts: False
openssh_sshd_ignore_rhosts: True

openssh_sshd_password_authentication: True
openssh_sshd_permit_empty_passwords: False
openssh_sshd_challenge_response_authentication: True

openssh_sshd_allow_agent_forwarding: True
openssh_sshd_allow_tcp_forwarding: True
openssh_sshd_gateway_ports: False
openssh_sshd_x11_forwarding: False
openssh_sshd_x11_display_offset: 10
openssh_sshd_x11_use_localhost: True
openssh_sshd_print_motd: True
openssh_sshd_print_last_log: True
openssh_sshd_tcp_keep_alive: True
openssh_sshd_use_login: False
openssh_sshd_use_privilege_separation: True
openssh_sshd_permit_user_environment: False
openssh_sshd_compression: delayed
openssh_sshd_client_alive_interval: 0
openssh_sshd_client_alive_count_max: 3
openssh_sshd_use_dns: True
openssh_sshd_pid_file: /var/run/sshd.pid
openssh_sshd_max_startups: 10
openssh_sshd_permit_tunnel: False
openssh_sshd_chroot_directory: none

openssh_sshd_banner: none

openssh_sshd_banner: none

openssh_sshd_subsystems:
  sftp: /win32openssh/bin/sftp-server.exe
  scp: /win32openssh/bin/scp.exe
```

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: mywindowshost
      roles:
         - { role: windows-openssh, openssh_sshd_port: 4242 }

License
-------

The MIT License (MIT)

Copyright (c) 2016 Ableton AG, Berlin.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Author Information
------------------

[Theo Crevon](https://github.com/tcr-ableton)

Maintainers
-----------

* [tcr-ableton](https://github.com/tcr-ableton)
