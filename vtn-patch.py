#! /usr/bin/python

import os
import re
import sys
import copy
import json
import time
from base64 import b64encode
from subprocess import Popen, PIPE

DEV_ID = ''

def curl(url, method="GET", headers=["Accept: application/json"], data=None):
    " Simple cURL wrapper "
    # url: ONOS API endpoint
    # method: HTTP request method (GET/POST/PUT/DELETE)
    # header: list contains multiple headers for request

    if method in ["GET", "DELETE"] and data:
        raise Exception("GET/DELETE method don't allow data streaming.")

    headers = ["-H '%s'" % header for header in headers]
    headers_str = " ".join(headers)

    command = "curl -v -X {method} {headers}"
    command = command.format(method=method, headers=headers_str)

    if data:
        command += " -d '{data}'".format(data=json.dumps(data))

    command += " {url}".format(url=url)

    print(command)

    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()

    ret_val = json.loads(stdout) if method in ["GET"] else ""

    return ret_val

def headnode_ip():
    " Get headnode IP address from ~/.ssh/config "

    HOME = os.getenv('HOME')


    with open("%s/.ssh/config" % HOME, "r") as openfile:
        config = openfile.read()

    pattern = r"Host head1\n  HostName (\d+\.\d+\.\d+\.\d+)"
    result = re.search(pattern, config)

    if not result:
        sys.exit("Can't find ~/.ssh/config")

    return result.groups(1)[0]

def parse_hostdata(data):
    " Get Host mac, ipaddr pair as dictionary "

    hosts = {d["mac"]: d["ipAddresses"][0] for d in data["hosts"]}
    return hosts

def parse_groupdata(data):

    group_data = list()

    for group in data['groups']:
        if not group['buckets']:
            continue

        info = {
            'deviceId': group['deviceId'],
            'appCookie': group['appCookie'],
            'groupId': group['givenGroupId'],
            'buckets': [],
        }

        for bucket in group['buckets']:
            bucket_info = {
                'mac': bucket['treatment']['instructions'][0]['mac'],
                'port': bucket['treatment']['instructions'][1]['port']
            }

            info['buckets'].append(bucket_info)

        group_data.append(info)

    return group_data

def update_groupdata(hostdata, groupdata):
    BUCKET_TEMPLATE = {
        'weight': 1,
        'treatment': {
            'instructions': [
                {
                    'type': 'L2MODIFICATION',
                    'subtype': 'ETH_DST',
                    'mac': ''
                },
                {
                    'type': 'L3MODIFICATION',
                    'subtype': 'IPV4_DST',
                    'ip': ''
                },
                {
                    'type': 'OUTPUT',
                    'port': ''
                }
            ]
        }
    }
    GROUP_TEMPLATE = {
        'type': 'SELECT',
        'appCookie': '',
        'groupId': '',
        'buckets': []
    }

    group_postdata = list()

    for data in groupdata:
        gd = copy.deepcopy(GROUP_TEMPLATE)
        gd['appCookie'] = data['appCookie'].encode()
        gd['groupId'] = data['groupId'].encode()
        gd['deviceId'] = data['deviceId'].encode()

        for bucketdata in data['buckets']:
            bucket = copy.deepcopy(BUCKET_TEMPLATE)
            instruction = bucket['treatment']['instructions']

            # Replace mac, ip, port information into instruction
            instruction[0]['mac'] = bucketdata['mac'].encode()
            instruction[1]['ip'] = hostdata[bucketdata['mac']].encode()
            instruction[2]['port'] = bucketdata['port'].encode()

            gd['buckets'].append(bucket)

        group_postdata.append(gd)

    return group_postdata


def handshake_patch(src_net, dst_net, src_gw):

    FLOW_TEMPLATE = {
        "flows": [
        {
            "priority": 6000,
            "timeout": 0,
            "isPermanent": true,
            "deviceId": "%s" % DEV_ID,
            "treatment": {
                "instructions": [
                    {
                        "type":"L3MODIFICATION",
                        "subtype":"IPV4_SRC",
                        "ip": "%s" % src_gw
                    },
                    {
                        "type": "TABLE",
                        "port": "4"
                    }
                ]
            },
            "selector": {
                "criteria": [
                    {
                        "type": "ETH_TYPE",
                        "ethType": "0x0800"
                    },
                    {
                        "type": "IPV4_SRC",
                        "ip": "%s" % src_net
                    },
                    {
                        "type": "IPV4_DST",
                        "ip": "%s" % dst_net
                    }
                ]
            }
        }
    }

    return FLOW_TEMPLATE


if __name__ == '__main__':
    # Get Head Node IP Address and select connect port number
    ip = headnode_ip()
    port = 8182

    # Define ONOS API URL and apipoint
    ONOS_URL = 'http://{ip}:{port}/onos/v1/'.format(ip=ip, port=port)
    DEVICEAPI_URL = ONOS_URL + 'devices'
    HOSTAPI_URL = ONOS_URL + 'hosts'
    FLOWAPI_URL = ONOS_URL + 'flows'
    GROUPAPI_URL = ONOS_URL + 'groups'

    credit = b64encode("onos:rocks")

    # Header used with no streaming data, e.g.: GET, DELETE 
    header1 = [
        "Accept: application/json",
        "Authorization: Basic {credit}".format(credit=credit),
    ]

    # Header used with streaming data, e.g.: PUT, POST
    header2 = [
        "Accept: application/json",
        "Content-type: application/json",
        "Authorization: Basic {credit}".format(credit=credit),
    ]

    # Get First Available OVS's Device ID
    global DEV_ID
    devices = curl(DEVICEAPI_URL, headers=header1)["devices"]
    device = filter(lambda x: x["available"] is True, devices).next()
    DEV_ID = device["id"]

    # Get Host data in {mac: ip} dictionary
    hostdata = parse_hostdata(curl(HOSTAPI_URL, headers=header1))

    # Get Group data
    groupdata = parse_groupdata(curl(GROUPAPI_URL, headers=header1))

    # DELETE current Group data
    for group in groupdata:
        DELETE_URL = GROUPAPI_URL + '/{devid}/{appcookie}'.format(
            devid=group['deviceId'], appcookie=group['appCookie']
        )

        curl(DELETE_URL, method='DELETE', headers=header1)

    group_postdata = update_groupdata(hostdata, groupdata)

    # CREATE new Group data
    for group in group_postdata:
        devid = group.pop('deviceId')
        CREATE_URL = GROUPAPI_URL + '/{devid}'.format(devid=devid)

        curl(GROUPAPI_URL, headers=header1)
        curl(CREATE_URL, method='POST', headers=header2, data=group)

    handshake_patch_data = [
        ('10.0.6.0/24', '10.0.5.0/24', '10.0.6.1'),
        ('10.0.8.0/24', '10.0.5.0/24', '10.0.8.1'),
        ('10.0.7.0/24', '10.0.6.0/24', '10.0.7.1'),
        ('10.0.8.0/24', '10.0.6.0/24', '10.0.8.1')
    ]

    FLOW_CREATE_URL = FLOWAPI_URL + '?appId=87'

    for data in handshake_patch_data:
        flow = handshake_patch(data)
        curl(FLOW_CREATE_URL, method='POST', headers=header2, data=flow)
