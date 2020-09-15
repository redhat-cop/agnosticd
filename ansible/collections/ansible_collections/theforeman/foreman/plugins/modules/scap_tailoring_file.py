#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2020 Evgeni Golov <evgeni@golov.de>
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
module: scap_tailoring_file
version_added: 1.0.0
short_description: Manage SCAP Tailoring Files
description:
  - Create, update, and delete SCAP Tailoring Files
author:
  - "Evgeni Golov (@evgeni)"
options:
  name:
    description:
      - Name of the tailoring file.
    required: true
    type: str
  updated_name:
    description:
      - New name of the tailoring file.
      - When this parameter is set, the module will not be idempotent.
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
  - theforeman.foreman.foreman.scap_datastream
'''

EXAMPLES = '''
- name: Create SCAP tailoring file
  theforeman.foreman.scap_tailoring_file:
    name: "Red Hat firefox default content"
    scap_file: "/home/user/Downloads/ssg-firefox-ds-tailoring.xml"
    original_filename: "ssg-firefox-ds-tailoring.xml"
    organizations:
      - "Default Organization"
    locations:
      - "Default Location"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: Update SCAP tailoring file
  theforeman.foreman.scap_tailoring_file:
    name: "Red Hat firefox default content"
    updated_name: "Updated tailoring file name"
    scap_file: "/home/user/Downloads/updated-ssg-firefox-ds-tailoring.xml"
    original_filename: "updated-ssg-firefox-ds-tailoring.xml"
    organizations:
      - "Org One"
      - "Org Two"
    locations:
      - "Loc One"
      - "Loc Two"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: Delete SCAP tailoring file
  theforeman.foreman.scap_tailoring_file:
    name: "Red Hat firefox default content"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: absent
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    scap_tailoring_files:
      description: List of scap tailoring files.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanScapDataStreamModule


class ForemanTailoringFileModule(ForemanScapDataStreamModule):
    pass


def main():
    module = ForemanTailoringFileModule(
        argument_spec=dict(
            updated_name=dict(type='str'),
        ),
        foreman_spec=dict(
            name=dict(type='str', required=True),
        ),
        required_plugins=[('openscap', ['*'])],
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
