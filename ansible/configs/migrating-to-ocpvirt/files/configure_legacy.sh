yum install -y qemu-kvm qemu-img libvirt virt-install libguestfs-tools python3-lxml python3-setuptools

systemctl enable --now libvirtd

nmcli connection down "System eth1"
nmcli connection del "System eth1"
nmcli connection add ifname br-flat type bridge con-name br-flat stp no
nmcli con add type bridge-slave ifname "eth1" master br-flat
nmcli connection modify br-flat ipv4.addresses 192.168.3.253/24 ipv4.method manual
nmcli connection up br-flat


cd /var/lib/libvirt/images/
curl -O https://www.opentlc.com/download/mig_to_ocpvirt/database.qcow2
virt-install --ram 2048 --vcpus 1 --os-variant rhel8.0 \
  --disk path=/var/lib/libvirt/images/database.qcow2,device=disk,bus=virtio,format=qcow2 \
  --import --noautoconsole --vnc \
  --network bridge=br-flat --name legacy \
  --cpu host,+vmx --boot bios.rebootTimeout=0 \
  --dry-run --print-xml > /tmp/database.xml

virsh define --file /tmp/database.xml
