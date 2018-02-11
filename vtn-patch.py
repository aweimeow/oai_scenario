#! /usr/bin/python

import re
import sys
import json
from base64 import b64encode
from subprocess import Popen, PIPE

def curl(url, method="GET", headers=["Accept: application/json"], data=None):
    " Simple cURL wrapper "
    # url: ONOS API endpoint
    # method: HTTP request method (GET/POST/PUT/DELETE)
    # header: list contains multiple headers for request

    if method in ["GET", "DELETE"] and data:
        raise Exception("GET/DELETE method don't allow data streaming.")

    headers = ["-H %s" % header for header in headers]
    headers_str = " ".join(headers)

    command = "curl -X {method} '{headers}'"
    command = command.format(method=method, headers=headers_str)

    if data:
        command += " -d '{data}'".format(data=data)

    command += " {url}".format(url=url)

    p = Popen(command.split(), stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()

    return json.decode(stdout)

def headnode_ip():
    " Get headnode IP address from ~/.ssh/config "

    with open("~/.ssh/config", "r") as openfile:
        config = openfile.read()

    pattern = r"Host head1\n  HostName (\d+\.\d+\.\d+\.\d+)"
    result = re.search(pattern, config)

    if not result:
        sys.exit("Can't find ~/.ssh/config")

    return result.groups(1)

def parse_hostdata(data):
    " Get Host mac, ipaddr pair as dictionary "

    hosts = [{d["mac"]: d["ipAddresses"][0]} for d in data["hosts"]]
    return hosts

def parse_groupdata(data):

    group_data = list()

    for group in data['groups'][1:]:
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
        gd = GROUP_TEMPLATE.copy()
        gd['appCookie'] = data['appCookie']
        gd['groupId'] = data['groupId']
        gd['deviceId'] = data['deviceId']

        for bucketdata in data['buckets']:
            bucket = BUCKET_TEMPLATE.copy()
            instruction = bucket['treatment']['instructions']

            # Replace mac, ip, port information into instruction
            instruction[0]['mac'] = bucketdata['mac']
            instruction[1]['ip'] = hostdata[bucketdata['mac']]
            instruction[2]['port'] = bucketdata['port']

            gd['buckets'].append(bucket)

        group_postdata.append(gd)

    return group_postdata

if __name__ == '__main__':
    # Get Head Node IP Address and select connect port number
    ip = headnode_ip()
    port = 8182

    # Define ONOS API URL and apipoint
    ONOS_URL = 'http://{ip}:{port}/onos/v1/'.format(ip=ip, port=port)
    HOSTAPI_URL = ONOS_URL + 'hosts'
    GROUPAPI_URL = ONOS_URL + 'groups'

    credit = b64encode("onos:rocks")

    headers = [
        "Accept: application/json",
        "Authorization: {credit}" % credit,
    ]

    # Get Host data in {mac: ip} dictionary
    hostdata = parse_hostdata(curl(HOSTAPI_URL, headers=headers))

    # Get Group data
    groupdata = parse_groupdata(curl(GROUPAPI_URL, headers=headers))

    # DELETE current Group data
    for group in groupdata:
        DELETE_URL = GROUPAPI_URL + '/{devid}/{appcookie}'.format(
            devid=group['deviceId'], appcookie=group['appCookie']
        )

        curl(DELETE_URL, method='DELETE', headers=headers)

    group_postdata = update_groupdata(hostdata, groupdata)

    # CREATE new Group data
    for group in group_postdata:
        CREATE_URL = GROUPAPI_URL + '/{devid}'.format(devid=group['deviceId'])

        curl(CREATE_URL, method='POST', headers=headers, data=group)
