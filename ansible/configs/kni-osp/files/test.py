import openstack
import os,time
import json
#from openstack.config import loader
#config = loader.OpenStackConfig()
#cloud = openstack.connect(cloud=openstack)
os_username="admin"
os_auth_url="http://169.45.205.100:5000/v3"
os_password="2RkTeNFMmJzGli68NU3BXhsLX"
os_project_name="ospadbasic"
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
        print("VM Name: %s IPMI IP: %s IPMI PW: %s" % (server.name, ipmiaddr, ipmipw))
       os.system("/usr/sbin/ip address add %s dev eth0" % ipmiaddr)
      os.system("/usr/local/bin/openstackbmc.py --project-name=\"%s\" --vm-name=\"%s\" --auth-url=%s --address=%s --ipmi-password=%s --api-username=%s --api-password=%s &" % (os_project_name, server.name, os_auth_url, ipmiaddr, ipmipw, os_username, os_password))
