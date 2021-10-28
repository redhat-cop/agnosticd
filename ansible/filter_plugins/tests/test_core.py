#!/usr/bin/env python

import pytest
from ansible.errors import AnsibleFilterError
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import core



def test_ec2_tags_to_equinix_metal_tags():
    testcases = [
        [
            [
                {
                    "key":"AnsibleGroup",
                    "value":"bastions",
                },
                {
                    "key":"ostype",
                    "value":"linux",
                }
            ],
            [
                "AnsibleGroup=bastions",
                "ostype=linux"
            ],
        ],
        [
            [
                {
                    "Key":"AnsibleGroup",
                    "Value":"bastions",
                },
            ],
            [
                "AnsibleGroup=bastions",
            ],
        ],
        [
            [
                {
                    "Key":"AnsibleGroup",
                    "value":"bastions",
                },
            ],
            [
                "AnsibleGroup=bastions",
            ],
        ],
        [
            [
                {
                    "key":"AnsibleGroup",
                    "Value":"bastions",
                },
            ],
            [
                "AnsibleGroup=bastions",
            ],
        ],
        [
            [],
            [],
        ]
    ]

    for tc in testcases:
        assert(core.ec2_tags_to_equinix_metal_tags(tc[0]) == tc[1])

    error_testcases = [
        [
            {
                "key":"key1",
                "value":"value1",
            },
            {
                "key":"key2",
            }
        ],
        [
            {
                "key":"key1",
            },
        ],
        [
            {
                "key":"",
                "value":"value",
            },
        ],
        [
            {
                "key":"key",
                "value":"",
            },
        ],
        [1,2,3],
        "",
        None,
        {},
    ]

    for tc in error_testcases:
        with pytest.raises(AnsibleFilterError):
            core.ec2_tags_to_equinix_metal_tags(tc)

def test_equinix_metal_tags_to_dict():
    testcases = [
        [
            [
                "AnsibleGroup=bastions",
                "ostype=linux",
            ],
            { "AnsibleGroup":"bastions",
              "ostype":"linux"},
        ],
        [
            [
                "AnsibleGroup=bastions",
                "ostype=linux",
                "ignoredvalue",
            ],
            { "AnsibleGroup":"bastions",
              "ostype":"linux"},
        ],
        [
            [
                "AnsibleGroup=",
                "ostype=linux",
                "ignoredvalue",
            ],
            { "AnsibleGroup":"",
              "ostype":"linux"},
        ],
        [
            ["ignored"],
            {},
        ],
        [
            [],
            {},
        ]
    ]

    for tc in testcases:
        assert(core.equinix_metal_tags_to_dict(tc[0]) == tc[1])

    error_testcases = [
        [
            {
                "key":"key1",
                "value":"value1",
            },
        ],
        ["=c"],
        [1,2,3],
        "",
        None,
        {},
    ]

    for tc in error_testcases:
        with pytest.raises(AnsibleFilterError):
            core.equinix_metal_tags_to_dict(tc)

def test_ec2_tags_to_dict():
    testcases = [
        [
            [
                {
                    "key":"AnsibleGroup",
                    "value":"bastions",
                },
                {
                    "key":"ostype",
                    "value":"linux",
                }
            ],
            {
                "AnsibleGroup":"bastions",
                "ostype":"linux"
            },
        ],
        [
            [
                {
                    "Key":"AnsibleGroup",
                    "Value":"bastions",
                },
            ],
            {
                "AnsibleGroup":"bastions",
            },
        ],
        [
            [
                {
                    "Key":"AnsibleGroup",
                    "value":"bastions",
                },
            ],
            {
                "AnsibleGroup":"bastions",
            },
        ],
        [
            [
                {
                    "key":"AnsibleGroup",
                    "Value":"bastions",
                },
            ],
            {
                "AnsibleGroup":"bastions",
            },
        ],
        [
            [],
            {},
        ]
    ]

    for tc in testcases:
        assert(core.ec2_tags_to_dict(tc[0]) == tc[1])

    error_testcases = [
        [
            {
                "key":"key1",
                "value":"value1",
            },
            {
                "key":"key2",
            }
        ],
        [
            {
                "key":"key1",
            },
        ],
        [
            {
                "key":"",
                "value":"value",
            },
        ],
        [
            {
                "key":"key",
                "value":"",
            },
        ],
        [1,2,3],
        "",
        None,
        {},
    ]

    for tc in error_testcases:
        with pytest.raises(AnsibleFilterError):
            core.ec2_tags_to_dict(tc)

def test_dict_to_equinix_metal_tags():
    testcases = [
        [
            {
                    "AnsibleGroup":"bastions",
                    "ostype":"linux",
                    "number": 2,
            },
            [
                "AnsibleGroup=bastions",
                "ostype=linux",
                "number=2"
            ],
        ],
        [
            {},
            [],
        ]
    ]

    for tc in testcases:
        assert(core.dict_to_equinix_metal_tags(tc[0]) == tc[1])

    error_testcases = [
        {"key": {}},
        {2: "value"},
        {"key": []},
        [1,2,3],
        "",
        None,
        [],
    ]

    for tc in error_testcases:
        with pytest.raises(AnsibleFilterError):
            core.dict_to_equinix_metal_tags(tc)
