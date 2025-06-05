#!/usr/bin/python
#
# Copyright: (c) 2020, Johnathan Kupferer <jkupfere@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: agnosticd_user_info

short_description: Display user information for agnosticd deployment and save in output directory

version_added: "2.9"

description:
- This module provides the capability of displaying user information in agnosticd processing while saving the output as a YAML in the output directory.
- Files "user-info.yaml" stores a list of messages to deliver to the environment owner and "user-data.yaml" store structured data.
- Messages and data can be stored for specific users to support multi-user environments.
- The string "user.info: " is prepended to the displayed output for compatibility with the prior practice of using the debug module with this special prefix string.

options:
  msg:
    description:
      - This is the message or data to display.
      - It should be a string.
  body:
    description:
      - Content body to accompany messages.
  data:
    description:
      - Dictionary of data to store.
      - Values may be of any type, deep data structures are discouraged.
      - Subsequent calls to agnosticd_user_info will add new keys and update existing keys.
  user:
    description:
      - User name if data or message should be set for a particular user.

author:
- Johnathan Kupferer
'''

RETURN = '''
msg:
  description: 'The message or body, prepended by "user.info" or "user.body"'
  type: str
  returned: always
error:
  description: Error message on failure
  type: str
  returned: failed
'''

# Module is implemented as an action plugin
