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
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler
except Exception as e:
    from ansible.module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler


DOCUMENTATION = '''
module: cohesity_license
short_description: Apply license to Cohesity clusters
description:
    - This module is used to apply license to Cohesity clusters once they are created. The operation is idempotent
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
  license_key:
    description:
      - The license key to apply.
    required: yes
'''

REQUEST_TIMEOUT = 120
OK_SUCCESS_STATUS_CODE = 200
NO_CONTENT_STATUS_CODE = 204


def get_cluster_info(module, token):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    try:
        uri = "https://" + server + \
              "/irisservices/api/v1/public/cluster"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token}
        response = open_url(url=uri, method='GET', headers=headers,
                            validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)
        if not response.getcode() == OK_SUCCESS_STATUS_CODE:
            module.fail_json(
                changed=False,
                msg="Failed to get cluster information")
        return json.loads(response.read())
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def apply_cluster_license(module, token):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    try:
        uri = "https://" + server + \
              "/irisservices/api/v1/licenseAgreement"

        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token}
        payload = {
            'signedVersion': 2,
            'signedByUser': module.params.get('username'),
            'licenseKey': module.params.get('license_key'),
            'signedTime': int(time.time())
        }

        response = open_url(url=uri, method='POST', data=json.dumps(payload), headers=headers,
                            validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)
        if not response.getcode() == NO_CONTENT_STATUS_CODE:
            module.fail_json(
                changed=False,
                msg="Failed to apply cluster license",
                **(json.loads(response.read())))
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
            license_key=dict(required=True, no_log=True)
        )
    )
    # => Create a new module object
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    results = dict(
        changed=False,
        msg="Attempting to apply cluster license"
    )

    token = get__cohesity_auth__token(module)

    cluster_information = get_cluster_info(
        module, token)
    if module.check_mode:
        if 'eulaConfig' in cluster_information:
            check_mode_results = dict(msg='Check Mode: The cluster license is already applied. No changes',
                                      changed=False)
        else:
            check_mode_results = dict(msg='Check Mode: The cluster license is not applied. This action applies the'
                                      ' cluster license',
                                      changed=True)
        module.exit_json(**check_mode_results)

    if 'eulaConfig' in cluster_information:
        results = dict(
            changed=False,
            msg="The cluster license is already applied")
    else:
        apply_cluster_license(module, token)
        results = dict(
            changed=True,
            msg="The cluster license is applied successfully")
    module.exit_json(**results)


if __name__ == '__main__':
    main()
