# (c) 2018, Cohesity Inc
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.


class ModuleDocFragment(object):

    # Core Cohesity Options documentation fragment
    DOCUMENTATION = """
options:
  server:
    description:
      - IP or FQDN for the Cohesity Cluster
    aliases: ['Cohesity_server', 'cluster']
  username:
    description:
      - Username with which Ansible will connect to the Cohesity Cluster
    aliases: ['cohesity_user', 'admin_name']
  password:
    description:
      - Password belonging to the selected Username.  This parameter will not be logged.
    aliases: ['cohesity_password', 'admin_pass']
  validate_certs:
    description:
      - Switch determines if SSL Validation should be enabled.
    type: bool
    default: 'no'
  security_token:
    description:
      - Access Token with permisions to connect to the Cohesity Cluster.  This parameter will not be logged.
    aliases: ['access_token']
requirements:
  - "python >= 2.6"
notes:
  - "TODO: add notes"
"""
