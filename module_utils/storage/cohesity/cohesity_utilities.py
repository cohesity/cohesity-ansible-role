#!/usr/bin/python
#
# cohesity_authentication
#
# Copyright information
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


def raise__cohesity_exception__handler(error, module):
        module.fail_json(msg="Unexpected error caused while managing the Cohesity Protection Source.",
                         error_details=str(error),
                         error_class=type(error).__name__)
