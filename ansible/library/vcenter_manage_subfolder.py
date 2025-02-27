import requests
import urllib3
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = """
---
author: Patrick Rutledge <prutledg@redhat.com>
module: vcenter_manage_subfolder
short_description: Manage a sub folder on vcenter
description:
  - The module requires login to vcenter server
  - The module manages a parent and sub folder on mentioned vcenter server
  - The module will not create any folders with names that already exist in vcenter
  - The module will create a parent folder if it doesn't exist
  - The module will not delete the parent folder when you delete the subfolder
version_added: "1.0"
options:
  host:
    description:
      - The vcenter server on which the folder is to be managed
    required: true
  login:
    description:
      - The login name to authenticate on vcenter
    required: true
  password:
    description:
      - The password to authenticate vcenter
    required: true
  folder_name:
    description:
      - The sub folder name to manage
    required: true
  parent_folder_name:
    description:
      The name of parent folder for the sub folder being managed
    required: true
  datacenter_name:
    description:
      - The name of the datacenter where the folders are to be managed
    required: true
examples:
  - name: create a subfolder
    vcenter_manage_subfolder:
      host: "{{ server }}"
      login: "{{ login }}"
      password: "{{ password }}"
      folder_name: "{{ folder_name }}"
      parent_folder_name: "{{ parent_folder_name }}"
      datacenter_name: "{{ dc_name }}"
      state: present

  - name: create a subfolder
    vcenter_manage_subfolder:
      host: "{{ server }}"
      login: "{{ login }}"
      password: "{{ password }}"
      folder_name: "{{ folder_name }}"
      parent_folder_name: "{{ parent_folder_name }}"
      datacenter_name: "{{ dc_name }}"
      state: absent
"""

try:
    from vmware.vapi.vsphere.client import create_vsphere_client, VsphereClient

except ImportError:
    print("failed=true, msg=vmware.vapi.vsphere python module not available")
    exit(1)

from pyVim.connect import SmartConnect
from pyVmomi import vim

import requests, urllib3
import sys


def connect(
    host: str, user: str, pwd: str, insecure: bool
) -> tuple[VsphereClient, vim.ServiceInstance]:
    session = requests.session()
    if insecure:
        session.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    vsphere_client = create_vsphere_client(host, user, pwd, session=session)
    si = SmartConnect(host=host, user=user, pwd=pwd, disableSslCertValidation=insecure)
    return vsphere_client, si


def vim_moref_to_moid(moref):
    return moref._GetMoId()


def get_datacenter(module, service_instance, datacenter_name):
    content = service_instance.RetrieveContent()
    datacenters = [
        entity
        for entity in content.rootFolder.childEntity
        if hasattr(entity, "vmFolder")
    ]
    for dc in datacenters:
        if dc.name == datacenter_name:
            return dc.vmFolder


def get_folder(service_instance, dc, folder_name, parent_folder_obj):
    if not parent_folder_obj:
        parent = dc.childEntity
    else:
        parent = parent_folder_obj.childEntity
    for entity in parent:
        s = str(entity)
        if s.startswith("'vim.Folder:"):
            if folder_name == entity.name:
                return entity


def create_vm_folder(parent_folder_obj, folder_name):
    try:
        return parent_folder_obj.CreateFolder(folder_name)
    except vim.fault.DuplicateName:
        print("Folder already exists")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(requred=True),
            login=dict(required=True),
            password=dict(required=True, no_log=True),
            folder_name=dict(required=True),
            parent_folder_name=dict(required=True),
            datacenter_name=dict(required=True),
            state=dict(required=True),
        )
    )

    host = module.params.get("host")
    login = module.params.get("login")
    password = module.params.get("password")
    folder_name = module.params.get("folder_name")
    parent_folder_name = module.params.get("parent_folder_name")
    datacenter_name = module.params.get("datacenter_name")
    state = module.params.get("state")
    changed_value = False

    try:
        (vsphere_client, service_instance) = connect(
            host, login, password, insecure=True
        )
    except Exception as e:
        module.fail_json(msg="Failed to connect to %s: %s" % (host, e))

    try:
        dc = get_datacenter(module, service_instance, datacenter_name)
    except:
        module.fail_json(msg="failed to find datacenter: %s" % datacenter_name)

    try:
        parent_folder_obj = get_folder(service_instance, dc, parent_folder_name, None)
    except:
        parent_folder_obj = None

    if state == "present":
        if not parent_folder_obj:
            try:
                parent_folder_obj = create_vm_folder(dc, parent_folder_name)
            except Exception as e:
                module.fail_json(msg="failed to create root folder: %s" % e)
            changed_value = True

        try:
            folder_obj = get_folder(
                service_instance, dc, folder_name, parent_folder_obj
            )
        except:
            folder_obj = None

        if not folder_obj:
            try:
                folder = create_vm_folder(parent_folder_obj, folder_name)
            except Exception as e:
                module.fail_json(msg="failed to create folder: %s" % e)
            changed_value = True

        module.exit_json(
            changed=changed_value, folder=folder_name, parent_folder=parent_folder_name
        )

    elif state == "absent":

        if not parent_folder_obj:
            module.exit_json(
                changed=False, folder=folder_name, parent_folder=parent_folder_name
            )

        try:
            folder_obj = get_folder(
                service_instance, dc, folder_name, parent_folder_obj
            )
        except:
            module.exit_json(
                changed=False, folder=folder_name, parent_folder=parent_folder_name
            )

        if folder_obj:
            try:
                folder_obj.Destroy_Task()
            except Exception as e:
                module.fail_json(msg="failed to delete folder: %s" % e)
            changed_value = True
        else:
            changed_value = False

        module.exit_json(
            changed=changed_value, folder=folder_name, parent_folder=parent_folder_name
        )


main()
