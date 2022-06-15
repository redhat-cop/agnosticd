# Copyright: (c) 2021, Alberto Gonzalez <alberto.gonzalez@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import datetime

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: osp_upload_storage_to_ibmcloud.py
short_description: uploads OSP objects to IBM Cloud
version_added: "2.7"
description:
    - Upload the images/VMs/volumes to IBMCLOUD directly from Ceph
options:
    - type: vms/volumes/images
    - items: a list dictionary (src/dest) with the source and destination
extends_documentation_fragment:
    - openstack
equirements:
    - "python >= 2.7"
    - "openstacksdk"
    - "ibm-cos-sdk"
author:
    - Alberto Gonzalez
'''

EXAMPLES = '''
   - name: Upload vms from project
     become: true
     register: upload_objects
     environment:
       OS_AUTH_URL: "{{ osp_auth_url }}"
       OS_USERNAME: "{{ osp_auth_username }}"
       OS_PASSWORD: "{{ osp_auth_password }}"
       OS_PROJECT_NAME: "{{ osp_project | default('admin') }}"
       OS_PROJECT_DOMAIN_ID: "{{ osp_auth_project_domain }}"
       OS_USER_DOMAIN_NAME: "{{ osp_auth_user_domain }}"
       OS_INTERFACE: "{{ osp_interface | default('internal') }}"
       PATH: "/root/.local/bin:{{ ansible_env.PATH }}"
       CEPH_CONF: "/etc/ceph/{{ ceph_cluster | default('red') }}.conf"
     osp_upload_storage_to_ibmcloud:
       ibm_endpoint: "{{ ibm_endpoint }}"
       ibm_auth_endpoint: "{{ ibm_auth_endpoint }}"
       ibm_api_key: "{{ ibm_api_key }}"
       ibm_resource_id: "{{ ibm_resource_id }}"
       bucket: "{{ ibm_bucket_name }}"
       project: "{{ image_store }}"
       output_dir: "{{ output_dir }}"
       glance_pool: "{{ ceph_cluster | default('red') }}-{{ type }}"
       overwrite: "{{ overwrite_image | default('false') }}"
       type: "vms"
       items: 
         - src: 3compute01
           dest: 3compute01-root-162.qcow2
         - src: 3compute02
           dest: 3compute02-root-162.qcow2
         - src: 2ctrl01
           dest: 2ctrl01-root-162.qcow2

'''
RETURN = '''
'''

from ansible.module_utils.basic import *
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import \
    openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module
import ibm_boto3
import os,time
from ibm_botocore.client import Config, ClientError
import uuid
import shutil

try:
    import botocore
except ImportError:
    pass  # will be detected by imported AnsibleAWSModule


def get_connection(module):
    endpoint = module.params['ibm_endpoint']
    api_key = module.params['ibm_api_key']
    auth_endpoint = module.params['ibm_auth_endpoint']
    resource_id = module.params['ibm_resource_id']

    cos = ibm_boto3.resource("s3",
                             ibm_api_key_id=api_key,
                             ibm_service_instance_id=resource_id,
                             ibm_auth_endpoint=auth_endpoint,
                             config=Config(signature_version="oauth"),
                             endpoint_url=endpoint
                             )
    return cos


def osp_upload_storage_to_ibmcloud(module):
    output_dir = module.params.get('output_dir')
    upload_element = module.params.get('type')
    elements = module.params.get('items')
    project = module.params.get("project")
    glance_pool = module.params.get("glance_pool")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    sdk, cloud = openstack_cloud_from_module(module)
    upload_objects = ""



    if upload_element == "vms":
        for element in elements:
            vm = cloud.get_server(element["src"])
            if vm.vm_state != "stopped":
                 module.fail_json(msg="VM %s is not in stopped state, state is %s" % (vm.name, vm.vm_state))
            dest_disk = "%s/%s" % (output_dir, element["dest"])
            src = "rbd:%s/%s_disk" % (glance_pool, vm.id)
            upload_objects += check_convert_and_upload_object(module, src, element, dest_disk) + "\n"

    elif upload_element == "volumes":
        for element in elements:
            volume = cloud.get_volume(element["src"])
            if volume["attachments"]:
                vm = cloud.get_server(volume["attachments"][0]["server_id"])
                if vm.vm_state != "stopped":
                    module.fail_json(msg="VM %s is not in stopped state, state is %s" % (vm.name, vm.vm_state))
            dest_disk = "%s/%s" % (output_dir, element["src"])
            src = "rbd:%s/volume-%s" % (glance_pool, volume.id)
            upload_objects += check_convert_and_upload_object(module, src, element, dest_disk) + "\n"

    elif upload_element == "images":
        for element in elements:
            image = cloud.get_image(element["src"])
            dest_disk = "%s/%s" % (output_dir, element["dest"])
            src = "rbd:%s/%s" % (glance_pool, image.id)
            upload_objects += check_convert_and_upload_object(module, src, element, dest_disk) + "\n"

    return upload_objects


def check_convert_and_upload_object(module, src, element, dest_disk):
     project = module.params.get("project")
     bucket_name = module.params.get('bucket')
     s3 = get_connection(module)
     try:
         object_key = "%s/%s" % (project, element["dest"])
         s3.meta.client.head_object(Bucket=bucket_name,Key=object_key)
         module.fail_json(msg="Object %s/%s on IBM Cloud exists" % (project,element["dest"]))
       
     except ClientError:
         cmd = "qemu-img convert -O qcow2 %s %s" % (src, dest_disk)
         module.run_command(cmd, check_rc=True)
         s3.meta.client.upload_file(dest_disk, bucket_name, "%s/%s" % (project, element["dest"]))
         os.remove(dest_disk)
         return "%s/%s" % (project, element["dest"])



def run_module():
    module_args = dict(
        ibm_endpoint=dict(type='str', required=True),
        ibm_api_key=dict(type='str', required=True, no_log=True),
        ibm_auth_endpoint=dict(type='str', default='https://iam.cloud.ibm.com/identity/token'),
        ibm_resource_id=dict(type='str', required=True),
        project=dict(type='str', required=True),
        bucket=dict(required=True),
        mode=dict(choices=['upload', 'download'], default='download'),
        output_dir=dict(default="/images/import"),
        glance_pool=dict(required=True),
        overwrite=dict(aliases=['force'], default=False, choices=BOOLEANS),
        chunk_file_size=dict(default=5, type='int'),
        threshold_file_size=dict(default=15, type='int'),
        retries=dict(default=5, type=int),
        type=dict(default="vms"),
        items=dict(default=[], type=list),
    )

    argument_spec = openstack_full_argument_spec(
        image=dict(required=False),
    )
    module_args.update(argument_spec)
    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(module_args, **module_kwargs)

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(msg="Operation skipped - running in check mode", changed=True)

    mode = module.params.get("mode")
    objects = osp_upload_storage_to_ibmcloud(module)

    result = dict(
        changed=True,
        failed=False,
        objects=objects
    )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

