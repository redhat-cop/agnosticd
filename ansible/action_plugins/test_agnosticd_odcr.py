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

def test_reservation_match():
    r1 = {"instance_platform": "Linux/UNIX",
          "instance_type": "m5.xlarge",
          "instance_count": 1}

    r2 = {"instance_platform": "Linux/UNIX",
          "instance_type": "m5.xlarge",
          "instance_count": 2}

    r2_1 = {"instance_type": "m5.xlarge",
            "instance_count": 2}

    r3 = {"instance_platform": "Linux/UNIX",
          "instance_type": "m5.xlarge",
          "instance_count": 3}

    r4 = {"instance_platform": "Linux/UNIX",
          "instance_type": "m4.large",
          "instance_count": 10}
    testcases = [
        {
            "args": [r1, r1],
            "result": True,
        },
        {
            "args": [r1, r2],
            "result": True,
        },
        {
            "args": [r2, r2_1],
            "result": False,
        },
    ]

    for tc in testcases:
        assert agnosticd_odcr.reservation_match(*tc["args"]) == tc["result"], tc

def test_inject_reservation():
    r1 = {"instance_platform": "Linux/UNIX",
          "instance_type": "m5.xlarge",
          "instance_count": 1}
    r1_1 = {"instance_platform": "Linux/UNIX",
            "instance_type": "m5.xlarge",
            "instance_count": "1"}

    r2 = {"instance_platform": "Linux/UNIX",
          "instance_type": "m5.xlarge",
          "instance_count": 2}

    r2_1 = {"instance_type": "m5.xlarge",
            "instance_count": 2}

    r3 = {"instance_platform": "Linux/UNIX",
          "instance_type": "m5.xlarge",
          "instance_count": 3}

    r4 = {"instance_platform": "Linux/UNIX",
          "instance_type": "m4.large",
          "instance_count": 10}
    testcases = [
        {
            "args": [[], r1],
            "result": [r1]
        },
        {
            "args": [[], r1, r1_1],
            "result": [r2]
        },
        {
            "args": [[r1], r1],
            "result": [r2]
        },
        {
            "args": [[r1], r1],
            "result": [r2]
        },
        {
            "args": [[], r1, r2, r4],
            "result": [r3, r4]
        },
        {
            "args": [[], r1, r2, r2_1, r4],
            "result": [r3, r2_1, r4]
        },
    ]
    for tc in testcases:
        assert(agnosticd_odcr.inject_reservation(*tc["args"]) == tc["result"])

def test_regroup_reservations():
    input1 = {
        "az1": [
            {"instance_count":1,"instance_platform":"Linux/UNIX","instance_type":"t3.large"}
        ],
        "masters": [
            {"instance_count":3,"instance_platform":"Linux/UNIX","instance_type":"m5.xlarge"}
        ],
        "workers1": [
            {"instance_count":3,"instance_platform":"Linux/UNIX","instance_type":"m5a.2xlarge"}
        ],
        "workers2": [
            {"instance_count":2,"instance_platform":"Linux/UNIX","instance_type":"m5a.2xlarge"}
        ]}

    expected1 = {
        "az1": [
            {"instance_count":1,"instance_platform":"Linux/UNIX","instance_type":"t3.large"},
            {"instance_count":3,"instance_platform":"Linux/UNIX","instance_type":"m5.xlarge"},
            {"instance_count":5,"instance_platform":"Linux/UNIX","instance_type":"m5a.2xlarge"}
        ]
    }

    input2 = {
        "az1": [
            {"instance_count":1,"instance_platform":"Linux/UNIX","instance_type":"t3.large"}
        ],
        "masters": [
            {"instance_count":3,"instance_platform":"Linux/UNIX","instance_type":"m5.xlarge"}
        ],
        "workers1": [
            {"instance_count":3,"instance_platform":"Linux/UNIX","instance_type":"m5.xlarge"}
        ],
        "workers2": [
            {"instance_count":2,"instance_platform":"Red hat","instance_type":"m5.xlarge"}
        ]}

    expected2 = {
        "az1": [
            {"instance_count":1,"instance_platform":"Linux/UNIX","instance_type":"t3.large"},
            {"instance_count":6,"instance_platform":"Linux/UNIX","instance_type":"m5.xlarge"},
            {"instance_count":2,"instance_platform":"Red hat","instance_type":"m5.xlarge"},
        ]
    }
    input3 = {
        "az1": [
            {"instance_count":1,"instance_platform":"Linux/UNIX","instance_type":"m5.xlarge"}
        ],
        "masters": [
            {"instance_count":3,"instance_platform":"Linux/UNIX","instance_type":"m5.xlarge"}
        ],
        "workers1": [
            {"instance_count":3,"instance_platform":"Linux/UNIX","instance_type":"m5.xlarge"}
        ],
        "workers2": [
            {"instance_count":30,"instance_platform":"Linux/UNIX","instance_type":"m5.xlarge"}
        ]}

    expected3 = {
        "az1": [
            {"instance_count":37,"instance_platform":"Linux/UNIX","instance_type":"m5.xlarge"},
        ]
    }

    input4 = {
        "myzone": [
            {"instance_count":1,"instance_platform":"Linux/UNIX","instance_type":"m5.xlarge"}
        ],
    }
    expected4 = {
        "az1": [
            {"instance_count":1,"instance_platform":"Linux/UNIX","instance_type":"m5.xlarge"},
        ]
    }

    testcases = [
        [input1, expected1],
        [input1, expected1],
        [input2, expected2],
        [input3, expected3],
        [input4, expected4],
        [{}, {"az1":[]}],
    ]

    for tc in testcases:
        assert(agnosticd_odcr.regroup_reservations(tc[0]) == tc[1])
