import base64
import json
import os

with open('bootstrap.ign', 'r') as f:
    ignition = json.load(f)

files = ignition['storage'].get('files', [])

infra_id = os.environ.get('INFRA_ID', 'openshift').encode()
hostname_b64 = base64.standard_b64encode(infra_id + b'-bootstrap\n').decode().strip()
files.append(
{
    'path': '/etc/hostname',
    'mode': 420,
    'contents': {
        'source': 'data:text/plain;charset=utf-8;base64,' + hostname_b64,
        'verification': {}
    },
    'filesystem': 'root',
})

dhcp_client_conf_b64 = base64.standard_b64encode(b'[main]\ndhcp=dhclient\n').decode().strip()
files.append(
{
    'path': '/etc/NetworkManager/conf.d/dhcp-client.conf',
    'mode': 420,
    'contents': {
        'source': 'data:text/plain;charset=utf-8;base64,' + dhcp_client_conf_b64,
        'verification': {}
        },
    'filesystem': 'root',
})

dhclient_cont_b64 = base64.standard_b64encode(b'send dhcp-client-identifier = hardware;\nprepend domain-name-servers 127.0.0.1;\n').decode().strip()
files.append(
{
    'path': '/etc/dhcp/dhclient.conf',
    'mode': 420,
    'contents': {
        'source': 'data:text/plain;charset=utf-8;base64,' + dhclient_cont_b64,
        'verification': {}
        },
    'filesystem': 'root'
})

ignition['storage']['files'] = files;

with open('bootstrap.ign', 'w') as f:
    json.dump(ignition, f)