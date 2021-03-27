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
        ['0s', datetime.timedelta(0)],
        ['3600', datetime.timedelta(hours=1)],
        ['1d12h', datetime.timedelta(days=1, hours=12)],
        ['3d 12h 6m', datetime.timedelta(days=3, hours=12, minutes=6)],
        ['1d 12h', datetime.timedelta(days=1, hours=12)],
    ]
    for tc in testcases:
        assert(agnosticd_odcr.parse_duration(tc[0]) == tc[1])
