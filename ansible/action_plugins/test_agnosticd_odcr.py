#!/usr/bin/env python

import pytest
import agnosticd_odcr
import datetime

def test_parse_duration():

    testcases = [
        ['3d', datetime.timedelta(days=3)],
        [' 3d', datetime.timedelta(days=3)],
        [' 3d ', datetime.timedelta(days=3)],
        [' 3d   ', datetime.timedelta(days=3)],
        [' 3d \t  ', datetime.timedelta(days=3)],
        [' 3d \t \n ', datetime.timedelta(days=3)],
        ['8D', datetime.timedelta(days=8)],
        ['1h', datetime.timedelta(hours=1)],
        ['0h', datetime.timedelta(0)],
        ['0', datetime.timedelta(0)],
        ['0d0m0s', datetime.timedelta(0)],
        ['1d0m0s', datetime.timedelta(days=1)],
        ['0s', datetime.timedelta(0)],
        ['3600', datetime.timedelta(hours=1)],
        ['1d12h', datetime.timedelta(days=1, hours=12)],
        ['3d 12h 6m', datetime.timedelta(days=3, hours=12, minutes=6)],
        ['1d 12h', datetime.timedelta(days=1, hours=12)],
    ]
    for tc in testcases:
        assert(agnosticd_odcr.parse_duration(tc[0]) == tc[1])

    error_testcases = [
        '3 days',
        'INVALID',
        'duration in the middle 3d of a sentence',
        '2.3d',
        '2.3m',
        'd',
        'm',
        's',
        '',
        None,
        {},
        [],
        ["nonemptylist"],
    ]

    for tc in error_testcases:
        with pytest.raises(agnosticd_odcr.InvalidDuration):
            agnosticd_odcr.parse_duration(tc)
