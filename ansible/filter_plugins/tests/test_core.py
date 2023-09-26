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
        assert(sorted(core.ec2_tags_to_equinix_metal_tags(tc[0])) == tc[1])

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
                "ignoredvalue",
                "ostype=linux",
            ],
            { "AnsibleGroup":"bastions",
              "ostype":"linux"},
        ],
        [
            [
                "AnsibleGroup=",
                "ignoredvalue",
                "ostype=linux",
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
                "number=2",
                "ostype=linux",
            ],
        ],
        [
            {},
            [],
        ]
    ]

    for tc in testcases:
        assert(sorted(core.dict_to_equinix_metal_tags(tc[0])) == tc[1])

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
        assert(core.agnosticd_get_all_images(tc[0], predefined) == tc[1])

    error_testcases = [
        "imageloop",
    ]

    for tc in error_testcases:
        with pytest.raises(AnsibleFilterError):
            core.agnosticd_get_all_images(tc, predefined)

def test_agnosticd_filter_out_installed_collections():
    testcases = [
        {
            "requirements": {},
            "installed_collections": {},
            "result": {},
        },
        {
            "requirements":
            {
                "collections": [
                    {
                        "name": "amazon.aws",
                        "version": "2.2.0"
                    },
                    {
                        "name": "ansible.posix",
                        "version": "1.3.0"
                    },
                    {
                        "name": "community.general",
                        "version": "4.6.1"
                    },
                    {
                        "name": "community.vmware",
                        "version": "2.7.0"
                    },
                    {
                        "name": "google.cloud",
                        "version": "1.0.2"
                    },
                    {
                        "name": "kubernetes.core",
                        "version": "2.3.0"
                    },
                    {
                        "name": "openstack.cloud",
                        "version": "1.7.2"
                    }
                ],
                "roles": [
                    {
                        "name": "ftl-injector",
                        "src": "https://github.com/redhat-gpte-devopsautomation/ftl-injector",
                        "version": "v0.17"
                    }
                ]
            },
            "installed_collections":
            {
                "/usr/share/ansible/collections/ansible_collections": {

                "community.general": {
                    "version": "6.3.0"
                },
                    "community.aws": {
                        "version": "5.2.0"
                    },
                    "ansible.utils": {
                        "version": "2.9.0"
                    },
                    "ansible.netcommon": {
                        "version": "4.1.0"
                    },
                    "ansible.posix": {
                        "version": "1.5.1"
                    },
                    "amazon.aws": {
                        "version": "5.2.0"
                    },
                    "kubernetes.core": {
                        "version": "2.4.0"
                    },
                    "azure.azcollection": {
                        "version": "1.14.0"
                    },
                    "openstack.cloud": {
                        "version": "2.0.0"
                    }
                }
            }
            ,
            "result":
            {
                "collections": [
                    {
                        "name": "community.vmware",
                        "version": "2.7.0"
                    },
                    {
                        "name": "google.cloud",
                        "version": "1.0.2"
                    },
                ],
                "roles": [
                    {
                        "name": "ftl-injector",
                        "src": "https://github.com/redhat-gpte-devopsautomation/ftl-injector",
                        "version": "v0.17"
                    }
                ]
            },
        },
    ]

    for tc in testcases:
        assert(
            core.agnosticd_filter_out_installed_collections(
                tc["requirements"], tc["installed_collections"]) == tc["result"]
        )
