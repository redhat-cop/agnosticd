#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Christoffer Reijer (Basalt AB)
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
module: user
version_added: 1.0.0
short_description: Manage Users
description:
  - Create, update, and delete users
author:
  - "Christoffer Reijer (@ephracis) Basalt AB"
options:
  login:
    aliases:
      - name
    description:
      - Name of the user
    required: true
    type: str
  firstname:
    description:
      - First name of the user
    required: false
    type: str
  lastname:
    description:
      - Last name of the user
    required: false
    type: str
  mail:
    description:
      - Email address of the user
      - Required when creating a new user
    required: false
    type: str
  description:
    description:
      - Description of the user
    required: false
    type: str
  admin:
    description:
      - Whether or not the user is an administrator
    required: false
    default: false
    type: bool
  user_password:
    description:
      - Password for the user
    required: false
    type: str
  default_location:
    description:
      - The location that the user uses by default
    required: false
    type: str
  default_organization:
    description:
      - The organizxation that the user uses by default
    required: false
    type: str
  auth_source:
    description:
      - Authentication source where the user exists
    required: false
    type: str
  timezone:
    description:
      - Timezone for the user
      - If blank it will use the browser timezone.
    required: false
    type: str
    choices:
      - 'International Date Line West'
      - 'American Samoa'
      - 'Midway Island'
      - 'Hawaii'
      - 'Alaska'
      - 'Pacific Time (US & Canada)'
      - 'Tijuana'
      - 'Arizona'
      - 'Chihuahua'
      - 'Mazatlan'
      - 'Mountain Time (US & Canada)'
      - 'Central America'
      - 'Central Time (US & Canada)'
      - 'Guadalajara'
      - 'Mexico City'
      - 'Monterrey'
      - 'Saskatchewan'
      - 'Bogota'
      - 'Eastern Time (US & Canada)'
      - 'Indiana (East)'
      - 'Lima'
      - 'Quito'
      - 'Atlantic Time (Canada)'
      - 'Caracas'
      - 'Georgetown'
      - 'La Paz'
      - 'Puerto Rico'
      - 'Santiago'
      - 'Newfoundland'
      - 'Brasilia'
      - 'Buenos Aires'
      - 'Greenland'
      - 'Montevideo'
      - 'Mid-Atlantic'
      - 'Azores'
      - 'Cape Verde Is.'
      - 'Dublin'
      - 'Edinburgh'
      - 'Lisbon'
      - 'London'
      - 'Monrovia'
      - 'UTC'
      - 'Amsterdam'
      - 'Belgrade'
      - 'Berlin'
      - 'Bern'
      - 'Bratislava'
      - 'Brussels'
      - 'Budapest'
      - 'Casablanca'
      - 'Copenhagen'
      - 'Ljubljana'
      - 'Madrid'
      - 'Paris'
      - 'Prague'
      - 'Rome'
      - 'Sarajevo'
      - 'Skopje'
      - 'Stockholm'
      - 'Vienna'
      - 'Warsaw'
      - 'West Central Africa'
      - 'Zagreb'
      - 'Zurich'
      - 'Athens'
      - 'Bucharest'
      - 'Cairo'
      - 'Harare'
      - 'Helsinki'
      - 'Jerusalem'
      - 'Kaliningrad'
      - 'Kyiv'
      - 'Pretoria'
      - 'Riga'
      - 'Sofia'
      - 'Tallinn'
      - 'Vilnius'
      - 'Baghdad'
      - 'Istanbul'
      - 'Kuwait'
      - 'Minsk'
      - 'Moscow'
      - 'Nairobi'
      - 'Riyadh'
      - 'St. Petersburg'
      - 'Tehran'
      - 'Abu Dhabi'
      - 'Baku'
      - 'Muscat'
      - 'Samara'
      - 'Tbilisi'
      - 'Volgograd'
      - 'Yerevan'
      - 'Kabul'
      - 'Ekaterinburg'
      - 'Islamabad'
      - 'Karachi'
      - 'Tashkent'
      - 'Chennai'
      - 'Kolkata'
      - 'Mumbai'
      - 'New Delhi'
      - 'Sri Jayawardenepura'
      - 'Kathmandu'
      - 'Almaty'
      - 'Astana'
      - 'Dhaka'
      - 'Urumqi'
      - 'Rangoon'
      - 'Bangkok'
      - 'Hanoi'
      - 'Jakarta'
      - 'Krasnoyarsk'
      - 'Novosibirsk'
      - 'Beijing'
      - 'Chongqing'
      - 'Hong Kong'
      - 'Irkutsk'
      - 'Kuala Lumpur'
      - 'Perth'
      - 'Singapore'
      - 'Taipei'
      - 'Ulaanbaatar'
      - 'Osaka'
      - 'Sapporo'
      - 'Seoul'
      - 'Tokyo'
      - 'Yakutsk'
      - 'Adelaide'
      - 'Darwin'
      - 'Brisbane'
      - 'Canberra'
      - 'Guam'
      - 'Hobart'
      - 'Melbourne'
      - 'Port Moresby'
      - 'Sydney'
      - 'Vladivostok'
      - 'Magadan'
      - 'New Caledonia'
      - 'Solomon Is.'
      - 'Srednekolymsk'
      - 'Auckland'
      - 'Fiji'
      - 'Kamchatka'
      - 'Marshall Is.'
      - 'Wellington'
      - 'Chatham Is.'
      - "Nuku'alofa"
      - 'Samoa'
      - 'Tokelau Is.'
  locale:
    description:
      - The language locale for the user
    required: false
    type: str
    choices:
      - 'ca'
      - 'de'
      - 'en'
      - 'en_GB'
      - 'es'
      - 'fr'
      - 'gl'
      - 'it'
      - 'ja'
      - 'ko'
      - 'nl_NL'
      - 'pl'
      - 'pt_BR'
      - 'ru'
      - 'sv_SE'
      - 'zh_CN'
      - 'zh_TW'
  roles:
    description:
      - List of roles assigned to the user
    required: false
    type: list
    elements: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
- name: Create a user
  theforeman.foreman.user:
    name: test
    firstname: Test
    lastname: Userson
    mail: test.userson@example.com
    description: Dr. Test Userson
    admin: no
    user_password: s3cret
    default_location: Test Location
    default_organization: Test Organization
    auth_source: Internal
    timezone: Stockholm
    locale: sv_SE
    roles:
      - Manager
    locations:
      - Test Location
    organizations:
      - Test Organization
    state: present

- name: Update a user
  theforeman.foreman.user:
    name: test
    firstname: Tester
    state: present

- name: Change password
  theforeman.foreman.user:
    name: test
    user_password: newp@ss

'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    users:
      description: List of users.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanTaxonomicEntityAnsibleModule,
)


# List of allowed timezones
timezone_list = [
    'International Date Line West',
    'American Samoa',
    'Midway Island',
    'Hawaii',
    'Alaska',
    'Pacific Time (US & Canada)',
    'Tijuana',
    'Arizona',
    'Chihuahua',
    'Mazatlan',
    'Mountain Time (US & Canada)',
    'Central America',
    'Central Time (US & Canada)',
    'Guadalajara',
    'Mexico City',
    'Monterrey',
    'Saskatchewan',
    'Bogota',
    'Eastern Time (US & Canada)',
    'Indiana (East)',
    'Lima',
    'Quito',
    'Atlantic Time (Canada)',
    'Caracas',
    'Georgetown',
    'La Paz',
    'Puerto Rico',
    'Santiago',
    'Newfoundland',
    'Brasilia',
    'Buenos Aires',
    'Greenland',
    'Montevideo',
    'Mid-Atlantic',
    'Azores',
    'Cape Verde Is.',
    'Dublin',
    'Edinburgh',
    'Lisbon',
    'London',
    'Monrovia',
    'UTC',
    'Amsterdam',
    'Belgrade',
    'Berlin',
    'Bern',
    'Bratislava',
    'Brussels',
    'Budapest',
    'Casablanca',
    'Copenhagen',
    'Ljubljana',
    'Madrid',
    'Paris',
    'Prague',
    'Rome',
    'Sarajevo',
    'Skopje',
    'Stockholm',
    'Vienna',
    'Warsaw',
    'West Central Africa',
    'Zagreb',
    'Zurich',
    'Athens',
    'Bucharest',
    'Cairo',
    'Harare',
    'Helsinki',
    'Jerusalem',
    'Kaliningrad',
    'Kyiv',
    'Pretoria',
    'Riga',
    'Sofia',
    'Tallinn',
    'Vilnius',
    'Baghdad',
    'Istanbul',
    'Kuwait',
    'Minsk',
    'Moscow',
    'Nairobi',
    'Riyadh',
    'St. Petersburg',
    'Tehran',
    'Abu Dhabi',
    'Baku',
    'Muscat',
    'Samara',
    'Tbilisi',
    'Volgograd',
    'Yerevan',
    'Kabul',
    'Ekaterinburg',
    'Islamabad',
    'Karachi',
    'Tashkent',
    'Chennai',
    'Kolkata',
    'Mumbai',
    'New Delhi',
    'Sri Jayawardenepura',
    'Kathmandu',
    'Almaty',
    'Astana',
    'Dhaka',
    'Urumqi',
    'Rangoon',
    'Bangkok',
    'Hanoi',
    'Jakarta',
    'Krasnoyarsk',
    'Novosibirsk',
    'Beijing',
    'Chongqing',
    'Hong Kong',
    'Irkutsk',
    'Kuala Lumpur',
    'Perth',
    'Singapore',
    'Taipei',
    'Ulaanbaatar',
    'Osaka',
    'Sapporo',
    'Seoul',
    'Tokyo',
    'Yakutsk',
    'Adelaide',
    'Darwin',
    'Brisbane',
    'Canberra',
    'Guam',
    'Hobart',
    'Melbourne',
    'Port Moresby',
    'Sydney',
    'Vladivostok',
    'Magadan',
    'New Caledonia',
    'Solomon Is.',
    'Srednekolymsk',
    'Auckland',
    'Fiji',
    'Kamchatka',
    'Marshall Is.',
    'Wellington',
    'Chatham Is.',
    "Nuku'alofa",
    'Samoa',
    'Tokelau Is.',
]

# List of allowed locales
locale_list = [
    'ca',
    'de',
    'en',
    'en_GB',
    'es',
    'fr',
    'gl',
    'it',
    'ja',
    'ko',
    'nl_NL',
    'pl',
    'pt_BR',
    'ru',
    'sv_SE',
    'zh_CN',
    'zh_TW',
]


class ForemanUserModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanUserModule(
        foreman_spec=dict(
            login=dict(required=True, aliases=['name']),
            firstname=dict(required=False),
            lastname=dict(required=False),
            mail=dict(required=False),
            description=dict(required=False),
            admin=dict(required=False, type='bool', default=False),
            user_password=dict(required=False, no_log=True, flat_name='password'),
            default_location=dict(required=False, type='entity', resource_type='locations'),
            default_organization=dict(required=False, type='entity', resource_type='organizations'),
            auth_source=dict(required=False, type='entity'),
            timezone=dict(required=False, choices=timezone_list),
            locale=dict(required=False, choices=locale_list),
            roles=dict(required=False, type='entity_list'),
        ),
        entity_key='login',
    )

    with module.api_connection():
        entity = module.lookup_entity('entity')

        if not module.desired_absent:
            if 'mail' not in module.foreman_params:
                if not entity:
                    module.fail_json(msg="The 'mail' parameter is required when creating a new user.")
                else:
                    module.foreman_params['mail'] = entity['mail']

        module.run()


if __name__ == '__main__':
    main()
