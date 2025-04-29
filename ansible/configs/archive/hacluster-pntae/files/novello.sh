#!/bin/bash
for file in "openstackbmc.py" "openstackbmc-wrap.bash" "openstackbmc-wrap.py"; do
	curl -L -o /usr/local/bin/${file} https://www.opentlc.com/download/novello/openstackbmc/${file}
done

curl -L -o /etc/systemd/system/openstackbmc.service https://www.opentlc.com/download/novello/openstackbmc/openstackbmc.service

if ! which python; then
   ln -s /usr/bin/python2 /usr/bin/python
   ln -s /usr/bin/easy_install-2.7 /usr/bin/easy_install
fi
easy_install pip==8.1
/bin/pip2.7 install openstacksdk==0.31.0 decorator==4.0.0 stevedore==1.32.0 dogpile.cache==0.9.2 pyghmi==1.5.15
rm /etc/systemd/system/ravellobmc.service /etc/systemd/system/multi-user.target.wants/ravellobmc.service
chmod u+x /usr/local/bin/openstackbmc-wrap.bash


systemctl enable openstackbmc.service
systemctl start openstackbmc.service

