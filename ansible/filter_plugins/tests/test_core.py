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

def test_agnosticd_get_all_images():

    predefined = {
        "image1": {
            "name": "image1",
            "owner": "1234",
        },
        "image2": {
            "name": "image2",
            "owner": "1234",
        },
        "image3": {
            "name": "image3",
            "owner": "1234",
        },
        "image4": "image1",
        "image5": ["image1", "image2"],
        "image6": ["image1", {"name": "image7"}, "image2"],
        "imageloop": ["image5", "image8", "imageloop"],
    }

    testcases = [
        # string not matching any predefined image dict
        ["undefined", []],
        # empty list (no image)
        [[], []],
        # list of list of list ... if empty, resolve to empty
        [[[], [[[]]]], []],
        # Get image by image name in predefined
        ["image1", [predefined["image1"]]],
        ["image1", [predefined["image1"]]],
        ["image2", [predefined["image2"]]],
        # Get image by dict, return list of one element with the same dict.
        [predefined["image2"], [predefined["image2"]]],
        # Get image by list of one dict, return the only image
        [[predefined["image2"]], [predefined["image2"]]],
        # Get image by list of one dict, and one ref to another image
        [[predefined["image2"], "image1"], [predefined["image2"], predefined["image1"]]],
        # Get image by name, that is a combination of 2 images
        ["image5", [predefined["image1"], predefined["image2"]]],
        ["image6", [predefined["image1"], {"name":"image7"}, predefined["image2"]]],
    ]

    for tc in testcases:
        print("test suivant")
        assert(core.agnosticd_get_all_images(tc[0], predefined) == tc[1])

    error_testcases = [
        "imageloop",
    ]

    for tc in error_testcases:
        with pytest.raises(AnsibleFilterError):
            core.agnosticd_get_all_images(tc, predefined)
