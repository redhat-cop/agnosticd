apt_repositories
================

[![Build Status](https://github.com/systemli/ansible-role-apt_repositories/workflows/Integration/badge.svg?branch=main)](https://github.com/systemli/ansible-role-apt_repositories/actions?query=workflow%3AIntegration)

Add third-party repositories in Debian and derivates and pin their packages.
Follows guide from [Debian wiki](https://wiki.debian.org/DebianRepository/UseThirdParty).

It defaults to deb822, but also allows single line style ([manpage](https://manpages.debian.org/buster/apt/sources.list.5.en.html#THE_DEB_AND_DEB-SRC_TYPES:_GENERAL_FORMAT)).

Requirements
------------

Debian 9+ or Ubuntu 18.04+. Other versions of Debian/Ubuntu might be supported as well, but aren't tested.

Role Variables
--------------

```
apt_repositories:
  - url: https://...
    key: |
      -----BEGIN PGP PUBLIC KEY BLOCK-----
      MY_ARMORED_KEY
      ...
```

Further possible variables (and their defaults) are:

```
apt_repositories:
  - url: https://...
    filename: "{{ item.url|urlsplit('hostname') }}"
    types: deb
    suites: "{{ ansible_distribution_release }}"
    components: main
    packages: []
    key_path: # a file path in the role `files` dir instead of `key`
```

Furthermore, it supports `preset` values. For an example see `vars/gitlab.yml`.
Presets can be partially overridden.

Current presets:

  - caddy
  - gitlab
  - grafana
  - jitsi
  - prosody
  - sury
  - torproject

PRs welcome!

Example Playbook
----------------

```
- hosts: server
  roles:
    - systemli.apt_repositories
  vars:
    apt_repositories:
      - filename: packages.gitlab.com
        url: https://packages.gitlab.com/gitlab/gitlab-ce/debian/
        key: "{{ gitlab_ce_key }}"
        packages:
          - gitlab-ce
```

or

```
- hosts: server
  roles:
    - systemli.apt_repositories
  vars:
    apt_repositories:
      - preset: gitlab
```

or just add it as a dependency for `ansible-galaxy`:

```
# meta/main.yml
...
dependencies:
  - role: systemli.apt_repositories
    vars:
      apt_repositories:
        - filename: download.jitsi.org
          url: https://download.jitsi.org/
          key_path: jitsi-archive-keyring.gpg
          suites: stable/
          components: ''
          packages: "{{ jitsi_meet_packages }}"
```

License
-------

GPLv3

Author Information
------------------

systemli.org
