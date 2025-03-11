# Preparation of the RHEL VM

sudo subscription-manager register --username jbmohr

sudo dnf install -y lvm2

sudo subscription-manager repos \
--enable rhocp-4.12-for-rhel-8-$(uname -i)-rpms \
--enable fast-datapath-for-rhel-8-$(uname -i)-rpms

sudo dnf install -y microshift
sudo dnf --showduplicates list microshift
sudo dnf install -y microshift-4.12.6-202303012057.p0.g50997a2.assembly.4.12.6.el8

sudo systemctl enable microshift

sudo dnf install -y openshift-clients

sudo subscription-manager unregister
sudo subscription-manager clean

history -c

# Notes

AWS EC2 only
subscription-manager config --rhsm.manage_repos=1

https://access.redhat.com/solutions/641193
yum install libguestfs-tools-c
virt-customize -a <qcow2 image file name> --root-password password:password

lsblk
DEVICE=/dev/nvme1n1
sudo pvcreate      ${DEVICE}
sudo vgcreate rhel ${DEVICE}
sudo vgs

scp -i ~/.ssh/opentlc_admin_backdoor.pem ~/redhat/ocp-pull-secret.json ec2-user@${BASTION}:/tmp/openshift-pull-secret
sudo cp /tmp/openshift-pull-secret /etc/crio/openshift-pull-secret
sudo chmod 600 /etc/crio/openshift-pull-secret

sudo systemctl start microshift

mkdir -p ~/.kube/
sudo cat /var/lib/microshift/resources/kubeadmin/kubeconfig > ~/.kube/config
chmod go-r ~/.kube/config

oc get all -A

journalctl -xu microshift
