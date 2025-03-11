# PostgreSQL VM Build

Here are the steps performed in creating the RHEL 9 virtual machine that has PostgreSQL running as a service. For reference, the location and variable used are as follows:

```
ocp4_workload_mad_roadshow_kubevirt_psql_image_location: https://gpte-public.s3.amazonaws.com/ama_demo/postgresql-database.qcow2
```

## Prepare the RHEL 9 image

Activation key from https://console.redhat.com/insights/connector/activation-keys/rhdp-kubevirt-postgresql

```
sudo subscription-manager register --org <ORG_ID> --activationkey <ACTIVATION_KEY>
sudo dnf install postgresql-server
postgresql-setup --initdb
sudo systemctl start postgresql.service
sudo systemctl enable postgresql.service
sudo -u postgres psql postgres
  CREATE USER redhat WITH SUPERUSER PASSWORD 'redhat';
  CREATE DATABASE customers;
  \q
sudo vi /var/lib/pgsql/data/postgresql.conf
  listen_addresses = '*'
sudo vi /var/lib/pgsql/data/pg_hba.conf
  host    all             all             0.0.0.0/0               md5
  host    all             all             ::/0                    md5
sudo systemctl restart postgresql.service
history -c
```

## Test

Connect to the PostgreSQL Kubevirt VM from another container.

```
oc run psql-${RANDOM} -it --rm --image=registry.redhat.io/rhel8/postgresql-13:latest --restart=Never \
--annotations=k8s.v1.cni.cncf.io/networks='[{"name":"postgresql-net", "namespace":"default", "interface":"net1","ips":["10.10.10.40/24"]}]' \
--env="PGPASSWORD=redhat" \
-- psql -h 10.10.10.30 -U redhat customers
```

## Image size optimization

```
qemu-img convert postgresql-database.img postgresql-database.qcow2
qemu-img convert -O qcow2 postgresql-database.img postgresql-database.qcow2
```
