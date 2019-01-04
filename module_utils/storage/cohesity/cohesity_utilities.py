#
# cohesity_authentication
#
# Copyright (c) 2018 Cohesity Inc
# Apache License Version 2.0
#


'''
The **CohesityUtilities** utils module provides the authentication token manage
for Cohesity Platforms.
'''


def cohesity_common_argument_spec():
    return dict(
        cluster=dict(type='str'),
        username=dict(type='str', aliases=['cohesity_user', 'admin_name']),
        password=dict(type='str', aliases=['cohesity_password',
                                           'admin_pass'], no_log=True),
        validate_certs=dict(default=True, type='bool'),
        state=dict(choices=['present', 'absent'], default='present')
    )


def raise__cohesity_exception__handler(error, module, message=""):
    if not message:
      message = "Unexpected error caused while managing the Cohesity Module."

    module.fail_json(msg=message,
                     error_details=str(error),
                     error_class=type(error).__name__)
