# !/usr/bin/python
# Copyright (c) 2019 Cohesity Inc
# Apache License Version 2.0

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible.module_utils.basic import AnsibleModule
from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.controllers.base_controller import BaseController
from cohesity_management_sdk.exceptions.api_exception import APIException
from cohesity_management_sdk.models.create_view_request import CreateViewRequest
from cohesity_management_sdk.models.nfs_root_permissions import NfsRootPermissions
from cohesity_management_sdk.models.qo_s import QoS
from cohesity_management_sdk.models.quota_policy import QuotaPolicy
from cohesity_management_sdk.models.storage_policy_override import StoragePolicyOverride
from cohesity_management_sdk.models.subnet import Subnet
from cohesity_management_sdk.models.update_view_param import UpdateViewParam

try:
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec,\
        raise__cohesity_exception__handler
except Exception:
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec,\
        raise__cohesity_exception__handler


cohesity_client = None
TWENTY_GiB = 20*(1024**3)
EIGHTEEN_GiB = 18*(1024**3)


def get_view_details(module):
    '''
    function to get the view details
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        view = cohesity_client.views.get_views(view_names=module.params.get('name'))
        if view.views:
            return True, view.views[0]
        return False, None
    except APIException as ex:
        raise__cohesity_exception__handler(
            str(json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_storage_domain_id(module):
    '''
    function to get the storage domain id from name
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        view_boxes = cohesity_client.view_boxes.\
            get_view_boxes(names=module.params.get('storage_domain'))
        for view_box in view_boxes:
            if view_box.name == module.params.get('storage_domain'):
                return view_box.id
        raise__cohesity_exception__handler(
            "Failed to find storage domain " + module.params.get('storage_domain'), module)
    except APIException as ex:
        raise__cohesity_exception__handler(
            str(json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def set_security(view_request, module):
    '''
    function to set the security parameters
    :param view_request: request body
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:

        if module.params.get('protocol') == "All" and module.params.get('security').get('security_mode', None):
            view_request.security_mode = 'k' + module.params.get('security').\
                get('security_mode', 'NativeMode')
        if module.params.get('security').get('override_global_whitelist', None) and\
                module.params.get('security').get('whitelist', ''):
            view_request.override_global_whitelist = module.params.get('security').\
                get('override_global_whitelist', True)
            view_request.subnet_whitelist = []
            for whitelist_subnet in module.params.get('security').get('whitelist'):
                subnet = Subnet()
                subnet.ip = whitelist_subnet.get('subnet_ip', '')
                subnet.netmask_ip_4 = whitelist_subnet.get('subnet_mask', '')
                subnet.nfs_access = 'k' + whitelist_subnet.get('nfs_permission', 'ReadWrite')
                subnet.smb_access = 'k' + whitelist_subnet.get('smb_permission', 'ReadWrite')
                subnet.nfs_root_squash = whitelist_subnet.get('nfs_root_squash', False)
                subnet.description = whitelist_subnet.get('description', '')
                view_request.subnet_whitelist.append(subnet)
        return view_request
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def set_quota(view_request, module):
    '''
    function to set the logical quota and alert threshold
    :param view_request: request body
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        quota_policy = QuotaPolicy()
        if module.params.get('quota').get('set_logical_quota', False):
            quota_policy.hard_limit_bytes = module.params.get('quota').\
                get('hard_limit_bytes', TWENTY_GiB)
            view_request.logical_quota = quota_policy
        if module.params.get('quota').get('set_alert_threshold', False):
            quota_policy.alert_limit_bytes = module.params.get('quota').\
                get('alert_limit_bytes', EIGHTEEN_GiB)
            view_request.logical_quota = quota_policy
        return view_request
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def set_nfs_options(view_request, module):
    '''
    function to set the nfs options
    :param view_request: request body
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        view_request.enable_nfs_view_discovery = module.params.\
            get('nfs_options').get('view_discovery', True)
        if module.params.get('nfs_options').get('user_id', '') or module.\
                params.get('nfs_options').get('group_id', ''):
            nfs_root_permissions = NfsRootPermissions()
            nfs_root_permissions.uid = module.params.get('nfs_options').get('user_id', 0)
            nfs_root_permissions.gid = module.params.get('nfs_options').get('group_id', 0)
            view_request.nfs_root_permissions = nfs_root_permissions
        return view_request
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def set_smb_options(view_request, module):
    '''
    function to set the smb options
    :param view_request: request body
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        view_request.enable_smb_view_discovery = module.params.\
            get('smb_options').get('view_discovery', True)
        view_request.enable_smb_access_based_enumeration =\
            module.params.get('smb_options').\
            get('access_based_enumeration', False)
        return view_request
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def create_view(module):
    '''
    function to create Cohesity view
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        create_view_request = CreateViewRequest()
        create_view_request.name = module.params.get('name')
        create_view_request.description = module.params.get('description')
        create_view_request.view_box_id = get_storage_domain_id(module)
        qos_policy = QoS()
        qos_policy.principal_name = module.params.get('qos_policy')
        create_view_request.qos = qos_policy
        create_view_request.protocol_access = 'k' + module.params.get('protocol')
        create_view_request.case_insensitive_names_enabled = module.params.get('case_insensitive')
        if module.params.get('protocol') == "S3Only" and module.params.get('object_key_pattern'):
            create_view_request.s_3_key_mapping_config = 'k' +\
                                                         module.params.get('object_key_pattern')
        storage_policy_override = StoragePolicyOverride()
        storage_policy_override.disable_inline_dedup_and_compression =\
            module.params.get('inline_dedupe_compression')
        create_view_request.storage_policy_override = storage_policy_override
        if module.params.get('security'):
            create_view_request = set_security(create_view_request, module)
        if module.params.get('quota'):
            create_view_request = set_quota(create_view_request, module)
        if module.params.get('nfs_options'):
            create_view_request = set_nfs_options(create_view_request, module)
        if module.params.get('smb_options'):
            create_view_request = set_smb_options(create_view_request, module)

        response = cohesity_client.views.create_view(create_view_request)
        result = dict(
            changed=True,
            msg="Cohesity view is created successfully",
            id=response.view_id,
            view_name=module.params.get('name')
        )
        module.exit_json(**result)
    except APIException as ex:
        raise__cohesity_exception__handler(str(
            json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def update_view(module):
    '''
    function to update Cohesity view
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        update_view_params = UpdateViewParam()
        update_view_params.description = module.params.get('description')
        qos_policy = QoS()
        qos_policy.principal_name = module.params.get('qos_policy')
        update_view_params.qos = qos_policy
        update_view_params.protocol_access = 'k' + module.params.get('protocol')
        storage_policy_override = StoragePolicyOverride()
        storage_policy_override.disable_inline_dedup_and_compression =\
            module.params.get('inline_dedupe_compression')
        update_view_params.storage_policy_override = storage_policy_override
        if module.params.get('security'):
            update_view_params = set_security(update_view_params, module)
        if module.params.get('quota'):
            update_view_params = set_quota(update_view_params, module)
        if module.params.get('nfs_options'):
            update_view_params = set_nfs_options(update_view_params, module)
        if module.params.get('smb_options'):
            update_view_params = set_smb_options(update_view_params, module)
        response = cohesity_client.views.\
            update_view_by_name(name=module.params.get('name'), body=update_view_params)
        result = dict(
            changed=True,
            msg="Cohesity view is updated successfully",
            id=response.view_id,
            view_name=module.params.get('name')
        )
        module.exit_json(**result)
    except APIException as ex:
        raise__cohesity_exception__handler(str(
            json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def delete_view(module):
    '''
    function to delete Cohesity view
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        cohesity_client.views.delete_view(name=module.params.get('name'))
    except APIException as ex:
        raise__cohesity_exception__handler(
            str(json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


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


def main():
    # => Load the default arguments including those specific to the Cohesity protection policy.
    argument_spec = cohesity_common_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type=str, required=True),
            description=dict(type='str', default=''),
            state=dict(choices=['present', 'absent'], default='present'),
            storage_domain=dict(type='str', required=True),
            qos_policy=dict(type='str', default='Backup Target Low'),
            protocol=dict(type='str', default='All'),
            case_insensitive=dict(type='bool', required=True),
            object_key_pattern=dict(type='str', required=False),
            inline_dedupe_compression=dict(type='bool', default=False),
            security=dict(type='dict', required=False),
            quota=dict(type='dict', required=False),
            nfs_options=dict(type='dict', required=False),
            smb_options=dict(type='dict', required=False)
        )
    )

    # => Create a new module object
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    results = dict(
        changed=False,
        msg="Attempting to manage Cohesity view",
        state=module.params.get('state')
    )

    global cohesity_client
    base_controller = BaseController()
    base_controller.global_headers['user-agent'] = 'cohesity-ansible/v2.3.2'
    cohesity_client = get_cohesity_client(module)
    view_exists, view_details = get_view_details(module)

    if module.check_mode:
        check_mode_results = dict(
            changed=False,
            msg="Check Mode: Cohesity view doesn't exist",
            name=""
        )
        if module.params.get('state') == "present":
            if view_exists:
                check_mode_results['msg'] =\
                    "Check Mode: Cohesity view is updated."
                check_mode_results['name'] = view_details.name
                check_mode_results['changed'] = True
            else:
                check_mode_results['msg'] =\
                    "Check Mode: Cohesity view doesn't exist." \
                    " This action would create a new Cohesity view"
                check_mode_results['changed'] = True
        else:
            if view_exists:
                check_mode_results['msg'] =\
                    "Check Mode: Cohesity view is present." \
                    "This action would delete the view."
                check_mode_results['name'] = view_details.name
                check_mode_results['changed'] = True
            else:
                check_mode_results['msg'] =\
                    "Check Mode: Cohesity view doesn't exist. No changes."
        module.exit_json(**check_mode_results)

    elif module.params.get('state') == "present":
        if view_exists:
            update_view(module)
        else:
            create_view(module)

    elif module.params.get('state') == "absent":
        if view_exists:
            delete_view(module)
            results = dict(
                changed=True,
                msg="Cohesity view is deleted successfully",
                view_name=module.params.get('name')
            )
        else:
            results = dict(
                changed=False,
                msg="Cohesity view doesn't exist",
                view_name=module.params.get('name')
            )
    else:
        module.fail_json(msg="Invalid State selected: {}".format(
            module.params.get('state')), changed=False)

    module.exit_json(**results)


if __name__ == '__main__':
    main()
