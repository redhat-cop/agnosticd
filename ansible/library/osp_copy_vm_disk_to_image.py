# Copyright: (c) 2021, Alberto Gonzalez <alberto.gonzalez@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import datetime

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: osp_copy_vm_disk_to_image
short_description: converts a ephemeral VM disk to a image directly with Ceph
version_added: "2.7"
description:
    - this module connects to Ceph and creates an OSP image cloning the ceph image
options:
    - items: a list of dictionary (src, dest)
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
       osp_copy_vm_disk_to_image: 
         project: "{{ osp_project }}"
         ceph_cluster: "{{ ceph_cluster | default('red') }}"
         items:
           - src: myvm1
             dest: myvm1-image
           - src: myvm2
             dest: myvm2-image
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


def osp_copy_vm_disk_to_image(module):
    output_dir = module.params.get('output_dir')
    upload_element = module.params.get('type')
    elements = module.params.get('items')
    project = module.params.get("project")
    ceph_cluster = module.params.get("ceph_cluster")

    sdk, cloud = openstack_cloud_from_module(module)
    upload_objects = ""



    for element in elements:
       vm = cloud.get_server(element["src"])
       if vm.vm_state != "stopped":
          module.fail_json(msg="VM %s is not in stopped state, state is %s" % (vm.name, vm.vm_state))
       image = cloud.get_image(element["dest"])
       if image:
          module.log("Renaming image %s" % (image.name))
          d = datetime.datetime.now()
          #cloud.update_image(image.name,name="%s-%s" % (image.name, d.strftime("%Y%m%d%H%M")))
          cmd = "openstack image set --name %s-%s %s" % (image.name, d.strftime("%Y%m%d%H%M"), image.name)
          rc, out, err = module.run_command(cmd, check_rc=True)
          #module.fail_json(msg="Image %s already exists" % (image.name))

       img_id = uuid.uuid4()
       dest = "%s-images/%s" % (ceph_cluster, img_id)
       src = "%s-vms/%s_disk" % (ceph_cluster, vm.id)
       clone_vm_to_image_on_ceph(module, src, dest) 
       create_glance_image(module, element["dest"], img_id)
       update_glance_location(module, img_id)

    return 0


def clone_vm_to_image_on_ceph(module, src, dest):
     commands = []
     commands.append("rbd cp %s %s" % (src, dest))
     commands.append("rbd snap create %s@snap" % dest)
     commands.append("rbd snap protect %s@snap" % dest)
     
     for cmd in commands:  
         module.run_command(cmd, check_rc=True)

def create_glance_image(module, image_name, img_id):
    # glance image-create --disk-format raw --id $IMAGE_ID --container-format bare --name IMAGE_NAME
    # TODO: Add virtio properties to the images
    cmd = "glance image-create --disk-format raw --id {0} --container-format bare --visibility public --name '{1}' --owner admin".format(
        img_id, image_name)
    module.log("run_command: glance image-create --disk-format raw --id {0} --container-format bare --visibility public --name '{1}'".format(
            img_id, image_name))
    rc, out, err = module.run_command(cmd, check_rc=True)


def update_glance_location(module, img_id):
    #     glance --os-image-api-version 2 location-add --url "rbd://$CLUSTER_ID/$POOL/$IMAGE_ID/snap" $IMAGE_ID
    result = module.run_command("ceph fsid", check_rc=True)
    cluster_id = result[1].rstrip('\n')
    module.log("CLUSTER ID: '{}'".format(cluster_id))
    glance_pool = module.params.get("ceph_cluster") + "-images"
    cmd = "glance location-add --url \'rbd://{cluster}/{pool}/{img_id}/snap\' {img_id}".format(cluster=cluster_id,
                                                                                             pool=glance_pool,
                                                                                             img_id=img_id)
    module.log("UPDATE LOCATION: %s" % cmd)
    module.run_command(cmd, check_rc=True)


def run_module():
    module_args = dict(
        project=dict(type='str', required=True),
        ceph_cluster=dict(type='str', required=True),
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
    objects = osp_copy_vm_disk_to_image(module)

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

