#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'supported_by': 'community',
    'status': ['preview']
}

DOCUMENTATION = '''
module: cohesity_facts
short_description: Gather facts about a Cohesity Cluster.
description:
    - Gather facts about Cohesity Clusters.
version_added: '2.6.5'
author: 'Jeremy Goodrum (github.com/goodrum)'

extends_documentation_fragment:
    - cohesity
requirements: []
'''

EXAMPLES = '''
# Gather facts about all nodes and select resources in a cluster
- cohesity_facts:
    server: cohesity.lab
    username: admin
    password: password
'''

RETURN = '''
nodes:
    returned: on success
    description: >
        Nodes and information for members of the selected Cohesity Server.
    type: list
    sample: "[
  {
    "capacityByTier": [
      {
        "storageTier": 0,
        "tierMaxPhysicalCapacityBytes": 0
      }
    ],
    "chassisInfo": {
      "chassisId": 0,
      "chassisName": "string",
      "location": "string",
      "rackId": 0
    },
    "clusterPartitionId": 0,
    "clusterPartitionName": "string",
    "diskCount": 0,
    "id": 0,
    "ip": "string",
    "isMarkedForRemoval": true,
    "maxPhysicalCapacityBytes": 0,
    "nodeHardwareInfo": {
      "cpu": "string",
      "memorySizeBytes": 0,
      "network": "string"
    },
    "nodeIncarnationId": 0,
    "nodeSoftwareVersion": "string",
    "offlineMountPathsOfDisks": [
      "string"
    ],
    "removalState": "kDontRemove",
    "stats": {
      "id": 0,
      "usagePerfStats": {
        "dataInBytes": 0,
        "dataInBytesAfterReduction": 0,
        "minUsablePhysicalCapacityBytes": 0,
        "numBytesRead": 0,
        "numBytesWritten": 0,
        "physicalCapacityBytes": 0,
        "readIos": 0,
        "readLatencyMsecs": 0,
        "systemCapacityBytes": 0,
        "systemUsageBytes": 0,
        "totalPhysicalRawUsageBytes": 0,
        "totalPhysicalUsageBytes": 0,
        "writeIos": 0,
        "writeLatencyMsecs": 0
      }
    },
    "systemDisks": [
      {
        "devicePath": "string",
        "id": 0,
        "offline": true
      }
    ]
  }
]"
'''
# NOTE: Required to find the location of the modules when testing
# TODO:  Strip this from the final

import json
import traceback
from ansible.module_utils.urls import open_url, urllib_error
try:
    # => TODO:  Find a better way to handle this!!!
    # => When unit testing, we need to look in the correct location however, when run via ansible,
    # => the expectation is that the modules will live under ansible.
    from module_utils.storage.cohesity.cohesity_auth import Authentication, TokenException, ParameterViolation
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec
except:
    from ansible.module_utils.storage.cohesity.cohesity_auth import Authentication, TokenException, ParameterViolation
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec


class FactsError(Exception):
    pass


def get_cluster(module):

    server = module.params.get('server')
    validate_certs = module.params.get('validate_certs')
    auth = Authentication()
    auth.username = module.params.get('username')
    auth.password = module.params.get('password')
    token = auth.get_token(server)

    try:
        uri = "https://" + server + "/irisservices/api/v1/public/basicClusterInfo"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token}
        cluster = open_url(url=uri, headers=headers,
                           validate_certs=validate_certs)
        cluster = json.loads(cluster.read())
    except urllib_error.HTTPError as e:
        try:
            msg = json.loads(e.read())['message']
        except:
            # => For HTTPErrors that return no JSON with a message (bad errors), we
            # => will need to handle this by setting the msg variable to some default.
            msg = "no-json-data"
        else:
            raise FactsError(e)
    return cluster


def get_nodes(module):

    server = module.params.get('server')
    validate_certs = module.params.get('validate_certs')
    auth = Authentication()
    auth.username = module.params.get('username')
    auth.password = module.params.get('password')
    token = auth.get_token(server)

    try:
        uri = "https://" + server + "/irisservices/api/v1/public/nodes"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token}
        nodes = open_url(url=uri, headers=headers,
                         validate_certs=validate_certs)
        nodes = json.loads(nodes.read())
    except urllib_error.HTTPError as e:
        try:
            msg = json.loads(e.read())['message']
        except:
            # => For HTTPErrors that return no JSON with a message (bad errors), we
            # => will need to handle this by setting the msg variable to some default.
            msg = "no-json-data"
        else:
            raise FactsError(e)
    return nodes


def main():
    argument_spec = cohesity_common_argument_spec()
    module = AnsibleModule(argument_spec=argument_spec)
    results = dict(
        changed=False,
        cluster=''
    )
    try:
        results['cluster'] = get_cluster(module)
        results['cluster']['nodes'] = get_nodes(module)
    except Exception as error:
        module.fail_json(msg="Something went wrong",
                         exception=traceback.format_exc())
    module.exit_json(**results)


if __name__ == '__main__':
    main()
