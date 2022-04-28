#!/usr/bin/env python3


import pytest
from ansible.errors import AnsibleFilterError
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import agnosticd_requirements


def test_set_in_list():
    l = []
    testcases = [
        {
            'args': [{'name': 'foo', 'value': '123'}, l],
            'expected': [{'name': 'foo', 'value': '123'}],
        },
        {
            'args': [{'name': 'foo', 'value': '123'}, l],
            'expected': [{'name': 'foo', 'value': '123'}],
        },
        {
            'args': [{'name': 'foo2', 'value': '345'}, l],
            'expected': [
                {'name': 'foo', 'value': '123'},
                {'name': 'foo2', 'value': '345'},
            ],
        },
    ]

    for tc in testcases:
        agnosticd_requirements.set_in_list(*tc['args'])
        assert(l == tc['expected'])


def test_agnosticd_compile_requirements():
    testcases = [
        {
            'args': [
                {'roles': [{'name':'foo'}]},
                {},
            ],
            'expected': {
                'roles': [{'name':'foo'}],
            },
        },
        {
            'args': [
                {'roles': [{'name':'foo'}]},
                {'roles': [{'name':'foo'}]},
            ],
            'expected': {
                'roles': [{'name':'foo'}],
            },
        },
        {
            'args': [
                {'roles': [{'name':'foo', 'value': '2'}]},
                {'roles': [{'name':'foo', 'value': '3'}]},
            ],
            'expected': {
                'roles': [{'name':'foo', 'value': '3'}]
            },
        },
        {
            'args': [
                {'roles': [{'name':'foo', 'value': '2'}]},
                {'collections': [{'name':'foo', 'value': '3'}]},
            ],
            'expected': {
                'roles': [{'name':'foo', 'value': '2'}],
                'collections': [{'name':'foo', 'value': '3'}]
            },
        },
        {
            'args': [
                {'roles': [{'name':'foo', 'value': '2'}]},
                {'collections': [{'name':'foo', 'value': '3'}]},
                {'collections': [{'name':'foo', 'value': '4'}]},
                {'roles': [{'name':'foo', 'value': '4'}]},
                {'roles': [{'name':'foo2', 'value': '4'}]},
            ],
            'expected': {
                'roles': [
                    {'name':'foo', 'value': '4'},
                    {'name':'foo2', 'value': '4'},
                ],
                'collections': [{'name':'foo', 'value': '4'}]
            },
        },
    ]

    for tc in testcases:
        assert(agnosticd_requirements.agnosticd_compile_requirements(tc['args']) == tc['expected'])
