# (c) 2019, Evgeni Golov <evgeni@redhat.com>
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
#

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):

    # Foreman documentation fragment
    DOCUMENTATION = '''
requirements:
  - apypie
options:
  server_url:
    description: URL of the Foreman server
    required: true
    type: str
  username:
    description: Username accessing the Foreman server
    required: true
    type: str
  password:
    description: Password of the user accessing the Foreman server
    required: true
    type: str
  validate_certs:
    description: Whether or not to verify the TLS certificates of the Foreman server
    default: true
    type: bool
'''

    NESTED_PARAMETERS = '''
options:
  parameters:
    description:
      - Entity domain specific host parameters
    required: false
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Name of the parameter
        required: true
        type: str
      value:
        description:
          - Value of the parameter
        required: true
        type: raw
      parameter_type:
        description:
          - Type of the parameter
        default: 'string'
        choices:
          - 'string'
          - 'boolean'
          - 'integer'
          - 'real'
          - 'array'
          - 'hash'
          - 'yaml'
          - 'json'
        type: str
'''

    OS_FAMILY = '''
options:
  os_family:
    description:
      - The OS family the entity shall be assigned with.
    required: false
    choices:
      - AIX
      - Altlinux
      - Archlinux
      - Coreos
      - Debian
      - Freebsd
      - Gentoo
      - Junos
      - NXOS
      - Rancheros
      - Redhat
      - Solaris
      - Suse
      - Windows
      - Xenserver
    type: str
'''

    TAXONOMY = '''
options:
  organizations:
    description: List of organizations the entity should be assigned to
    type: list
    elements: str
  locations:
    description: List of locations the entity should be assigned to
    type: list
    elements: str
'''

    ENTITY_STATE = '''
options:
  state:
    description:
      - State of the entity
    default: present
    choices:
      - present
      - absent
    type: str
'''

    ENTITY_STATE_WITH_DEFAULTS = '''
options:
  state:
    description:
      - State of the entity
      - C(present_with_defaults) will ensure the entity exists, but won't update existing ones
    default: present
    choices:
      - present
      - present_with_defaults
      - absent
    type: str
'''

    HOST_OPTIONS = '''
options:
  compute_resource:
    description: Compute resource name
    required: false
    type: str
  compute_profile:
    description: Compute profile name
    required: false
    type: str
  domain:
    description: Domain name
    required: false
    type: str
  subnet:
    description: IPv4 Subnet name
    required: false
    type: str
  subnet6:
    description: IPv6 Subnet name
    required: false
    type: str
  root_pass:
    description:
      - Root password.
      - Will result in the entity always being updated, as the current password cannot be retrieved.
    type: str
    required: false
  realm:
    description: Realm name
    required: false
    type: str
  architecture:
    description: Architecture name
    required: False
    type: str
  medium:
    aliases: [ media ]
    description:
      - Medium name
      - Mutually exclusive with I(kickstart_repository).
    required: False
    type: str
  operatingsystem:
    description: Operatingsystem title
    required: False
    type: str
  pxe_loader:
    description: PXE Bootloader
    required: false
    choices:
      - PXELinux BIOS
      - PXELinux UEFI
      - Grub UEFI
      - Grub2 BIOS
      - Grub2 ELF
      - Grub2 UEFI
      - Grub2 UEFI SecureBoot
      - Grub2 UEFI HTTP
      - Grub2 UEFI HTTPS
      - Grub2 UEFI HTTPS SecureBoot
      - iPXE Embedded
      - iPXE UEFI HTTP
      - iPXE Chain BIOS
      - iPXE Chain UEFI
    type: str
  ptable:
    description: Partition table name
    required: False
    type: str
  environment:
    description: Puppet environment name
    required: false
    type: str
  puppetclasses:
    description: List of puppet classes to include in this host group. Must exist for hostgroup's puppet environment.
    required: false
    type: list
    elements: str
  config_groups:
    description: Config groups list
    required: false
    type: list
    elements: str
  puppet_proxy:
    description: Puppet server proxy name
    required: false
    type: str
  puppet_ca_proxy:
    description: Puppet CA proxy name
    required: false
    type: str
  openscap_proxy:
    description:
      - OpenSCAP proxy name.
      - Only available when the OpenSCAP plugin is installed.
    required: false
    type: str
  content_source:
    description:
      - Content source.
      - Only available for Katello installations.
    required: false
    type: str
  lifecycle_environment:
    description:
      - Lifecycle environment.
      - Only available for Katello installations.
    required: false
    type: str
  kickstart_repository:
    description:
      - Kickstart repository name.
      - You need to provide this to use the "Synced Content" feature.
      - Mutually exclusive with I(medium).
      - Only available for Katello installations.
    required: false
    type: str
  content_view:
    description:
      - Content view.
      - Only available for Katello installations.
    required: false
    type: str
'''

    ORGANIZATION = '''
options:
  organization:
    description:
      - Organization that the entity is in
    required: true
    type: str
'''

    SCAP_DATASTREAM = '''
options:
  scap_file:
    description:
      - File containing XML DataStream content.
      - Required when creating a new DataStream.
    required: false
    type: path
  original_filename:
    description:
      - Original file name of the XML file.
      - If unset, the filename of I(scap_file) will be used.
    required: false
    type: str
'''
