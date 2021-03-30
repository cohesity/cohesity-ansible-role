#!/usr/bin/python
# Copyright (c) 2018 Cohesity Inc
# Apache License Version 2.0

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'supported_by': 'community',
    'status': ['preview']
}

DOCUMENTATION = '''
module: cohesity_win_agent
short_description: Management of Cohesity Physical Windows Agent
description:
    - Ansible Module used to deploy or remove the Cohesity Physical Agent from supported Windows Machines.
    - When executed in a playbook, the Cohesity Agent installation will be validated and the appropriate
    - state action will be applied.  The most recent version of the Cohesity Agent will be automatically
    - downloaded to the host.
version_added: '2.6.5'
author: 'Jeremy Goodrum (github.com/goodrum)'

options:
  state:
    description:
      - Determines if the agent should be C(present) or C(absent) from the host
    choices:
      - present
      - absent
    default: 'present'
  service_user:
    description:
      - Username with which Cohesity Agent will be installed
  service_password:
    description:
      - Password belonging to the selected Username.  This parameter will not be logged.
  install_type:
    description:
      - Installation type for the Cohesity Agent on Windows
    choices:
      - volcbt
      - fscbt
      - allcbt
      - onlyagent
    default: 'volcbt'
  preservesettings:
    description:
      - Should the settings be retained when uninstalling the Cohesity Agent
    type: bool
    default: 'no'


extends_documentation_fragment:
    - cohesity
requirements: []
'''

EXAMPLES = '''
# Install the current version of the agent on Windows
- cohesity_win_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present

# Install the current version of the agent with custom Service Username/Password
- cohesity_win_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present
    service_user: cagent
    service_password: cagent

# Install the current version of the agent using FileSystem ChangeBlockTracker
- cohesity_win_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present
    install_type: fscbt
'''

RETURN = '''
'''
