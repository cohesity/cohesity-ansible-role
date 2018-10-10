#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'supported_by': 'community',
    'status': ['preview']
}

DOCUMENTATION = '''
module: cohesity_win_agent
short_description: Installs and Remove the Cohesity Agent on Windows Hosts.
description:
    - Installation and Management of the Cohesity Agent.
version_added: '2.6.5'
author: 'Jeremy Goodrum (github.com/goodrum)'

options:
  service_user:
    description:
      - Username with which Cohesity Agent will be installed
  service_password:
    description:
      - Password belonging to the selected Username.  This parameter will not be logged.
  install_type:
    description:
      - Installation type for the Cohesity Agent
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
  state:
    description:
      - Determines if the agent should be installed or removed
    choices:
      - present
      - absent


extends_documentation_fragment:
    - cohesity
requirements: []
'''

EXAMPLES = '''
# Install the current version of the agent on Linux
- cohesity_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present

# Install the current version of the agent with custom Service Username/Password
- cohesity_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present
    service_user: cagent
    service_password: cagent
'''

RETURN = '''
'''
