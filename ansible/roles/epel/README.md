<p align="right">
    <a href="https://travis-ci.org/epiloque/ansible-epel">
        <img src="https://travis-ci.org/epiloque/ansible-epel.svg?branch=master"
             alt="build status">
    </a>
        <a href="https://galaxy.ansible.com/epiloque/epel">
        <img src="https://img.shields.io/badge/ansible--galaxy-epel-blue.svg"
             alt="ansible galaxy">
    </a>
</p>

epel role

## Role Variables

Available variables are listed below, along with default values:

```yaml
epel_url: https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
```


## Example Playbook

```yaml
- hosts: servers
  roles:
    - epiloque.epel
```

## License

BSD
