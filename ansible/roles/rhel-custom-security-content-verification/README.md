## Verification playbook for configs/rhel-custom-security-content

Checks if required packages are installed, if proper directories exist and if required podman image was built.

## How to run

```
ansible-playbook -i <TARGET_HOST>, main.yml -u ec2-user
```

