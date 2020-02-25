import openstack
import os,time,sys
import json

os_username=sys.argv[2]
os_auth_url=sys.argv[1]
os_password=sys.argv[3]
os_project_name=sys.argv[4]
os_region="regionOne"

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
  if "description" in server.metadata:
    for field in server.metadata["description"].split(" "):
      if "ipmiaddr" in field:
        ipmiaddr=field.split(":")[1]
      elif "ipmipw" in field:
        ipmipw=field.split(":")[1]
    if ipmiaddr: 
      if "cdrom" in server.metadata: 
        image = conn.image.find_image(server.metadata["cdrom"])
        print("VM Name: %s IPMI IP: %s IPMI PW: %s" % (server.name, ipmiaddr, ipmipw))
        os.system("/usr/sbin/ip address add %s dev eth0" % ipmiaddr)
        print("python /usr/local/bin/openstackbmc.py --project-name=\"%s\" --vm-name=\"%s\" --auth-url=%s --address=%s --ipmi-password=%s --api-username=%s --api-password=%s --pxe-image=%s &" % (os_project_name, server.name, os_auth_url, ipmiaddr, ipmipw, os_username, os_password, image.id))
        os.system("python /usr/local/bin/openstackbmc.py --project-name=\"%s\" --vm-name=\"%s\" --auth-url=%s --address=%s --ipmi-password=%s --api-username=%s --api-password=%s --pxe-image=%s &" % (os_project_name, server.name, os_auth_url, ipmiaddr, ipmipw, os_username, os_password, image.id))
  
