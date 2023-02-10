#!/bin/sh
OSPVERSION=17.0
OCPVERSION=v4.8.2
yum install -y podman skopeo
podman login -u='6340056|gpteosp161' -p=eyJhbGciOiJSUzUxMiJ9.eyJzdWIiOiJiMDA2ZjdkMjk3NjA0ODA3ODEyMTYxMjU1ZWMxNTBiOSJ9.h6ClBLZ4mI_QV8GNdCiKQPH4XQ_8WyQ3N7M8tuva9TipH883GH7hMSSRpvKn6Wh3YF2HSQwEJZANPjWL59oW2kzhI9QaAfmBah9sKp1Mq173lJMkYwQgtenXKLsKkAq9A2E45SFYGLikz54jPx-idG8mJCSGHfViNSXVgRppshExh_hFxPsxHQx2yEDgfJlDTeBCHhYrHjmtwHMZm9c8DAybXM1l056toMV_guBSKGNlt8d9NrIz8bG2j5ABW6olRien6GuRlr-KLsDO8MrE-7FBh6qngtI1othTF7pgYVUaWwcXmJ90oqYG3x4oQAACm4H87RmReQif_MquI-dpIA7Fs5cfkchrrSVxi1N9HgDheDtm0SeMW8uxe0jdxZMcP3vp6SCGGRevopJIcSsfW2YroOqrPnPXuQFXDqNII6x2QCNreK-icHZerCdoX2GNOsTgybiLacxLtLdWVMphNG7aILdTT7Tn6uolm28U7pm2o6Ypb3bSLOUJZ8M7hqJFYRjQDoC56_-V7qhrgFZ5dEBMn-7HMLnSUvtDiNHBUDiqKZmSUSLumea-NyHldsznwmRfdSicLMnwE5_mWuiRZNSSHUSpqg1kdcAThho-WOrSGAMj_FpkUNw-e3KGlbeYDWoe9Bauk0tvZbU2omSh88K0U8P2j6AWcfvE_uoHhac registry.redhat.io
openssl req -new -newkey rsa:4096 -nodes \
    -keyout /etc/ssl/certs/registry.key -out /etc/ssl/certs/registry.csr \
    -subj "/C=US/ST=NC/L=Raleigh/O=Red Hat/CN=192.0.2.253"
openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
    -subj "/C=US/ST=NC/L=Raleigh/O=Red Hat/CN=192.0.2.253" \
    -keyout  /etc/ssl/certs/registry.key  -out  /etc/ssl/certs/registry.crt
chcon system_u:object_r:container_file_t:s0 /etc/ssl/certs/registry*
podman run -d -p 5000:5000 --restart=always \
  -v /etc/ssl/certs:/certs:Z \
  -e REGISTRY_HTTP_ADDR=0.0.0.0:443 \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/registry.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/registry.key \
  -p 443:443 \
  --name registry registry:2
for i in `podman search --limit 1000 "registry.redhat.io/rhosp" | grep rhosp-rhel9 | awk '{ print $1 }' | grep -v beta | sed "s/registry.redhat.io\///g" | tail -n+2`; do skopeo copy --dest-tls-verify=false docker://registry.redhat.io/$i:17.0 docker://localhost:443/$i:17.0; done


for image in $(curl -s -H "Accept: application/json" https://registry.access.redhat.com/crane/repositories/v2 | jq -r 'to_entries[] | .key | select(startswith("rhceph/rhceph-5"))'); do
   echo "Synchronizing image $image"
   for tag in $(skopeo inspect docker://registry.redhat.io/$image | jq -r ".RepoTags | .[]"); do
     echo "Copying tag $image:$tag"
     skopeo copy --dest-tls-verify=false docker://registry.redhat.io/$image:$tag docker://localhost:443/$image:$tag
done
done
sync
podman stop registry
df -hT > /root/df.txt


cat>/etc/systemd/system/registry.service <<EOF
[Unit]
Description=Registry container
Wants=syslog.service

[Service]
Restart=always
ExecStart=/usr/bin/podman start -a registry
ExecStop=/usr/bin/podman stop -t 2 registry

[Install]
WantedBy=multi-user.target
EOF
systemctl enable registry
