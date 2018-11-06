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
  cluster:
    description:
      - IP or FQDN for the Cohesity Cluster
    required: true
  cohesity_admin:
    description:
      - Username with which Ansible will connect to the Cohesity Cluster
    required: true
  cohesity_password:
    description:
      - Password belonging to the selected Username.  This parameter will not be logged.
    required: true
  validate_certs:
    description:
      - Switch determines if SSL Validation should be enabled.
    type: bool
    default: False

requirements:
  - A physical or virtual Cohesity system. The modules were developed with Cohesity version 6.1.0
  - Ansible 2.6
  - Python >= 2.6

notes:
  - Currently, the Ansible Module requires Full Cluster Administrator access.
"""
