# Preparation of the RHEL VM

AWS EC2 only
subscription-manager config --rhsm.manage_repos=1


https://access.redhat.com/solutions/641193
yum install libguestfs-tools-c
virt-customize -a <qcow2 image file name> --root-password password:password


sudo subscription-manager register --username jbmohr



lsblk

sudo dnf install -y lvm2

DEVICE=/dev/nvme1n1
sudo pvcreate      ${DEVICE}
sudo vgcreate rhel ${DEVICE}


sudo subscription-manager repos \
--enable rhocp-4.12-for-rhel-8-$(uname -i)-rpms \
--enable fast-datapath-for-rhel-8-$(uname -i)-rpms

sudo dnf install -y microshift
sudo dnf --showduplicates list microshift
sudo dnf install -y microshift-4.12.6-202303012057.p0.g50997a2.assembly.4.12.6.el8

scp -i ~/.ssh/opentlc_admin_backdoor.pem ~/redhat/ocp-pull-secret.json ec2-user@18.224.93.116:/tmp/openshift-pull-secret
cu
curl -o /tmp/openshift-pull-secret https://s3.ap-southeast-2.amazonaws.com/public.juliaaano/pull-secret.txt

sudo cp /tmp/openshift-pull-secret /etc/crio/openshift-pull-secret

sudo chmod 600 /etc/crio/openshift-pull-secret


sudo systemctl start microshift

sudo systemctl enable microshift


sudo dnf install -y openshift-clients

mkdir -p ~/.kube/
sudo cat /var/lib/microshift/resources/kubeadmin/kubeconfig > ~/.kube/config
chmod go-r ~/.kube/config

oc get all -A


journalctl -xu microshift


sudo subscription-manager unregister
sudo subscription-manager clean

history -c
