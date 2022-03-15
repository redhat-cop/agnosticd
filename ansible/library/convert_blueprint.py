# Copyright: (c) 2020, Marcos Amorim <mamorim@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: convert_blueprint
short_description: manage objects in IBM Cloud Object Store using S3
version_added: "2.7"
description:
    - This module allows the user to download QCOW2 images from IBM Cloud Storage, create a new image in Ceph and 
    add the image in OpenStack Glance
options:
    TODO
extends_documentation_fragment:
    - openstack
equirements:
    - "python >= 2.7"
    - "openstacksdk"
    - "ibm-cos-sdk"
author:
    - Marcos Amorim (@marcosmamorim)
'''

EXAMPLES = '''
- name: Download images from project
  environment:
    OS_AUTH_URL: "{{ osp_auth_url }}"
    OS_USERNAME: "{{ osp_auth_username }}"
    OS_PASSWORD: "{{ osp_auth_password }}"
    OS_PROJECT_NAME: "admin"
    OS_PROJECT_DOMAIN_ID: "{{ osp_auth_project_domain }}"
    OS_USER_DOMAIN_NAME: "{{ osp_auth_user_domain }}"
    PATH: "/root/.local/bin:{{ ansible_env.PATH }}"
    CEPH_CONF: "/etc/ceph/{{ ceph_cluster |default('red') }}.conf"
  convert_blueprint:
    ibm_endpoint: "{{ ibm_endpoint }}"
    ibm_auth_endpoint: "{{ ibm_auth_endpoint }}"
    ibm_api_key: "{{ ibm_api_key }}"
    ibm_resource_id: "{{ ibm_resource_id }}"
    bucket: "{{ ibm_bucket_name }}"
    project: "{{ project }}"
    output_dir: "{{ output_dir }}"
    mode: "download"
    glance_pool: "{{ ceph_cluster |default('red') }}-images"
    overwrite: "{{ overwrite_image | default('false') }}"
'''
RETURN = '''
'''

from ansible.module_utils.basic import *
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, \
    openstack_cloud_from_module
import ibm_boto3
import os
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


def glance_image_exists(module, image_name):
    try:
        module.log("Verifying if {} exists".format(image_name))
        sdk, cloud = openstack_cloud_from_module(module)
        image = cloud.get_image(image_name)
        return image

    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


def multi_part_download(module, object, dest):
    module.log(msg="Starting download %s to %s" % (object, dest))
    if module.check_mode:
        module.exit_json(msg="PUT operation skipped - running in check mode", changed=True)

    try:
        if os.path.exists(dest):
            return True
        s3 = get_connection(module)
        bucket_name = module.params.get('bucket')
        bucket = s3.Bucket(bucket_name)
        obj = bucket.Object(object)

        file_size = module.params.get('chunk_file_size')
        threshold_file = module.params.get('threshold_file_size')

        # set 5 MB chunks
        part_size = 1024 * 1024 * file_size

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * threshold_file

        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        with open(dest, 'wb') as data:
            obj.download_fileobj(Fileobj=data, Config=transfer_config)
        module.log(msg="Transfer for {0} Complete!\n".format(dest))
        return True
    except Exception as e:
        module.exit_json(msg="Unable to complete multi-part download: {0}".format(e))


def get_image_list(module, project):
    endpoint = module.params['ibm_endpoint']
    api_key = module.params['ibm_api_key']
    auth_endpoint = module.params['ibm_auth_endpoint']
    resource_id = module.params['ibm_resource_id']
    bucket = module.params.get('bucket')
    cos = ibm_boto3.client("s3",
                           ibm_api_key_id=api_key,
                           ibm_service_instance_id=resource_id,
                           ibm_auth_endpoint=auth_endpoint,
                           config=Config(signature_version="oauth"),
                           endpoint_url=endpoint
                           )

    module.log("Getting list of images for the project {0}".format(project))
    try:
        response = cos.list_objects_v2(Bucket=bucket, Prefix=project)
        if 'Contents' in response:
            return response["Contents"]
        return []
    except Exception as e:
        module.exit_json(msg="Error get bucket content. {0}".format(e))


def check_img_ceph(module, img_id):
    glance_pool = module.params.get("glance_pool")

    cmd = 'rbd info {0}/{1}'.format(glance_pool, img_id)
    module.log("CHECK IMG: %s" % cmd)
    rc, out, err = module.run_command(cmd)
    module.log("CHECK IMG: %s - rc: %s - out: %s - %s" % (cmd, rc, out, err))

    if rc == 0:
        return True
    else:
        return False


def check_snapshot_ceph(module, img_id):
    glance_pool = module.params.get("glance_pool")

    cmd = 'rbd snap list {0}/{1}'.format(glance_pool, img_id)
    rc, out, err = module.run_command(cmd)
    module.log("CHECK SNAP: %s - rc: %s - out: %s - %s" % (cmd, rc, out, err))

    if len(out) == 0:
        return True
    else:
        return False


def convert_to_ceph(module, disk_image, img_id):
    glance_pool = module.params.get("glance_pool")

    if not check_img_ceph(module, img_id):
        module.log("Converting image to ceph")
        cmd = "qemu-img convert -f qcow2 -O raw '{0}' 'rbd:{1}/{2}'".format(disk_image, glance_pool, img_id)
        module.log(cmd)
        module.run_command(cmd, check_rc=True)

    if check_snapshot_ceph(module, img_id):
        cmd = "rbd snap create {0}/{1}@snap".format(glance_pool, img_id)
        module.log("Create snapshot {}".format(cmd))
        module.run_command(cmd, check_rc=True)

        cmd = "rbd snap protect {0}/{1}@snap".format(glance_pool, img_id)
        module.log("Protect snapshot {}".format(cmd))
        module.run_command(cmd, check_rc=True)


def create_glance_image(module, image_name, img_id):
    # glance image-create --disk-format raw --id $IMAGE_ID --container-format bare --name IMAGE_NAME
    # TODO: Add virtio properties to the images
    cmd = "glance image-create --disk-format raw --id {0} --container-format bare --visibility public --name '{1}'".format(
        img_id, image_name)
    module.log("run_command: glance image-create --disk-format raw --id {0} --container-format bare --visibility public --name '{1}'".format(
            img_id, image_name))
    rc, out, err = module.run_command(cmd, check_rc=True)


def update_glance_location(module, img_id):
    #     glance --os-image-api-version 2 location-add --url "rbd://$CLUSTER_ID/$POOL/$IMAGE_ID/snap" $IMAGE_ID
    result = module.run_command("ceph fsid", check_rc=True)
    cluster_id = result[1].rstrip('\n')
    module.log("CLUSTER ID: '{}'".format(cluster_id))
    glance_pool = module.params.get("glance_pool")
    cmd = "glance location-add --url \'rbd://{cluster}/{pool}/{img_id}/snap\' {img_id}".format(cluster=cluster_id,
                                                                                             pool=glance_pool,
                                                                                             img_id=img_id)
    module.log("UPDATE LOCATION: %s" % cmd)
    module.run_command(cmd, check_rc=True)


def convert_to_raw(module):
    output_dir = module.params.get('output_dir')
    project = module.params.get('project')
    overwrite = boolean(module.params.get('overwrite'))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_list = get_image_list(module, project)
    for img in image_list:
        image_name = img["Key"].replace('/', '-').replace('.qcow2', '')

        check_image = glance_image_exists(module, image_name)
        module.log("DEBUG check_image: %s" % check_image)
        if check_image is not None and overwrite:
            check_image = None
            module.log("DELETE IMG %s" % image_name)
            module.run_command("glance image-delete '{}'".format(image_name), check_rc=True)

        if check_image is not None and not overwrite:
            module.log("Image %s already uploaded to glance. skipping..." % image_name)
            continue

        module.log("Downloading image {} from IBM Cloud".format(image_name))
        dest_disk = "%s/%s.qcow2" % (output_dir, image_name.replace(' ', '_'))

        if not multi_part_download(module, img["Key"], dest_disk):
            module.exit_json(msg="Error download images %s to %s " % (image_name, dest_disk))

        if check_image is not None:
            img_id = check_image.get('id')
        else:
            img_id = uuid.uuid4()
            create_glance_image(module, image_name, img_id)

        convert_to_ceph(module, dest_disk, img_id)
        module.log("Remove disk %s from disk" % dest_disk )
        os.remove(dest_disk)
        update_glance_location(module, img_id)

    shutil.rmtree(output_dir)
    module.exit_json(changed=True)


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
        retries=dict(default=5, type=int)
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

    if mode == "download":
        convert_to_raw(module)

    module.exit_json(failed=False)


def main():
    run_module()


if __name__ == '__main__':
    main()
