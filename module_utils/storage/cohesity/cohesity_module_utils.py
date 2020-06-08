# !/usr/bin/python
# Copyright (c) 2020 Cohesity Inc
# Apache License Version 2.0

from cohesity_management_sdk.cohesity_client import CohesityClient

try:
    from module_utils.storage.cohesity.cohesity_utilities import raise__cohesity_exception__handler
except Exception:
    from ansible.module_utils.storage.cohesity.cohesity_utilities import raise__cohesity_exception__handler


def get_cohesity_client(module):
    '''
    function to get cohesity cohesity client
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        cluster_vip = module.params.get('cluster')
        username = module.params.get('username')
        password = module.params.get('password')
        domain = 'LOCAL'
        if "@" in username:
            user_domain = username.split("@")
            username = user_domain[0]
            domain = user_domain[1]
        cohesity_client = CohesityClient(cluster_vip=cluster_vip,
                                         username=username,
                                         password=password,
                                         domain=domain)
        return cohesity_client
    except Exception as error:
        raise__cohesity_exception__handler(error, module)
