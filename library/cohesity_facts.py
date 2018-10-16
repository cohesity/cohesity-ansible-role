#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

import json
import traceback
from ansible.module_utils.urls import open_url, urllib_error
try:
    # => TODO:  Find a better way to handle this!!!
    # => When unit testing, we need to look in the correct location however, when run via ansible,
    # => the expectation is that the modules will live under ansible.
    from module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec
    from module_utils.storage.cohesity.cohesity_hints import *
except:
    from ansible.module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec
    from ansible.module_utils.storage.cohesity.cohesity_hints import *

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


class FactsError(Exception):
    pass


def main():
    argument_spec = cohesity_common_argument_spec()
    module = AnsibleModule(argument_spec=argument_spec)
    results = dict(
        changed=False,
        cluster=''
    )
    params = dict(
        server=module.params.get('cluster'),
        username=module.params.get('username'),
        password=module.params.get('password'),
        validate_certs=module.params.get('validate_certs'),
        is_deleted=False
    )
    params['token'] = get__cohesity_auth__token(module)
    try:
        results['cluster'] = get__cluster(params)
        results['cluster']['nodes'] = get__nodes(params)
        results['cluster']['protection'] = dict()
        results['cluster']['protection']['sources'] = dict()
        env_types = ['GenericNas']
        for env_type in env_types:
            params['environment'] = env_type
            results['cluster']['protection'][
                'sources'][env_type] = get__prot_source__all(params)
        params.pop('environment')
        results['cluster']['protection'][
            'policies'] = get__prot_policy__all(params)
        results['cluster']['protection']['jobs'] = get__prot_job__all(params)
        results['cluster'][
            'storage_domains'] = get__storage_domain_id__all(params)
        results['cluster']['protection'][
            'runs'] = get__protection_run__all(params)

    except Exception as error:
        module.fail_json(msg="Failure while collecting Cohesity Facts",
                         exception=traceback.format_exc())
    module.exit_json(**results)


if __name__ == '__main__':
    main()
