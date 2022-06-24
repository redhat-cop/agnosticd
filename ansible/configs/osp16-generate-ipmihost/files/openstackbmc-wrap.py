import openstack
import os,time,sys
import json
import socket
localip = socket.gethostbyname(socket.gethostname())


os_username=sys.argv[2]
os_auth_url=sys.argv[1]
os_password=sys.argv[3]
os_project_name=sys.argv[4]
pxe_image=sys.argv[5]
os_region="regionOne"
port=6200
def create_connection():
    return openstack.connect(
        auth=dict(
        auth_url=os_auth_url,
        project_name=os_project_name,
        username=os_username,
        password=os_password,
        project_domain_name="Default",
        user_domain_name="Default"),
        identity_api_version=3,
        region_name="regionOne"
    )

conn = create_connection()
for server in conn.compute.servers():
  ipmiaddr = ""
  ipmipw = ""
  if "ipmiaddr" in server.metadata and "ipmipw" in server.metadata:
    ipmiaddr = server.metadata["ipmiaddr"]
    ipmipw = server.metadata["ipmipw"]
  elif "description" in server.metadata:
    for field in server.metadata["description"].split(" "):
      if "ipmiaddr" in field:
        ipmiaddr=field.split(":")[1]
      elif "ipmipw" in field:
        ipmipw=field.split(":")[1]
  if ipmiaddr: 
    if pxe_image:
      image = conn.image.find_image(pxe_image)
    elif "cdrom" in server.metadata: 
      image = conn.image.find_image(server.metadata["cdrom"])
    os.system("/usr/sbin/ip address add %s dev eth0" % ipmiaddr)
    os.system("python /usr/local/bin/openstackbmc.py --project-name=\"%s\" --vm-name=\"%s\" --auth-url=%s --address=%s --ipmi-password=%s --api-username=%s --api-password=%s --pxe-image=%s --ipmi-port=623 &" % (os_project_name, server.name, os_auth_url, ipmiaddr, ipmipw, os_username, os_password, image.id))
  else:
     if "ipmimanaged" in server.metadata and server.metadata["ipmimanaged"] == "true" and "ipmipw" in server.metadata:
        ipmipw = server.metadata["ipmipw"]
        if "cdrom" in server.metadata: 
          image = conn.image.find_image(server.metadata["cdrom"])
          os.system("python /usr/local/bin/openstackbmc.py --project-name=\"%s\" --vm-name=\"%s\" --auth-url=%s --address=%s --ipmi-password=%s --api-username=%s --api-password=%s --pxe-image=%s --ipmi-port=%s &" % (os_project_name, server.name, os_auth_url, "0.0.0.0", ipmipw, os_username, os_password, image.id, port))
          conn.compute.set_server_metadata(server, ipmihost="%s:%s" % (localip, str(port)))
          port += 1
