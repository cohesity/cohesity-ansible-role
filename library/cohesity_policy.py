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
from cohesity_management_sdk.models.archival_external_target import ArchivalExternalTarget
from cohesity_management_sdk.models.blackout_period import BlackoutPeriod
from cohesity_management_sdk.models.continuous_schedule import ContinuousSchedule
from cohesity_management_sdk.models.daily_schedule import DailySchedule
from cohesity_management_sdk.models.extended_retention_policy import ExtendedRetentionPolicy
from cohesity_management_sdk.models.monthly_schedule import MonthlySchedule
from cohesity_management_sdk.models.protection_policy_request import ProtectionPolicyRequest
from cohesity_management_sdk.models.scheduling_policy import SchedulingPolicy
from cohesity_management_sdk.models.snapshot_archival_copy_policy import SnapshotArchivalCopyPolicy
from cohesity_management_sdk.models.time_of_day import TimeOfDay

try:
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec,\
        raise__cohesity_exception__handler
except Exception:
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec,\
        raise__cohesity_exception__handler


cohesity_client = None


def get_policy_details(module):
    '''
    function to get the protection policy details
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        policy_name = module.params.get('name')
        protection_policies = \
            cohesity_client.protection_policies.get_protection_policies(names=policy_name)
        if protection_policies:
            for policy in protection_policies:
                if policy.name == policy_name:
                    return True, policy
        return False, None
    except APIException as ex:
        raise__cohesity_exception__handler(
            str(json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def blackout_window(module):
    '''
    function to construct a list of blackout windows
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        blackout_windows = []
        for window in module.params.get('blackout_window'):
            blackout_period = BlackoutPeriod()
            blackout_period.day = 'k' + window.get('day', 'Wednesday')
            start_time = TimeOfDay()
            end_time = TimeOfDay()
            start_time.hour = int(window.get('start_time', '12:00').split(':')[0])
            start_time.minute = int(window.get('start_time', '12:00').split(':')[1])
            end_time.hour = int(window.get('end_time', '12:30').split(':')[0])
            end_time.minute = int(window.get('end_time', '12:30').split(':')[1])
            blackout_period.start_time = start_time
            blackout_period.end_time = end_time
            blackout_windows.append(blackout_period)
        return blackout_windows
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def policy_schedule(module, scheduling_policy):
    '''
    utility function to construct the scheduling policy for different backups
    :param module: object that holds parameters passed to the module
    :param scheduling_policy: dictionary that has the scheduing details
    :return:
    '''
    try:
        schedule = SchedulingPolicy()
        schedule.periodicity = 'k' + scheduling_policy['periodicity']
        if scheduling_policy['periodicity'] == 'Daily':
            daily_schedule = DailySchedule()
            daily_schedule.days =\
                ['k' + day for day in scheduling_policy.get('days', [])]
            schedule.daily_schedule = daily_schedule
        if scheduling_policy['periodicity'] == 'Monthly':
            monthly_schedule = MonthlySchedule()
            monthly_schedule.day = 'k' + scheduling_policy['day']
            monthly_schedule.day_count = 'k' + scheduling_policy['day_count']
            schedule.monthly_schedule = monthly_schedule
        if scheduling_policy['periodicity'] == 'Continuous':
            continuous_schedule = ContinuousSchedule()
            continuous_schedule.backup_interval_mins =\
                scheduling_policy['backup_interval_mins']
            schedule.continuous_schedule = continuous_schedule
        return schedule
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def extended_retention(module):
    '''
    function to construct the list of extended retention policies
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        extended_retentions = []
        for retention in module.params.get('extended_retention'):
            retention_policy = ExtendedRetentionPolicy()
            if module.params.get('full_backup_schedule') and retention.get('backup_run_type', ''):
                retention_policy.backup_run_type =\
                    'k' + retention.get('backup_run_type', 'Full')
            retention_policy.periodicity =\
                'k' + retention.get('retention_periodicity', 'Week')
            retention_policy.days_to_keep =\
                retention.get('days_to_retain', module.params.get('days_to_retain'))
            retention_policy.multiplier = retention.get('multiplier', 1)
            extended_retentions.append(retention_policy)
        return extended_retentions
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_external_target_id(module, target_name):
    '''
    function to get the external target id
    :param module: object that holds parameters passed to the module
    :param target_name: external target name
    :return:
    '''
    try:
        vaults = cohesity_client.vaults.get_vaults(name=target_name)
        for vault in vaults:
            if vault.name == target_name:
                return vault.id
        raise__cohesity_exception__handler(
            "Failed to find external target " + str(target_name), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def archival_copy_policies(module):
    '''
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        archival_policies = []
        for policy in module.params.get('archival_copy'):
            archival_policy = SnapshotArchivalCopyPolicy()
            archival_policy.multiplier = policy.get('multiplier', 1)
            archival_policy.copy_partial = policy.get('copy_partial', True)
            archival_policy.days_to_keep =\
                policy.get('days_to_retain', module.params.get('days_to_retain'))
            archival_policy.periodicity = 'k' + policy.get('periodicity', 'Day')
            external_target = ArchivalExternalTarget()
            external_target.vault_name = policy.get('target_name')
            external_target.vault_type = 'k' + policy.get('target_type')
            external_target.vault_id =\
                get_external_target_id(module, policy.get('target_name'))
            archival_policy.target = external_target
            archival_policies.append(archival_policy)
        return archival_policies
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def create_policy(module):
    '''
    function to create a protection policy
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        policy_request = ProtectionPolicyRequest()
        policy_request.name = module.params.get('name')
        policy_request.description = module.params.get('description')
        policy_request.days_to_keep = module.params.get('days_to_retain')
        policy_request.retries = module.params.get('retries')
        policy_request.retry_interval_mins = module.params.get('retry_interval')
        if module.params.get('blackout_window'):
            policy_request.blackout_periods = blackout_window(module)

        if module.params.get('incremental_backup_schedule'):
            policy_request.incremental_scheduling_policy =\
                policy_schedule(module, module.params.get('incremental_backup_schedule'))

        if module.params.get('full_backup_schedule'):
            policy_request.full_scheduling_policy =\
                policy_schedule(module, module.params.get('full_backup_schedule'))

        if module.params.get('log_backup_schedule'):
            policy_request.log_scheduling_policy =\
                policy_schedule(module, module.params.get('log_backup_schedule'))
            policy_request.days_to_keep_log = module.params.get('log_backup_schedule').\
                get('days_to_retain', module.params.get('days_to_retain'))

        if module.params.get('bmr_backup_schedule'):
            policy_request.system_scheduling_policy =\
                policy_schedule(module, module.params.get('bmr_backup_schedule'))
            policy_request.days_to_keep_system = module.params.get('bmr_backup_schedule').\
                get('days_to_retain', module.params.get('days_to_retain'))

        if module.params.get('extended_retention'):
            policy_request.extended_retention_policies = extended_retention(module)

        if module.params.get('archival_copy'):
            policy_request.snapshot_archival_copy_policies =\
                archival_copy_policies(module)

        policy_response = cohesity_client.protection_policies.\
            create_protection_policy(policy_request)

        result = dict(
            changed=True,
            msg="Cohesity protection policy is created successfully",
            id=policy_response.id,
            task_name=module.params.get('name')
        )
        module.exit_json(**result)
    except APIException as ex:
        raise__cohesity_exception__handler(
            str(json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def delete_policy(module, policy_id):
    '''
    function to delete the protection policy
    :param module: object that holds parameters passed to the module
    :param policy_id: protection policy id
    :return:
    '''
    try:
        cohesity_client.protection_policies.delete_protection_policy(id=policy_id)
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
            name=dict(type='str', required=True),
            description=dict(type='str', default=''),
            state=dict(choices=['present', 'absent'], default='present'),
            days_to_retain=dict(type=int, default=90),
            incremental_backup_schedule=dict(type=dict, required=True),
            full_backup_schedule=dict(type=dict),
            blackout_window=dict(type=list),
            retries=dict(type=int, default=3),
            retry_interval=dict(type=int, default=30),
            bmr_backup_schedule=dict(type=dict),
            log_backup_schedule=dict(type=dict),
            extended_retention=dict(type=list),
            archival_copy=dict(type=list)
        )
    )

    # => Create a new module object
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    results = dict(
        changed=False,
        msg="Attempting to manage Cohesity protection policy",
        state=module.params.get('state')
    )

    global cohesity_client
    base_controller = BaseController()
    base_controller.global_headers['user-agent'] = 'Ansible-v2.2.0'
    cohesity_client = get_cohesity_client(module)
    policy_exists, policy_details = get_policy_details(module)

    if module.check_mode:
        check_mode_results = dict(
            changed=False,
            msg="Check Mode: Cohesity protection policy doesn't exist",
            id=""
        )
        if module.params.get('state') == "present":
            if policy_exists:
                check_mode_results['msg'] =\
                    "Check Mode: Cohesity protection policy is already present. No changes"
                check_mode_results['id'] = policy_details.id
            else:
                check_mode_results['msg'] =\
                    "Check Mode: Cohesity protection policy doesn't exist." \
                    " This action would create a protection policy"
                check_mode_results['changed'] = True
        else:
            if policy_exists:
                check_mode_results['msg'] =\
                    "Check Mode: Cohesity protection policy is present." \
                    "This action would delete the policy."
                check_mode_results['id'] = policy_details.id
                check_mode_results['changed'] = True
            else:
                check_mode_results['msg'] =\
                    "Check Mode: Cohesity protection policy doesn't exist. No changes."
        module.exit_json(**check_mode_results)

    elif module.params.get('state') == "present":

        if policy_exists:
            results = dict(
                changed=False,
                msg="The Cohesity protection policy with specified name is already present",
                id=policy_details.id,
                policy_name=module.params.get('name')
            )
        else:
            create_policy(module)

    elif module.params.get('state') == "absent":
        if policy_exists:
            delete_policy(module, policy_details.id)
            results = dict(
                changed=True,
                msg="Cohesity protection policy is deleted",
                id=policy_details.id,
                policy_name=module.params.get('name')
            )
        else:
            results = dict(
                changed=False,
                msg="Cohesity protection policy doesn't exist",
                policy_name=module.params.get('name')
            )
    else:
        module.fail_json(msg="Invalid State selected: {}".format(
            module.params.get('state')), changed=False)

    module.exit_json(**results)


if __name__ == '__main__':
    main()
