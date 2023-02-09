useradd stack
echo 'r3dh4t1!' | passwd --stdin stack
echo 'stack ALL=(root) NOPASSWD:ALL' | tee -a /etc/sudoers.d/stack
chmod 0440 /etc/sudoers.d/stack
mkdir /home/stack/.ssh
cp /home/cloud-user/.ssh/authorized_keys /home/stack/.ssh/authorized_keys
chown stack:stack /home/stack/.ssh/authorized_keys
