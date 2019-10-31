# Scripts for Migration Demos in RHTE 2019 Labs

## Applying CORS Settings

Login to the bastion host using the information available in your lab console : 

```bash
ssh <your_lab_user>@bastion.<guid_of_ocp3>.<domain>
```

The `cors.yaml` playbook is available in the home directory on bastion host.

To apply CORS settings on your OCP3 cluster : 

```bash
GUID_4=<guid_of_ocp4> DOMAIN=<domain_of_ocp4_lab> ansible-playbook cors.yaml
```

Example usage :

```bash
GUID_4=09kt DOMAIN=events.opentlc.com ansible-playbook cors.yaml
```
