Role Name
=========

This role sets the OSP all-in-one deployment. 

Requirements
------------

Requires a RHEL OS installed on the host. 

Role Variables
--------------

Some sane defaults have already been set. 
The variables used in this role are: 

- **glance_images:**		- Type: list. Format: `{name: '<NAME>', src: '<SRC_URL>', dst: '<DST_FILENAME>', flavor: '<FLAVOR>'}`
- **glance_img_destination:** 	- Type: string. Path to directory which will hold the glance images to be imported. 

Dependencies
------------

TBD

Example Playbook
----------------

TODO

License
-------

BSD

Author Information
------------------

Nenad Peric, Systems Engineering, Red Hat inc.
