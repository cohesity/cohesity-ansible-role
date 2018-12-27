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
    from module_utils.storage.cohesity.cohesity_hints import get__cluster, get__nodes, \
        get__prot_source__all, get__prot_policy__all, get__prot_job__all, \
        get__storage_domain_id__all, get__protection_run__all

except:
    from ansible.module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec
    from ansible.module_utils.storage.cohesity.cohesity_hints import get__cluster, get__nodes, \
        get__prot_source__all, get__prot_policy__all, get__prot_job__all, \
        get__storage_domain_id__all, get__protection_run__all

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


options:
  state:
    description:
      - Determines the level of data collection to perform. Complete will gather all details
      - currently supported by the module.  Minimal will gather basic cluster information but
      - not gather details about source, jobs, or executions.
    choices:
      - complete
      - minimal
    default: complete
  include_sources:
    description:
      - When True, will return the details about all registered Protection Sources.  This value
      - is skipped when the C(state=complete)
    type: bool
    default: no
  include_jobs:
    description:
      - When True, will return the details about all registered Protection Jobs.  This value
      - is skipped when the C(state=complete)
    type: bool
    default: no
  include_runs:
    description:
      - When True, will return the details about all registered Protection Job executions.  This value
      - is skipped when the C(state=complete)
    type: bool
    default: no
  active_only:
    description:
      - When True, will return only the actively running Protection Job executions.  This value
      - will filter the Protection Job executions data if I(active_only=yes)
    type: bool
    default: no
  include_deleted:
    description:
      - When True, will return all details about all registered Protection data included items marked deleted.  This value
      - will filter the Protection Sources, Jobs, and Executions data and return only current information if I(include_deleted=no)
    type: bool
    default: no

extends_documentation_fragment:
    - cohesity
requirements: []
'''

EXAMPLES = '''
# Gather facts about all nodes and supported resources in a cluster
- cohesity_facts:
    cluster: cohesity.lab
    username: admin
    password: password

# Gather facts about all nodes and protection sources in a cluster
- cohesity_facts:
    cluster: cohesity.lab
    username: admin
    password: password
    state: minimal
    include_sources: True

# Gather facts about all nodes and return active job executions in a cluster
- cohesity_facts:
    cluster: cohesity.lab
    username: admin
    password: password
    state: minimal
    include_runs: True
    active_only: True

'''

RETURN = '''
{
  "cluster": {
    "nodes": [
          # Array of Cohesity Node Details
    ],
    "protection": {
      "jobs": [
        # Array of Job Details
      ],
      "policies": [
        # Array of Backup Policy Information
      ],
      "runs": [
        # Array of Backup executions
      ],
      "sources": {
        "GenericNas": [
          # Array of GenericNas Protection Sources
        ],
        "Physical": [
          # Array of Physical Protection Sources
        ],
        "VMware":  [
          # Array of VMware Protection Sources
        ],
      }
    },
    "storage_domains": [
          # Array of Cohesity Backup Storage Domains
    ],
  }
}

'''


class FactsError(Exception):
    pass


def main():
    argument_spec = cohesity_common_argument_spec()
    argument_spec.update(
        dict(
            state=dict(choices=['complete', 'minimal'], default='complete'),
            include_sources=dict(type='bool', default=False),
            include_jobs=dict(type='bool', default=False),
            include_runs=dict(type='bool', default=False),
            active_only=dict(type='bool', default=False),
            include_deleted=dict(type='bool', default=False)
        )
    )

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
        active_only=module.params.get('active_only'),
        is_deleted=module.params.get('is_deleted')
    )
    params['token'] = get__cohesity_auth__token(module)
    try:
        include_sources = True
        include_jobs = True
        include_runs = True
        if module.params.get('state') == 'complete':
            pass
        else:
            if module.params.get('include_sources'):
                include_sources = True
            if module.params.get('include_jobs'):
                include_jobs = True
            if module.params.get('include_runs'):
                include_runs = True

        results['cluster'] = get__cluster(params)
        results['cluster']['nodes'] = get__nodes(params)

        # => Create a root node for all protection related items
        results['cluster']['protection'] = dict()

        # => We will group each Protection Source based on the
        # => environment type so to do this, we will declare
        # => sources as a dictionary.
        results['cluster']['protection']['sources'] = dict()

        # => Iterate each supported Environment type and collect each grouped
        # => by type.
        if include_sources:
            env_types = ['Physical', 'VMware', 'GenericNas']
            for env_type in env_types:
                params['environment'] = env_type
                results['cluster']['protection'][
                    'sources'][env_type] = get__prot_source__all(params)
                # => Let's remove this key since it is not needed for further processing.
                params.pop('environment')

        # => Collect all Cohesity Protection Policies
        results['cluster']['protection'][
            'policies'] = get__prot_policy__all(params)

        # => Collect all registered Protection Jobs
        # => This value can be filtered by choosing
        # => `active_only=True/False` and/or `is_deleted=True/False`
        if include_jobs:
            results['cluster']['protection'][
                'jobs'] = get__prot_job__all(params)

        # => Collect all Storage Domains
        results['cluster'][
            'storage_domains'] = get__storage_domain_id__all(params)

        # => Collect all Protection Jobs execution details
        # => This value can be filtered by choosing
        # => `active_only=True/False` and/or `is_deleted=True/False`
        if include_runs:
            results['cluster']['protection'][
                'runs'] = get__protection_run__all(params)

    except Exception as error:
        module.fail_json(msg="Failure while collecting Cohesity Facts",
                         exception=traceback.format_exc())
    module.exit_json(**results)


if __name__ == '__main__':
    main()
