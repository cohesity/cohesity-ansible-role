#!/usr/bin/python
# Copyright (c) 2019 Cohesity Inc
# Apache License Version 2.0

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import time
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url, urllib_error

try:
    # => When unit testing, we need to look in the correct location however, when run via ansible,
    # => the expectation is that the modules will live under ansible.
    from module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec,\
        raise__cohesity_exception__handler
except Exception as e:
    from ansible.module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec,\
        raise__cohesity_exception__handler


RETRY = 5
REQUEST_TIMEOUT = 120
SLEEP_INTERVAL = 120
OK_SUCCESS_STATUS_CODE = 200
ACCEPTED_STATUS_CODE = 202
INTERNAL_ERROR_STATUS_CODE = 500
NO_CONTENT_STATUS_CODE = 204


DOCUMENTATION = '''
module: cohesity_virtual_cluster
short_description: create and destroy virtual edition cluster
description:
    - This module is used to create and destroy virtual edition cluster.
version_added: '2.6.5'
options:
  cohesity_server:
    description:
      - The cluster vip or FQDN
    required: yes
  cohesity_admin:
    description:
      - Cohesity cluster username
    required: yes
  cohesity_password:
    description:
      - Cohesity cluster password
      required: yes
  cohesity_validate_certs:
    description:
      - determines whether SSL Validation is enabled or not
    default: False
  state:
    description:
      - Defines the state of the cluster. 'present' creates the cluster and 'absent' destroys the cluster
    default: present
    choices:
        - present
        - absent
  cluster_name:
    description:
      - The name of the new Virtual edition cluster
    required: yes
  metadata_fault_tolerance:
    description:
      - The metadata fault tolerance
    default: 0
  enable_encryption:
    description:
      - Specifies whether or not to enable encryption. If encryption is enabled, all data on the cluster will be encrypted
    default: True
  enable_fips_mode:
    description:
      - Specifies whether or not to enable FIPS mode. This must be set to true in order to enable FIPS
    default: True
  encryption_keys_rotation_period:
    description:
      - The rotation period for encryption keys in days
    default: 1
  cluster_gateway:
    description:
      - The default gateway IP address for the cluster network
    required: yes
  cluster_subnet_mask:
    description:
      - The subnet mask of the cluster network
    required: yes
  domain_names:
    description:
      - List of domain names to configure on the cluster
    required: yes
  ntp_servers:
    description:
      - List NTP servers to configure on the cluster
    required: yes
  dns_servers:
    description:
      - List DNS servers to configure on the cluster
    required: yes
  virtual_ips:
    description:
      - List of virtual IPs for the new cluster
    required: yes
  virtual_ip_hostname:
    description:
      - The virtual IP hostname
    required: yes
  nodes_ip:
    description:
      - List of nodes ip addresses
    required: yes
  wait:
    description:
      - Boolean value to either wait or not wait for cluster creation or deletion.
    default: True
  wait_minutes:
    description:
      - Wait time in minutes
    default: 120
'''


def get_cluster_details(module, token):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    try:
        uri = "https://" + server + \
            "/irisservices/api/v1/public/basicClusterInfo"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token}
        response = open_url(url=uri, method='GET', headers=headers,
                            validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)
        if not response.getcode() == OK_SUCCESS_STATUS_CODE:
            return str(response.read), response.getcode()
        return json.loads(response.read()), OK_SUCCESS_STATUS_CODE
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        return str(e), INTERNAL_ERROR_STATUS_CODE
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def wait(module, token):
    if module.params.get('wait'):
        timeout = module.params.get('wait_minutes')
        while timeout > 0:
            cluster_details, status_code = get_cluster_details(
                module, token)
            if status_code == OK_SUCCESS_STATUS_CODE and 'name' in cluster_details:
                break
            time.sleep(SLEEP_INTERVAL)
            timeout = timeout - 2


def create_virtual_cluster(module, token):
    global RETRY
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    try:
        uri = "https://" + server + \
              "/irisservices/api/v1/public/clusters/virtualEdition"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token}
        payload = dict()
        payload['clusterName'] = module.params.get('cluster_name')
        payload['metadataFaultTolerance'] = module.params.get(
            'metadata_fault_tolerance')
        payload['encryptionConfig'] = {
            "enableEncryption": module.params.get('enable_encryption'),
            "enableFipsMode": module.params.get('enable_fips_mode'),
            "rotationPeriod": module.params.get('encryption_keys_rotation_period')
        }
        payload['networkConfig'] = {
            'clusterGateway': module.params.get('cluster_gateway'),
            'clusterSubnetMask': module.params.get('cluster_subnet_mask'),
            'dnsServers': module.params.get('dns_servers'),
            'domainNames': module.params.get('domain_names'),
            'ntpServers': module.params.get('ntp_servers'),
            'vipHostname': module.params.get('virtual_ip_hostname'),
            'vips': module.params.get('virtual_ips'),
        }
        payload['nodeConfigs'] = []
        for node_ip in module.params.get('nodes_ip'):
            payload['nodeConfigs'].append({'nodeIp': node_ip})

        response = open_url(url=uri, method='POST', data=json.dumps(payload), headers=headers,
                            validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)
        if not response.getcode() == ACCEPTED_STATUS_CODE:
            module.fail_json(
                changed=False,
                msg="Failed to create virtual edition cluster",
                **(json.loads(response.read())))
        wait(module, token)
        return json.loads(response.read())
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        error_message = str(e.read())
        if 'Node is already part of a cluster' in error_message:
            wait(module, token)
            return {"name": module.params.get('cluster_name')}
        elif 'timeout' in error_message and RETRY > 0:
            RETRY = RETRY - 1
            create_virtual_cluster(module, token)
        else:
            raise__cohesity_exception__handler(error_message, module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def destroy_virtual_cluster(module, token):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    try:
        uri = "https://" + server + \
            "/irisservices/api/v1/public/clusters"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token}
        response = open_url(url=uri, method='DELETE', headers=headers,
                            validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)
        if not response.getcode() == NO_CONTENT_STATUS_CODE:
            module.fail_json(
                changed=False,
                msg="Failed to destroy virtual edition cluster",
                **(json.loads(response.read())))

        if module.params.get('wait'):
            timeout = module.params.get('wait_minutes')
            while timeout > 0:
                cluster_details, status_code = get_cluster_details(
                    module, token)
                if status_code == OK_SUCCESS_STATUS_CODE and 'name' not in cluster_details:
                    break
                time.sleep(SLEEP_INTERVAL)
                timeout = timeout - 2
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def main():
    # => Load the default arguments.
    argument_spec = cohesity_common_argument_spec()
    argument_spec.update(
        dict(
            state=dict(choices=['present', 'absent'], default='present'),
            cluster_name=dict(type='str', required=True),
            metadata_fault_tolerance=dict(type=int, default=0),
            enable_encryption=dict(type=bool, default=True),
            enable_fips_mode=dict(type=bool, default=True),
            encryption_keys_rotation_period=dict(type=int, default=1),
            cluster_gateway=dict(type=str, required=True),
            cluster_subnet_mask=dict(type=str, required=True),
            domain_names=dict(type=list, required=True),
            ntp_servers=dict(type=list, required=True),
            dns_servers=dict(type=list, required=True),
            virtual_ips=dict(type=list, required=True),
            virtual_ip_hostname=dict(required=True),
            nodes_ip=dict(type=list, required=True),
            wait=dict(type=bool, default=True),
            wait_minutes=dict(type=int, default=120)
        )
    )
    # => Create a new module object
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    results = dict(
        changed=False,
        msg="Attempting to manage Cohesity Virtual edition cluster",
        state=module.params.get('state')
    )

    token = get__cohesity_auth__token(module)

    cluster_details, status_code = get_cluster_details(
        module, token)
    if not status_code == OK_SUCCESS_STATUS_CODE:
        module.fail_json(
            msg="Failed to get cluster details" +
                " .Reason: " + str(cluster_details),
            status_code=status_code,
            changed=False
        )
    if module.check_mode:
        check_mode_results = dict(
            changed=False,
            msg="Check Mode: Cohesity virtual edition cluster doesn't exist",
            name="")
        if module.params.get('state') == "present":
            if 'name' in cluster_details:
                check_mode_results[
                    'msg'] = "Check Mode: Cohesity Virtual edition cluster already exists.  No changes"
                check_mode_results['name'] = cluster_details['name']
            else:
                check_mode_results[
                    'msg'] = "Check Mode: Cohesity Virtual edition doesn't exist. This action would create the cluster."
                check_mode_results['changed'] = True
        else:
            if 'name' in cluster_details:
                check_mode_results[
                    'msg'] = "Check Mode: Cohesity Virtual edition cluster exists. This action would destroy the cluster"
                check_mode_results['name'] = cluster_details['name']
                check_mode_results['changed'] = True
            else:
                check_mode_results[
                    'msg'] = "Check Mode: Cohesity Virtual edition doesn't exist. No changes."
        module.exit_json(**check_mode_results)

    elif module.params.get('state') == "present":
        if 'name' in cluster_details:
            results = dict(
                changed=False,
                msg="The Virtual edition cluster already exists",
                **cluster_details)
        else:
            response = create_virtual_cluster(module, token)
            results = dict(
                changed=True,
                msg="Successfully created the Virtual edition cluster",
                **response)
    elif module.params.get('state') == "absent":
        if 'name' in cluster_details:
            destroy_virtual_cluster(module, token)
            results = dict(
                changed=True,
                msg="The Virtual edition cluster is destroyed",
                name=cluster_details['name'])
        else:
            results = dict(
                changed=False,
                msg="The Virtual edition cluster doesn't exist"
            )
    else:
        # => This error should never happen based on the set assigned to the parameter.
        # => However, in case, we should raise an appropriate error.
        module.fail_json(msg="Invalid State selected: {0}".format(
            module.params.get('state')), changed=False)

    module.exit_json(**results)


if __name__ == '__main__':
    main()
