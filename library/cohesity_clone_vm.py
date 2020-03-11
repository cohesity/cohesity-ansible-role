# !/usr/bin/python
# Copyright (c) 2019 Cohesity Inc
# Apache License Version 2.0

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import time

from ansible.module_utils.basic import AnsibleModule
from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.models.clone_task_request import CloneTaskRequest
from cohesity_management_sdk.models.vmware_clone_parameters import VmwareCloneParameters
from cohesity_management_sdk.models.restore_object_details import RestoreObjectDetails
from cohesity_management_sdk.exceptions.api_exception import APIException
from datetime import datetime


try:
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec,\
        raise__cohesity_exception__handler
except Exception:
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec,\
        raise__cohesity_exception__handler


SLEEP_TIME_SECONDS = 90
MICRO_SECONDS = 1000000
cohesity_client = None


DOCUMENTATION = '''
module: cohesity_clone
short_description: Clone VMs using Dev/Test workflow
description:
    - Ansible Module used to Clone VMs on Cohesity using Dev/Test workflow.
version_added: '2.6.5'
author:
  - Jeremy Goodrum (github.com/exospheredata)
  - Cohesity, Inc
options:
  name:
    description:
      - Name of the Clone Task
  state:
    description:
      - Determines if the Clone Task should be present or absent from the host
    choices:
      - present
      - absent
    default: 'present'
  job_name:
    description:
      - Protection Group/Job name from where VM will be cloned
    type: string
  view_name:
    description:
      - View name which will be cloned along with the VM
    type: string
  backup_timestamp:
    description:
      - Specify point in time snapshot using this option
    type: string
  environment:
    description:
      - Select the source environment for cloning. 
    choices:
      - VMware
    default: 'VMware'
  vm_names:
    description:
      - Name of the VMs that will be cloned
    type: list
  wait_for_job:
    description:
      - ASK_TEAM
    type: bool
    default: True
  prefix:
    description:
      - Add prefix to cloned VM name 
    type: string
    default: ''
  suffix:
    description:
      - Add suffix to cloned VM name 
    type: string
    default: ''
  power_on:
    description:
      - Specify if you want cloned VM powered on or off
    type: bool
    default: True
  network_connected:
    description:
      - Specify if you want cloned VM connected to network or a detached network
    type: bool
    default: True  
  wait_minutes:
    description:
      - ASK_TEAM
    type: int
    default: 30
  resource_pool:
    description:
      - ASK_TEAM
    type: string
requirements: []
'''

def get_clone_task(module, wait_request):
    '''
    Get clone task details
    :param module: object that holds parameters passed to the module
    :param wait_request: boolean to determine if request is made during wait time
    :return:
    '''
    try:
        environment = 'k' + module.params.get('environment')
        restore_tasks = cohesity_client.restore_tasks.get_restore_tasks(task_types=['kCloneVMs'],
                                                                        environment=environment)
        if restore_tasks:
            for task in restore_tasks:
                if task.name == module.params.get('name'):
                    return True, task
        return False, ''
    except APIException as ex:
        if not wait_request:
            raise__cohesity_exception__handler(
                str(json.loads(ex.context.response.raw_body)), module)
        else:
            return False, ''
    except Exception as error:
        if not wait_request:
            raise__cohesity_exception__handler(error, module)
        else:
            return False, ''


def get_protection_job_details(module):
    '''
    Get protection job details
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        protection_job_name = module.params.get('job_name')
        environment = 'k' + module.params.get('environment')
        protection_jobs = cohesity_client.\
            protection_jobs.get_protection_jobs(names=protection_job_name, environments=[environment])
        if protection_jobs:
            return protection_jobs[0]
        else:
            raise__cohesity_exception__handler("Failed to find the job name for the selected environment type",
                                               module)
    except APIException as ex:
        raise__cohesity_exception__handler(
            str(json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_snapshot_details(module, timestamp, vm_name, job_id):
    '''
    function to search and get the snapshot details of a vm
    :param module: object that holds parameters passed to the module
    :param timestamp: backup timestamp
    :param vm_name: vm to search
    :param job_id: protection job id
    :return:
    '''
    try:
        restore_object = RestoreObjectDetails()
        object_details = cohesity_client.restore_tasks.search_objects(search=vm_name, job_ids=[job_id])
        if object_details.total_count == 0:
            raise__cohesity_exception__handler('There are no existing snapshots for '
                                               + str(vm_name), module)
        else:
            if not timestamp:
                restore_object.job_id = job_id
                restore_object.protection_source_id = object_details.object_snapshot_info[0].\
                    snapshotted_source.id
            else:
                restore_object.job_id = job_id
                restore_object.protection_source_id = object_details.object_snapshot_info[0].\
                    snapshotted_source.id
                for snapshot in object_details.object_snapshot_info[0].versions:
                    requested_timestamp = datetime.strptime(
                        timestamp, '%Y-%m-%d:%H:%M').replace(second=0)
                    snapshot_timestamp = datetime.strptime(time.ctime(snapshot.started_time_usecs /
                                                                      MICRO_SECONDS),
                                                           '%a %b %d %H:%M:%S %Y').replace(second=0)
                    if requested_timestamp == snapshot_timestamp:
                        restore_object.job_run_id = snapshot.job_run_id
                        restore_object.started_time_usecs = snapshot.started_time_usecs
                if not restore_object.job_run_id:
                    raise__cohesity_exception__handler(
                        'Failed to get the snapshot of ' + vm_name + ' backed up at ' + str(timestamp), module)
        return restore_object
    except APIException as ex:
        raise__cohesity_exception__handler(
            str(json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_resource_pool_id(module, resource_pool, protection_source_id):
    '''
    function to get the resource pool id, parsing the protection source nodes tree structure
    :param module: object that holds parameters passed to the module
    :param resource_pool: resource pool name
    :param protection_source_id: protection source id, parent source where we search for resource pool
    :return:
    '''
    try:
        nodes = []
        protection_sources = cohesity_client.protection_sources.\
            list_protection_sources(id=protection_source_id, exclude_types=['kVirtualMachine'])
        for node in protection_sources[0].nodes:
            if 'nodes' in node:
                nodes.append(node['nodes'])
            if ('protectionSource' in node) and (node['protectionSource']['name'] == resource_pool) and\
                    node['protectionSource']['vmWareProtectionSource']['type'] == 'kResourcePool':
                return node['protectionSource']['id']
        while len(nodes) != 0:
            objects = nodes.pop()
            for node in objects:
                if 'nodes' in node:
                    nodes.append(node['nodes'])
                if ('protectionSource' in node) and (node['protectionSource']['name'] == resource_pool) and \
                        node['protectionSource']['vmWareProtectionSource']['type'] == 'kResourcePool':
                    return node['protectionSource']['id']
        raise__cohesity_exception__handler(
            "Failed to find the resource pool " + str(resource_pool), module)
    except APIException as ex:
        raise__cohesity_exception__handler(
            str(json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def wait(module):
    '''
    function to wait for clone task, waits for wait minutes passed to the module
    :param module: object that holds parameters passed to the module
    :return:
    '''
    if module.params.get('wait_for_job'):
        wait_time = module.params.get('wait_minutes')
        while wait_time > 0:
            clone_exist, clone_details = get_clone_task(module, True)
            if not clone_exist:
                return "The clone VMs request is accepted. Failed to check clone status during wait time"
            elif clone_exist and clone_details.error:
                raise__cohesity_exception__handler(
                    "The clone VMs task failed", module)
            elif clone_exist and clone_details.status == 'kFinished' and not clone_details.error:
                return "The clone VMs task is successful"
            time.sleep(SLEEP_TIME_SECONDS)
            wait_time = wait_time - 1
        return "The clone VMs request is accepted. The task is not finished in the wait time"
    else:
        return "The clone VMs request is accepted"


def clone_vm(module):
    '''
    function to clone the VMs
    :param module: object that holds parameters passed to the module
    :return:
    '''
    try:
        protection_job_details = get_protection_job_details(module)
        objects = []
        timestamp = module.params.get('backup_timestamp')
        resource_pool = module.params.get('resource_pool')
        for vm in module.params.get('vm_names'):
            object_details = get_snapshot_details(module, timestamp, vm, protection_job_details.id)
            objects.append(object_details)
        clone_request = CloneTaskRequest()
        clone_request.name = module.params.get('name')
        clone_request.target_view_name = module.params.get('view_name')
        clone_request.mtype = 'kCloneVMs'
        clone_request.new_parent_id = protection_job_details.parent_source_id
        clone_request.vmware_parameters = VmwareCloneParameters()
        if module.params.get('suffix'):
            clone_request.vmware_parameters.suffix = module.params.get('suffix')
        if module.params.get('prefix'):
            clone_request.vmware_parameters.prefix = module.params.get('prefix')
        clone_request.vmware_parameters.powered_on = module.params.get(
            'power_on')
        clone_request.vmware_parameters.resource_pool_id = \
            get_resource_pool_id(module, resource_pool, protection_job_details.parent_source_id)
        clone_request.objects = objects
        clone_details = cohesity_client.restore_tasks.\
            create_clone_task(body=clone_request)
        if not clone_details:
            raise__cohesity_exception__handler("Failed to clone VMs", module)
        status_message = wait(module)
        result = dict(
            changed=True,
            msg=status_message,
            id=clone_details.id,
            task_name=module.params.get('name')
        )
        module.exit_json(**result)
    except APIException as ex:
        raise__cohesity_exception__handler(
            str(json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def destroy_clone(module, clone_id):
    '''
    function to tear down clone
    :param module: object that holds parameters passed to the module
    :param clone_id: clone task id
    :return:
    '''
    try:
        cohesity_client.restore_tasks.delete_public_destroy_clone_task(id=clone_id)
    except APIException as ex:
        if "destroyed" in json.loads(ex.context.response.raw_body)['message']:
            status = dict(
                changed=False,
                msg="Cohesity clone task is already destroyed",
                task_name=module.params.get('name')
            )
            module.exit_json(**status)
        else:
            raise__cohesity_exception__handler(str(json.loads(ex.context.response.raw_body)), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_cohesity_client(module):
    '''
    function to get cohesity cohesity client
    :param module: object that holds parameters passed to the module
    :return:
    '''
    cluster_vip = module.params.get('cluster')
    username = module.params.get('username')
    password = module.params.get('password')
    domain = 'LOCAL'
    if "/" in username:
        user_domain = username.split("/")
        username = user_domain[1]
        domain = user_domain[0]

    cohesity_client = CohesityClient(cluster_vip=cluster_vip,
                                     username=username,
                                     password=password,
                                     domain=domain)
    return cohesity_client


def main():
    # => Load the default arguments including those specific to the Cohesity clone task.
    argument_spec = cohesity_common_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type='str', required=True),
            state=dict(choices=['present', 'absent'], default='present'),
            job_name=dict(type='str', required=True),
            view_name=dict(type='str', required=True),
            backup_timestamp=dict(type='str', default=''),
            environment=dict(choices=['VMware'], default='VMware'),
            vm_names=dict(type='list', required=True),
            wait_for_job=dict(type='bool', default=True),
            prefix=dict(type='str', default=""),
            suffix=dict(type='str', default=""),
            power_on=dict(type='bool', default=True),
            network_connected=dict(type='bool', default=True),
            wait_minutes=dict(type=int, default=30),
            resource_pool=dict(type='str', required=True)
        )
    )

    # => Create a new module object
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    results = dict(
        changed=False,
        msg="Attempting to manage Cohesity Clone",
        state=module.params.get('state')
    )

    global cohesity_client
    cohesity_client = get_cohesity_client(module)
    clone_exists, clone_details = get_clone_task(module, False)

    if module.check_mode:
        check_mode_results = dict(
            changed=False,
            msg="Check Mode: Cohesity clone task doesn't exist",
            id=""
        )
        if module.params.get('state') == "present":
            if clone_exists:
                check_mode_results['msg'] =\
                    "Check Mode: Cohesity clone task is already present. No changes"
                check_mode_results['id'] = clone_details.id
            else:
                check_mode_results['msg'] =\
                    "Check Mode: Cohesity clone task doesn't exist. This action would clone VMs"
                check_mode_results['changed'] = True
        else:
            if clone_exists:
                check_mode_results['msg'] =\
                    "Check Mode: Cohesity clone task is present." \
                    "This action would tear down the Cohesity Clone."
                check_mode_results['id'] = clone_details.id
                check_mode_results['changed'] = True
            else:
                check_mode_results['msg'] =\
                    "Check Mode: Cohesity Clone task doesn't exist. No changes."
        module.exit_json(**check_mode_results)

    elif module.params.get('state') == "present":

        if clone_exists:
            results = dict(
                changed=False,
                msg="The clone task with specified name is already present",
                id=clone_details.id,
                name=module.params.get('name')
            )
        else:
            clone_vm(module)

    elif module.params.get('state') == "absent":

        if clone_exists:
            destroy_clone(module, clone_details.id)
            results = dict(
                changed=True,
                msg="Cohesity clone is destroyed",
                id=clone_details.id,
                task_name=module.params.get('name')
            )
        else:
            results = dict(
                changed=False,
                msg="Cohesity clone task doesn't exist",
                task_name=module.params.get('name')
            )
    else:
        module.fail_json(msg="Invalid State selected: {}".format(
            module.params.get('state')), changed=False)

    module.exit_json(**results)


if __name__ == '__main__':
    main()
