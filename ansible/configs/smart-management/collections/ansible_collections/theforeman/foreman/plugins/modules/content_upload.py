#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2016, Eric D Helms <ericdhelms@gmail.com>
# (c) 2018, Sean O'Keeffe <seanokeeffe797@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: content_upload
version_added: 1.0.0
short_description: Upload content to a repository
description:
  - Allows the upload of content to a repository
author: "Eric D Helms (@ehelms)"
requirements:
  - python-debian (For deb Package upload)
  - rpm (For rpm upload)
options:
  src:
    description:
      - File to upload
    required: true
    type: path
    aliases:
      - file
  repository:
    description:
      - Repository to upload file in to
    required: true
    type: str
  product:
    description:
      - Product to which the repository lives in
    required: true
    type: str
notes:
  - Currently only uploading to deb, RPM & file repositories is supported
  - For anything but file repositories, a supporting library must be installed. See Requirements.
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Upload my.rpm"
  theforeman.foreman.content_upload:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    src: "my.rpm"
    repository: "Build RPMs"
    product: "My Product"
    organization: "Default Organization"
'''

RETURN = ''' # '''

import os
import traceback

from ansible.module_utils._text import to_bytes
from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloAnsibleModule, missing_required_lib

try:
    from debian import debfile
    HAS_DEBFILE = True
except ImportError:
    HAS_DEBFILE = False
    DEBFILE_IMP_ERR = traceback.format_exc()

try:
    import rpm
    HAS_RPM = True
except ImportError:
    HAS_RPM = False
    RPM_IMP_ERR = traceback.format_exc()

CONTENT_CHUNK_SIZE = 2 * 1024 * 1024


def get_deb_info(path):
    control = debfile.DebFile(path).debcontrol()
    return control['package'], control['version'], control['architecture']


def get_rpm_info(path):
    ts = rpm.TransactionSet()

    # disable signature checks, we might not have the key or the file might be unsigned
    # pre 4.15 RPM needs to use the old name of the bitmask
    try:
        vsflags = rpm.RPMVSF_MASK_NOSIGNATURES
    except AttributeError:
        vsflags = rpm._RPMVSF_NOSIGNATURES
    ts.setVSFlags(vsflags)

    with open(path) as rpmfile:
        rpmhdr = ts.hdrFromFdno(rpmfile)

    name = rpmhdr[rpm.RPMTAG_NAME].decode('ascii')
    epoch = rpmhdr[rpm.RPMTAG_EPOCHNUM]
    version = rpmhdr[rpm.RPMTAG_VERSION].decode('ascii')
    release = rpmhdr[rpm.RPMTAG_RELEASE].decode('ascii')
    arch = rpmhdr[rpm.RPMTAG_ARCH].decode('ascii')

    return (name, epoch, version, release, arch)


def main():
    module = KatelloAnsibleModule(
        foreman_spec=dict(
            src=dict(required=True, type='path', aliases=['file']),
            repository=dict(required=True, type='entity', scope=['product'], thin=False),
            product=dict(required=True, type='entity', scope=['organization']),
        ),
    )

    with module.api_connection():
        repository_scope = module.scope_for('repository')

        b_src = to_bytes(module.foreman_params['src'])
        filename = os.path.basename(module.foreman_params['src'])

        checksum = module.sha256(module.foreman_params['src'])

        content_unit = None
        if module.foreman_params['repository']['content_type'] == 'deb':
            if not HAS_DEBFILE:
                module.fail_json(msg=missing_required_lib("python-debian"), exception=DEBFILE_IMP_ERR)

            name, version, architecture = get_deb_info(b_src)
            query = 'name = "{0}" and version = "{1}" and architecture = "{2}"'.format(name, version, architecture)
            content_unit = module.find_resource('debs', query, params=repository_scope, failsafe=True)
        elif module.foreman_params['repository']['content_type'] == 'yum':
            if not HAS_RPM:
                module.fail_json(msg=missing_required_lib("rpm"), exception=RPM_IMP_ERR)

            name, epoch, version, release, arch = get_rpm_info(b_src)
            query = 'name = "{0}" and epoch = "{1}" and version = "{2}" and release = "{3}" and arch = "{4}"'.format(name, epoch, version, release, arch)
            content_unit = module.find_resource('packages', query, params=repository_scope, failsafe=True)
        elif module.foreman_params['repository']['content_type'] == 'file':
            query = 'name = "{0}" and checksum = "{1}"'.format(filename, checksum)
            content_unit = module.find_resource('file_units', query, params=repository_scope, failsafe=True)
        else:
            # possible types in 3.12: docker, ostree, yum, puppet, file, deb
            module.fail_json(msg="Uploading to a {0} repository is not supported yet.".format(module.foreman_params['repository']['content_type']))

        if not content_unit:
            if not module.check_mode:
                size = os.stat(module.foreman_params['src']).st_size
                content_upload_payload = {'size': size}
                content_upload_payload.update(repository_scope)
                content_upload = module.resource_action('content_uploads', 'create', content_upload_payload)
                content_upload_scope = {'id': content_upload['upload_id']}
                content_upload_scope.update(repository_scope)

                offset = 0

                with open(b_src, 'rb') as contentfile:
                    for chunk in iter(lambda: contentfile.read(CONTENT_CHUNK_SIZE), b""):
                        data = {'content': chunk, 'offset': offset, 'size': len(chunk)}
                        module.resource_action('content_uploads', 'update', params=content_upload_scope, data=data)

                        offset += len(chunk)

                uploads = [{'id': content_upload['upload_id'], 'name': filename,
                            'size': offset, 'checksum': checksum}]
                import_params = {'id': module.foreman_params['repository']['id'], 'uploads': uploads}
                module.resource_action('repositories', 'import_uploads', import_params)

                module.resource_action('content_uploads', 'destroy', content_upload_scope)
            else:
                module.set_changed()


if __name__ == '__main__':
    main()
