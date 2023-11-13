# !/usr/bin/python
# Copyright (c) 2020 Cohesity Inc
# Apache License Version 2.0

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import time

from ansible.module_utils.basic import AnsibleModule
from cohesity_management_sdk.exceptions.api_exception import APIException
from cohesity_management_sdk.models.cancel_protection_job_run_param import CancelProtectionJobRunParam
from cohesity_management_sdk.models.delete_protection_job_param import DeleteProtectionJobParam
from cohesity_management_sdk.models.protection_job_request_body import ProtectionJobRequestBody
from cohesity_management_sdk.models.run_protection_job_param import RunProtectionJobParam
from cohesity_management_sdk.models.time_of_day import TimeOfDay
from module_utils.storage.cohesity.cohesity_module_utils import get_cohesity_client

try:
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec,\
        raise__cohesity_exception__handler
except Exception:
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec,\
        raise__cohesity_exception__handler


cohesity_client = None
SLEEP_TIME_SECONDS = 60


def get_vmware_job_details(module):
    '''
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        jobs = cohesity_client.protection_jobs.\
            get_protection_jobs(names=module.params.get('job_name'))
        for job in jobs:
            if job.name == module.params.get('job_name'):
                return job
        return None
    except APIException as ex:
        raise__cohesity_exception__handler(str(
            json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_policy_id(module):
    '''
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        policies = cohesity_client.protection_policies.\
            get_protection_policies(names=module.params.get('protection_policy'))
        for policy in policies:
            if policy.name == module.params.get('protection_policy'):
                return policy.id
        raise__cohesity_exception__handler(
            "Failed to find protection policy " + module.params.get('protection_policy'), module)
    except APIException as ex:
        raise__cohesity_exception__handler(str(
            json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_view_box_id(module):
    '''
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        view_boxes = cohesity_client.view_boxes.get_view_boxes(names=module.params.get('storage_domain'))
        for view_box in view_boxes:
            if view_box.name == module.params.get('storage_domain'):
                return view_box.id
        raise__cohesity_exception__handler(
            "Failed to find storage domain " + module.params.get('storage_domain'), module)
    except APIException as ex:
        raise__cohesity_exception__handler(str(
            json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_parent_source_id(module, parent_source):
    '''
    :param module: object that holds parameters passed to the module
    :param parent_source: name of the parent protection source
    :return:
    '''
    try:
        sources = cohesity_client.protection_sources.list_protection_sources_root_nodes(environments='kVMware')
        for source in sources:
            if source.protection_source.name == parent_source:
                return source.protection_source.id
        raise__cohesity_exception__handler(
            "Failed to find protection source " + module.params.get('protection_source') + " on the cluster", module)
    except APIException as ex:
        raise__cohesity_exception__handler(str(
            json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_vmware_object_ids(module, source_object_tree, object_names):
    '''
    :param module: object that holds parameters passed to the module
    :param source_object_tree: protection source parent object tree
    :param object_names: list of object i.e vm names
    :return:
    '''
    try:
        object_ids = []
        nodes = []
        for node in source_object_tree[0].nodes:
            if 'nodes' in node:
                nodes.append(node['nodes'])
            if ('protectionSource' in node) and (node['protectionSource']['name'] in object_names) and\
                    node['protectionSource']['vmWareProtectionSource']['type'] == 'kVirtualMachine':
                object_ids.append(node['protectionSource']['id'])
        while len(nodes) != 0:
            objects = nodes.pop()
            for node in objects:
                if 'nodes' in node:
                    nodes.append(node['nodes'])
                if ('protectionSource' in node) and (node['protectionSource']['name'] in object_names) and \
                        node['protectionSource']['vmWareProtectionSource']['type'] == 'kVirtualMachine':
                    object_ids.append(node['protectionSource']['id'])
        if len(set(object_ids)) > len(object_names):
            raise__cohesity_exception__handler(
                "Found multiple vm's with same name", module)
        elif len(set(object_ids)) < len(object_names):
            raise__cohesity_exception__handler(
                "Couldn't find some vm's passed to the module", module)
        return list(set(object_ids))
    except APIException as ex:
        raise__cohesity_exception__handler(
            str(json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_vmware_source_objects(module, parent_source_id):
    '''
    :param module: object that holds parameters passed to the module
    :param parent_source_id: parent protection source id
    :return:
    '''
    try:
        protection_source = cohesity_client.protection_sources.list_protection_sources(id=parent_source_id)
        if len(protection_source) != 0:
            return protection_source
        raise__cohesity_exception__handler(
            "Failed to find protection source " + module.params.get('protection_source') + " on the cluster", module)
    except APIException as ex:
        raise__cohesity_exception__handler(str(
            json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_job_run(module, job_id):
    '''
    :param module: object that holds parameters passed to the module
    :param job_id: protection job id
    :return:
    '''
    try:
        protection_run = cohesity_client.protection_runs.get_protection_runs(job_id=job_id, num_runs=1)
        if protection_run:
            return protection_run[0]
        return None
    except APIException as ex:
        raise__cohesity_exception__handler(str(
            json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def start_vmware_job(module, job_id):
    '''
    :param module: object that holds parameters passed to the module
    :param job_id: protection job id
    :return:
    '''
    try:
        job_run = get_job_run(module, job_id)
        if job_run and job_run.backup_run.status in ['kAccepted', 'kRunning']:
            results = dict(
                changed=False,
                msg="The Protection Job is already started",
            )
            module.exit_json(**results)
        params = RunProtectionJobParam()
        params.run_type = 'k' + module.params.get('ondemand_run_type')
        cohesity_client.protection_jobs.create_run_protection_job(job_id, params)
        result = dict(
            changed=True,
            msg="The protection job run is started"
        )
        module.exit_json(**result)
    except APIException as ex:
        raise__cohesity_exception__handler(str(
            json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def stop_vmware_job(module, job_id):
    '''
    :param module: object that holds parameters passed to the module
    :param job_id: protection job id
    :return:
    '''
    try:
        job_run = get_job_run(module, job_id)
        if not job_run or job_run.backup_run.status not in ['kAccepted', 'kRunning']:
            results = dict(
                changed=False,
                msg="There is no active running job to cancel",
            )
            module.exit_json(**results)
        param = CancelProtectionJobRunParam()
        param.job_run_id = job_run.backup_run.job_run_id
        cohesity_client.protection_runs.create_cancel_protection_job_run(job_id, body=param)
        wait_minutes = module.params.get('wait_minutes')
        while wait_minutes > 0:
            job_run = get_job_run(module, job_id)
            if job_run and job_run.backup_run.status not in ['kAccepted', 'kRunning']:
                result = dict(
                    changed=True,
                    msg="The Protection job run is stopped",
                )
                module.exit_json(**result)
            time.sleep(SLEEP_TIME_SECONDS)
            wait_minutes = wait_minutes - 1
        result = dict(
            changed=True,
            msg="Request to stop the protection job is made. Timed out while checking if the job is stopped"
        )
        module.exit_json(**result)
    except APIException as ex:
        raise__cohesity_exception__handler(str(
            json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def create_vmware_job(module):
    '''
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        request_body = ProtectionJobRequestBody()
        request_body.name = module.params.get('job_name')
        request_body.policy_id = get_policy_id(module)
        request_body.view_box_id = get_view_box_id(module)
        request_body.environment = 'kVMware'
        request_body.timezone = module.params.get('timezone')
        if module.params.get('description'):
            request_body.description = module.params.get('description')
        if module.params.get('start_time'):
            start_time = module.params.get('start_time').split(':')
            if len(start_time) != 2:
                raise__cohesity_exception__handler(
                    "Please make sure the start time is in specified format", module)
            time_of_day = TimeOfDay()
            time_of_day.hour = int(start_time[0])
            time_of_day.minute = int(start_time[1])
            request_body.start_time = time_of_day
        request_body.parent_source_id =\
            get_parent_source_id(module, module.params.get('protection_source'))
        request_body.source_ids = [request_body.parent_source_id]
        vmware_source_object_tree = get_vmware_source_objects(module, request_body.parent_source_id)
        if module.params.get('include'):
            request_body.source_ids =\
                get_vmware_object_ids(module, vmware_source_object_tree, module.params.get('include'))
        if module.params.get('exclude'):
            request_body.exclude_source_ids =\
                get_vmware_object_ids(module, vmware_source_object_tree, module.params.get('exclude'))
        protection_job = cohesity_client.protection_jobs.create_protection_job(request_body)
        return protection_job
    except APIException as ex:
        raise__cohesity_exception__handler(str(
            json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def delete_vmware_job(module, job_id):
    '''
    :param module: object that holds parameters passed to the module
    :param job_id: protection job id
    :return:
    '''
    try:
        delete_job_params = DeleteProtectionJobParam()
        delete_job_params.delete_snapshots = module.params.get('delete_snapshots')
        cohesity_client.protection_jobs.delete_protection_job(job_id, body=delete_job_params)
    except APIException as ex:
        raise__cohesity_exception__handler(str(
            json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def main():
    argument_spec = dict(
            cluster=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            job_name=dict(type='str', required=True),
            description=dict(type='str'),
            state=dict(type='str', choices=['present', 'absent', 'started', 'stopped'], default='present'),
            ondemand_run_type=dict(type='str', choices=['Regular', 'Full', 'Log', 'System'], default='Regular'),
            wait_minutes=dict(type='int', default=30),
            protection_source=dict(type='str', required=True),
            timezone=dict(type='str', default='America/Los_Angeles'),
            include=dict(type='list', elements='str'),
            exclude=dict(type='list', elements='str'),
            protection_policy=dict(type='str', required=True),
            storage_domain=dict(type='str', required=True),
            start_time=dict(type='str'),
            delete_snapshots=dict(type='bool', default=False)
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    results = dict(
        changed=False,
        msg="Managing Cohesity protection job",
        state=module.params.get('state')
    )

    global cohesity_client
    cohesity_client = get_cohesity_client(module)
    job_details = get_vmware_job_details(module)

    if module.check_mode:
        if module.params.get('state') == "present":
            if job_details:
                check_mode_results = dict(
                    changed=False,
                    msg="Check Mode: The Cohesity protection job already exists on the cluster"
                )
            else:
                check_mode_results = dict(
                    changed=True,
                    msg="Check Mode: The Cohesity protection job is created"
                )
        elif module.params.get('state') == "absent":
            if job_details:
                check_mode_results = dict(
                    changed=True,
                    msg="Check Mode: The Cohesity protection job is deleted"
                )
            else:
                check_mode_results = dict(
                    changed=False,
                    msg="Check Mode: The Cohesity protection job doesn't exist on the cluster"
                )
        elif module.params.get('state') == "started":
            if job_details:
                check_mode_results = dict(
                    changed=True,
                    msg="Check Mode: The Cohesity protection job run is started"
                )
            else:
                check_mode_results = dict(
                    changed=False,
                    msg="Check Mode: The Cohesity protection job doesn't exist on the cluster"
                )
        elif module.params.get('state') == "stopped":
            if job_details:
                check_mode_results = dict(
                    changed=True,
                    msg="Check Mode: The Cohesity protection job run is stopped"
                )
            else:
                check_mode_results = dict(
                    changed=False,
                    msg="Check Mode: The Cohesity protection job doesn't exist on the cluster"
                )
        else:
            check_mode_results = dict(
                changed=False,
                msg="Check Mode: Invalid state"
            )
        module.exit_json(**check_mode_results)

    elif module.params.get('state') == "present":
        if job_details:
            results = dict(
                changed=False,
                msg="The Cohesity protection job already exists on the cluster"
            )
        else:
            protection_job = create_vmware_job(module)
            results = dict(
                changed=True,
                msg="The Cohesity protection job is created",
                id=protection_job.id
            )

    elif module.params.get('state') == "absent":
        if job_details:
            delete_vmware_job(module, job_details.id)
            results = dict(
                changed=True,
                msg="The Cohesity protection job is deleted",
                id=job_details.id
            )
        else:
            results = dict(
                changed=False,
                msg="The Cohesity protection job doesn't exist on the cluster"
            )
    elif module.params.get('state') == 'started':
        if job_details:
            start_vmware_job(module, job_details.id)
        else:
            results = dict(
                changed=False,
                msg="The Cohesity protection job doesn't exist on the cluster"
            )
    elif module.params.get('state') == 'stopped':
        if job_details:
            stop_vmware_job(module, job_details.id)
        else:
            results = dict(
                changed=False,
                msg="The Cohesity protection job doesn't exist on the cluster"
            )
    else:
        module.fail_json(msg="Invalid State selected: {}".format(
            module.params.get('state')), changed=False)

    module.exit_json(**results)


if __name__ == '__main__':
    main()
