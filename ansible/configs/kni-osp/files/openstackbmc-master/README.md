* Copy `openstackbmc.py` to `/usr/local/bin/`
* Replace `ravellobmc-wrap.bash` and `ravellobmc-wrap.py` inside `/usr/local/bin/`
* Run commands:

* `easy_install pip==8.1`
* `pip install openstacksdk==0.31.0 decorator==4.0.0`

Your IPMI VM needs to have the following metadata:

* **api_user**: an user on OSP to start/stop VM
* **api_pass**: the password for the user
* **api_url**: the OSP url (including http and v3)
* **project_name**: The name of the project
* **cdrom**: The name of the image containing `pxeboot.img` (or similar)

