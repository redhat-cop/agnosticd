from __future__ import (absolute_import, division, print_function)
import datetime
import os
import re
import pprint
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

import boto3
import botocore.exceptions
__metaclass__ = type

DOCUMENTATION = """
        lookup: agnosticd_aws_create_capacity_reservations
        author: Guillaume Core <gucore@redhat.com>
        version_added: "2.9"
        short_description: Create AWS on-demand Capacity Reservations
        description:
            - Create reservations and return Regions / AZs / Ids
        options:
          _terms:
            description: reservations to create
            required: True
          ttl:
            description: The TTL to set in the reservations
            required: False
            type: int
            default: 1h
"""

EXAMPLES = """
- name: Create reservations and save result
  vars:
    odcr:
      regions:
      - us-east-1
      - us-east-2
      reservations:
        az1:
          - instance_count: 3
            instance_platform: Linux/UNIX
            instance_type: "m5.xlarge"
  set_fact:
    _capacity_reservations: >-
      {{
      lookup(
      'agnosticd_aws_create_capacity_reservations',
      odcr,
      ttl='1h'
      )
      }}


"""

RETURN = """
_raw:
   description: Reservations
   type: list
"""

display = Display()
pp = pprint.PrettyPrinter(indent=2)

regex = re.compile(
    r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?'
)

def parse_time(time_str):
    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in iter(parts.items()):
        if param:
            time_params[name] = int(param)
    return datetime.timedelta(**time_params)

def translate_to_api_names(key_str):
    """Return the corresponding names to use with AWS Apis and python functions"""
    entries = {
        'instance_count': 'InstanceCount',
        'instance_platform': 'InstancePlatform',
        'instance_type': 'InstanceType',
        'instance_match_criteria': 'InstanceMatchCriteria',
        'tenancy': 'Tenancy',
    }

    if key_str in entries:
        return entries[key_str]
    else:
        raise AnsibleError("Key {} is not supported in a reservation.".format(key_str))


def tag_match(tags1, tags2):
    """All tags1 are in tags2"""
    for t1 in tags1:
        if t1 in tags2:
            continue

        return False

    return True

def check_response(response):
    """Check HTTPStatusCode"""
    try:
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            display.error(pp.pformat(response))
            raise AnsibleError("Error requesting EC2 offerings.")
    except:
        display.error(pp.pformat(response))
        raise AnsibleError("Error requesting EC2 offerings.")

class LookupModule(LookupBase):

    def get_azs(self):
        """Return all availability zones for a region"""

        response = self.client.describe_availability_zones()

        return list(
            map(
                lambda elem: elem['ZoneName'],
                filter(
                    lambda elem: elem['State'] == 'available',
                    response['AvailabilityZones']
                )
            )
        )

    def filter_azs(self, azs, instance_types):
        """Return the intersection of possible AZs for a list of instance types.

        args: 1) set of all AZs
              2) set of all instance types

        return:  set of AZs for which there is an offering for all instance types
        """
        response = self.client.describe_instance_type_offerings(
            LocationType='availability-zone',
            Filters=[
                {
                    'Name': 'instance-type',
                    'Values': list(instance_types),
                },
            ],
        )

        check_response(response)

        display.vvv(pp.pformat(response['InstanceTypeOfferings']))

        result = azs

        # Get the intersection of all AZs
        for instance_type in instance_types:
            result = result & set(map(lambda elem: elem['Location'],
                                      list(filter(lambda elem: elem['InstanceType'] == instance_type,
                                                  response['InstanceTypeOfferings']))))

        return result


    def create_reservation(self, ttl, reservation, tags=[], az=''):
        """Create an on-demand reservation

        returns ...
        """
        reservation_translated = {
            translate_to_api_names(k): v for k, v in reservation.items()
        }

        try:
            duration = parse_time(ttl)
        except:
            raise AnsibleError("could not parse duration {}".format(ttl))

        if len(tags) > 0:
            tag_spec =[{
                'ResourceType': 'capacity-reservation',
                'Tags':tags,
            }]
        else:
            tag_spec = []

        response = self.client.create_capacity_reservation(
            **reservation_translated,
            AvailabilityZone=az,
            EndDate=datetime.datetime.now() + duration,
            EndDateType='limited',
            InstanceMatchCriteria='open',
            TagSpecifications=tag_spec,
        )

        check_response(response)

        display.vvvv("response: %s" % pp.pformat(response))
        return response

    def describe_reservations(self, tags=[], az='*'):
        """Filter reservations by tag and return Ids"""

        filters = [{'Name':'state', 'Values':['active','pending']}]
        if az != None and az != '*' and az != '':
            filters.append({'Name': 'availability-zone', 'Values': [az]})

        response = self.client.describe_capacity_reservations(
            Filters=filters,
        )

        check_response(response)

        display.vvvvv(pp.pformat(response))
        result = list(
            filter(lambda elem: tag_match(tags, elem['Tags']),
                   response['CapacityReservations']))

        return [i['CapacityReservationId'] for i in result]

    def cancel_reservation(self, reservation_id, context):
        """Cancel a reservation by ID"""

        response = self.client.cancel_capacity_reservation(
            CapacityReservationId=reservation_id,
        )
        display.vvvv(pp.pformat(response))

        check_response(response)

        display.display("Reservation canceled: %s  (%s)" %(reservation_id, context))

    def cancel_all_reservations(tags, context):
        """Cancel all reservations matching tags"""
        reservation_ids = self.describe_reservations(tags=tags)
        for r_id in reservation_ids:
            self.cancel_reservation(r_id, context)

    def run(self, terms, variables=None, **kwargs):
        ttl = kwargs.get('ttl', '1h')

        aws_key = variables['aws_access_key_id']
        aws_secret = variables['aws_secret_access_key']

        tags = []
        if 'uuid' in variables:
            tags.append({'Key': 'uuid', 'Value': variables['uuid']})

        tags.append({'Key': 'guid', 'Value': variables['guid']})
        tags.append({'Key': 'created-by', 'Value': 'agnosticd'})


        ret = []
        for term in terms:
            display.v("# input\n%s" % pp.pformat(term))
            display.v("ttl: %s" % ttl)
            regions = term['regions']

            for region in regions:
                self.client = boto3.client('ec2',
                                        aws_access_key_id=aws_key,
                                        aws_secret_access_key=aws_secret,
                                        region_name=region,
                                        )
                self.cleanup_all_reservations(tags, context=region)


            loop1_break = False
            for region in regions:
                display.v(".loop1: Trying region %s" % (region))

                self.client = boto3.client('ec2',
                                        aws_access_key_id=aws_key,
                                        aws_secret_access_key=aws_secret,
                                        region_name=region,
                                        )

                all_azs = set(self.get_azs())
                display.v(".loop1: available AZs: %s" % all_azs)

                loop2_break = False
                for reservation_group in term['reservations']:
                    display.v("..loop2: reservation_group: %s" % (pp.pformat(reservation_group)))

                    all_instance_types = set(
                        i['instance_type'] for i in term['reservations'][reservation_group]
                    )
                    all_possible_azs = self.filter_azs(all_azs, all_instance_types)
                    display.v(
                        "..loop2: AZs with matching offerings for group %s: %s" %
                        (reservation_group, pp.pformat(all_possible_azs)))

                    loop3_break = False
                    for az in all_possible_azs:
                        created_reservations = []
                        display.v("...loop3: trying az %s" %(az))

                        for reservation in term['reservations'][reservation_group]:
                            # TODO: remove DRYRUN or replace with action=destroy
                            if 'DRYRUN' in variables and variables['DRYRUN']:
                                continue
                            try:
                                response = self.create_reservation(
                                    ttl=ttl,
                                    reservation=reservation,
                                    az=az,
                                    tags=tags)
                            except botocore.exceptions.ClientError as err:
                                if 'InstanceLimitExceeded' in str(err):
                                    display.display("InstanceLimitExceeded %s - %d * %s"
                                                    %(az, reservation['instance_count'], reservation['instance_type']))
                                    display.display(
                                        "Reservation could not be created in %s, trying next AZ."
                                        %(az)
                                    )
                                    for r_id in created_reservations:
                                        self.cancel_reservation(r_id, context=az)
                                    break

                                if 'InsufficientInstanceCapacity' in str(err):
                                    display.display("InsufficientInstanceCapacity %s - %d * %s"
                                                    %(az, reservation['instance_count'],
                                                      reservation['instance_type']))

                                    display.display(
                                        "Reservation could not be created in %s, trying next AZ."
                                        %(az)
                                    )
                                    for r_id in created_reservations:
                                        self.cancel_reservation(r_id, context=az)
                                    break

                                display.error(pp.pformat(err))
                                raise AnsibleError(
                                    "Client Error while creating reservation."
                                ) from err

                            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                                # if success, continue
                                r_id = response['CapacityReservation']['CapacityReservationId']
                                display.display("Reservation created: %s (%s)" %(r_id, az))
                                created_reservations.append(r_id)
                                continue

                            display.v(pp.pformat(r))
                            display.display(
                                "Reservation could not be created in %s, trying next AZ."
                                %(az)
                            )
                            for r_id in created_reservations:
                                self.cancel_reservation(r_id, context=az)
                            break
                        else:
                            # All reservations of the reservation group (az) are created
                            break
                        if loop3_break:
                            break
                    else:
                        # All AZ were tried for that reservation group
                        display.display(
                            "Reservations could not be created in %s, trying next region."
                            %(region)
                        )
                        # cancel all reservations made in that region
                        self.cleanup_all_reservations(tags, context=region)

                        break
                    if loop2_break:
                        break
                else:
                    # All reservation groups (az) are done
                    break
                if loop1_break:
                    break

        # TODO: testing (aws api down, etc)
        # TODO: return value
        ret_i = {}
        ret_i['azs'] = {}
        ret_i['ids'] = {}
        ret_i['region'] = "us-east-1"
        ret.append(ret_i)
        display.vvv("result: %s" % ret)
        return ret
