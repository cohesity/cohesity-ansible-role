#
# cohesity_authentication
#
# Copyright (c) 2022 Cohesity Inc
# Apache License Version 2.0
#


DOCUMENTATION = '''
module_utils: cohesity_utilities
author:
  - Naveena (naveena.maplelabs@cohesity.com)
short_description: The **CohesityUtilities** utils module provides the authentication token manage
for Cohesity Platforms.
version_added: 1.0.0
description:
    - The **CohesityUtilities** utils module provides the authentication token manage
for Cohesity Platforms.
'''


def cohesity_common_argument_spec():
    return dict(
        cluster=dict(type='str', aliases=['cohesity_server']),
        username=dict(type='str', aliases=['cohesity_user', 'admin_name', 'cohesity_admin']),
        password=dict(type='str', aliases=['cohesity_password',
                                           'admin_pass'], no_log=True),
        validate_certs=dict(default=True, type='bool', aliases=['cohesity_validate_certs']),
        state=dict(choices=['present', 'absent'], default='present')
    )


def raise__cohesity_exception__handler(error, module, message=""):
    if not message:
        message = "Unexpected error caused while managing the Cohesity Module."

    module.fail_json(msg=message,
                     error_details=str(error),
                     error_class=type(error).__name__)


# constants
REQUEST_TIMEOUT = 120
