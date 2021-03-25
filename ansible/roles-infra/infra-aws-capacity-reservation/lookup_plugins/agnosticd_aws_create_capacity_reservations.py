"""agnosticd_aws_create_capcity_reservations Lookup plugin"""

from __future__ import (absolute_import, division, print_function)
import datetime
import re
import pprint
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

import boto3
import botocore.exceptions
#pylint: disable=invalid-name
__metaclass__ = type
#pylint: enable=invalid-name

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

def parse_time(time_str):
    """Parse duration (str) and return timedelta

    Return False if the string doesn't match"""

    regex = re.compile(
        r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?'
    )

    parts = regex.match(time_str)
    if not parts:
        return False
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

    raise AnsibleError("Key {} is not supported in a reservation.".format(key_str))


def tag_match(tags1, tags2):
    """All tags1 are in tags2"""
    for tag in tags1:
        if tag in tags2:
            continue

        return False

    return True

def check_response(response):
    """Check HTTPStatusCode"""
    try:
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            display.error(pp.pformat(response))
            raise AnsibleError("Error requesting EC2 offerings.")
    except Exception as err:
        display.error(pp.pformat(response))
        raise AnsibleError("Error requesting EC2 offerings.") from err

# TODO: create a class ODCRFactory

class LookupModule(LookupBase):
    """LookupModule class"""

    def get_azs(self, region):
        """Return all availability zones for a region"""

        if region not in self.availability_zones:
            response = self.clients[region].describe_availability_zones()

            self.availability_zones[region] = list(
                map(
                    lambda elem: elem['ZoneName'],
                    filter(
                        lambda elem: elem['State'] == 'available',
                        response['AvailabilityZones']
                    )
                )
            )

        return self.availability_zones[region]

    def filter_azs(self, region, instance_types):
        """Return the AZs with matching InstanceType offerings,
        given a list of instance types.
        """
        response = self.clients[region].describe_instance_type_offerings(
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

        # Start with all AZs
        result = set(self.get_azs(region))

        # Get the intersection of all AZs
        for instance_type in instance_types:
            instance_type_azs = set()
            for offering in response['InstanceTypeOfferings']:
                if offering['InstanceType'] == instance_type:
                    instance_type_azs.add(offering['Location'])

            # Reduce the set
            result = result & instance_type_azs

        return result

    def describe_reservations(self, region, availability_zone='*'):
        """Filter reservations by tag and return Ids"""

        filters = [{'Name':'state', 'Values':['active','pending']}]
        if availability_zone is not None and availability_zone != '*' and availability_zone != '':
            filters.append({'Name': 'availability-zone', 'Values': [availability_zone]})

        response = self.clients[region].describe_capacity_reservations(
            Filters=filters,
        )

        check_response(response)

        display.vvvvv(pp.pformat(response))
        result = list(
            filter(lambda elem: tag_match(self.tags, elem['Tags']),
                   response['CapacityReservations']))

        return [i['CapacityReservationId'] for i in result]

    def cancel_reservation(self, region, reservation_id):
        """Cancel a reservation by ID"""

        response = self.clients[region].cancel_capacity_reservation(
            CapacityReservationId=reservation_id,
        )
        display.vvvv(pp.pformat(response))

        check_response(response)

        display.display("Reservation canceled: %s  (%s)" %(reservation_id, region))

    def cancel_all_reservations(self, region):
        """Cancel all reservations in a region matching tags"""
        reservation_ids = self.describe_reservations(region)
        for r_id in reservation_ids:
            self.cancel_reservation(region, r_id)

    def create_reservation(self, region, availability_zone, reservation):
        """Create a reservation in an Availability Zone.

        On success:
            Return True, reservation_id
        On Failure:
            Return False, ''
        """
        try:
            reservation_translated = {
                translate_to_api_names(k): v for k, v in reservation.items()
            }

            try:
                duration = parse_time(self.ttl)
            except Exception as err:
                raise AnsibleError("could not parse duration {}".format(self.ttl)) from err

            if len(self.tags) > 0:
                tag_spec =[{
                    'ResourceType': 'capacity-reservation',
                    'Tags':self.tags,
                }]
            else:
                tag_spec = []

            response = self.clients[region].create_capacity_reservation(
                **reservation_translated,
                AvailabilityZone=availability_zone,
                EndDate=datetime.datetime.now() + duration,
                EndDateType='limited',
                InstanceMatchCriteria='open',
                TagSpecifications=tag_spec,
            )

            check_response(response)
            display.vvvv("response: %s" % pp.pformat(response))

            display.vvv(pp.pformat(response))
        except botocore.exceptions.ClientError as err:
            if 'InstanceLimitExceeded' in str(err):
                display.display("InstanceLimitExceeded %s - %d * %s"
                                %(availability_zone,
                                  reservation['instance_count'],
                                  reservation['instance_type']))
                display.display(
                    "Reservation could not be created in %s, trying next AZ."
                    %(availability_zone)
                )
                return False, ''

            if 'InsufficientInstanceCapacity' in str(err):
                display.display("InsufficientInstanceCapacity %s - %d * %s"
                                %(availability_zone, reservation['instance_count'],
                                    reservation['instance_type']))

                return False, ''

            display.error(pp.pformat(err))
            raise AnsibleError(
                "Client Error while creating reservation."
            ) from err

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            # if success, continue
            r_id = response['CapacityReservation']['CapacityReservationId']
            display.display("Reservation created: %s (%s)" %(r_id, availability_zone))
            return True, r_id

        return False, ''


    def create_reservations(self, region, availability_zone, reservations):
        """Create all reservations in the specified AZ

        Return a tuple (ok, reservations_ids)

        On success:
            ok is True
            reservations_ids is the list of capacity-reservation IDs created

        On failure:
            ok is False
            reservation_ids is the empty list
        """
        reservation_ids = []
        for reservation in reservations:
            if self.dry_run:
                continue

            return_ok, reservation_id = self.create_reservation(
                region,
                availability_zone,
                reservation)

            if not return_ok:
                display.display(
                    "reservation could not be created in %s, trying next AZ."
                    %(availability_zone)
                )
                for r_id in reservation_ids:
                    self.cancel_reservation(region, r_id)

                return False, []

            reservation_ids.append(reservation_id)

        return True, reservation_ids

    def do_reservation_group(self, region, reservation_group):
        """Determine the AZs with matching instance-type offerings.

        Try to create capacity reservations in one of those AZs.
        If fails, move the next matching AZ.
        If all fail, fail.

        On success:
        Return True, availability_zone, reservation_ids

        On failure:
        Return False, '', empty list
        """
        display.v("..loop2: reservation_group: %s" % (pp.pformat(reservation_group)))

        all_instance_types = set(
            i['instance_type'] for i in reservation_group
        )
        matching_azs = self.filter_azs(region, all_instance_types)
        display.v(
            "..loop2: AZs with matching offerings for group: %s" %
            (pp.pformat(matching_azs)))

        for availability_zone in matching_azs:
            display.v("...loop3: trying AZ %s" %(availability_zone))

            r_ok, reservation_ids = self.create_reservations(
                region,
                availability_zone,
                reservation_group)

            if r_ok:
                return True, availability_zone, reservation_ids

        return False, '', []

    def do_region(self, region, reservation_groups):
        """Create reservations, try a region.

        On success:
            Return True,
                   {
                     'az1': {
                         'availability_zone': ...,
                         'reservation_ids': ...,
                     },
                     ...
                   }

        On failure:
            Return False, {}
        """


        display.v(".loop1: Trying region %s" % (region))

        if region not in self.clients:
            self.set_client(region)

        display.v(".loop1: available AZs: %s" % self.get_azs(region))

        result = {}
        for reservation_group_name in reservation_groups:
            reservation_group = reservation_groups[reservation_group_name]
            display.v("..loop2: group %s" %(reservation_group_name))
            r_ok, availability_zone, reservation_ids = self.do_reservation_group(
                region,
                reservation_group
            )

            if not r_ok:
                # cancel all reservations made in that region
                self.cancel_all_reservations(region)
                return False, {}

            result[reservation_group_name] = {
                'availability_zone': availability_zone,
                'reservation_ids': reservation_ids,
            }

        return True, result

    def set_client(self, region):
        """Create and save boto3 EC2 client for a region"""
        self.clients[region] = boto3.client('ec2',
                                            aws_access_key_id=self.aws_key,
                                            aws_secret_access_key=self.aws_secret,
                                            region_name=region,
                                            )

    def run(self, terms, variables=None, **kwargs):
        # pylint: disable=attribute-defined-outside-init
        self.ttl = kwargs.get('ttl', '1h')
        self.aws_key = variables['aws_access_key_id']
        self.aws_secret = variables['aws_secret_access_key']
        self.tags = []
        self.clients = {}
        self.availability_zones = {}
        self.action = variables['ACTION']
        if 'odcr_DRYRUN' in variables:
            self.dry_run = True
        else:
            self.dry_run = False

        if 'uuid' in variables:
            self.tags.append({'Key': 'uuid', 'Value': variables['uuid']})

        self.tags.append({'Key': 'guid', 'Value': variables['guid']})
        self.tags.append({'Key': 'created-by', 'Value': 'agnosticd'})


        # First, cleanup all reservations matching tags
        for region in set(self._flatten(term['regions'] for term in terms)):
            self.set_client(region)
            self.cancel_all_reservations(region)

        if self.action == 'destroy':
            return []

        ret = []
        for term in terms:
            display.v("# input\n%s" % pp.pformat(term))
            display.v("ttl: %s" % self.ttl)

            for region in term['regions']:
                r_ok, result = self.do_region(region, term['reservations'])
                if r_ok:
                    # In case of a single availability zone
                    if len(result) == 1:
                        for k in list(result):
                            result['single_availability_zone'] = result[k]['availability_zone']

                    result['region'] = region
                    ret.append(result)
                    break

                # All reservation groups could not be created in the available AZs
                display.display(
                    "Reservations could not be created in %s, trying next region."
                    %(region)
                )
            else:
                display.display("No more regions.")
                raise AnsibleError("Reservations could not be created.")

        return ret
