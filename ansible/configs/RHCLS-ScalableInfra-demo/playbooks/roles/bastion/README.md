Role for configuring Bastion hosts
=========
This role is used to configure bastion hosts for the cloud suite environments. 
More details will follow as needed.

Requirements
------------
Any pre-requisites that may not be covered by Ansible itself or the role, should/will be mentioned here. 

Role Variables
--------------
This section contains a list of variables used by the role and their defult values. 
Those which should/can be changed will be marked as such followed by a short explanation.
All these variables can be overriden anywhere, since they have the lowest priority. 

- **setup_bastion**		- Type: bool. Should be set to yes (it is needed for package setup/install)
- **bastion_packages** 		- Type: list. Contains the list of packages yum should install on the Bastion host
- **exports_url** 	 	    - Type: string, Contains the path to the 'exports' file for NFS on Bastion
- **rhel_repositories**		- Type: hash, Contains the required key-value pairs for the yum_repository module. 
- **internal_network** 		- Type: string. The IP address range in CIDR notation (eg. 192.168.1.1/24) 
- **enabled_repositories**	- Type: string. The comma-separated list of repositories to enable on the remote system.


Dependencies
------------
Depends on the following roles:
 - packages 

Example Playbook
----------------
An example of how to use the role (for instance, with variables passed in as parameters):
```yaml
    - hosts: group or hostname from inventory
      roles:
         - { role: bastion, exports_url: some_new_url }
```

A simple way calling of the role is included in the *bastion.yml* file in the tests directory. 


