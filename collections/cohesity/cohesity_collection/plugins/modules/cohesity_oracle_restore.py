#!/usr/bin/python
# Copyright (c) 2020 Cohesity Inc
# Apache License Version 2.0

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import datetime
import json
import time
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url
from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.exceptions.api_exception import APIException
from cohesity_management_sdk.models.delete_protection_job_param import DeleteProtectionJobParam
from cohesity_management_sdk.models.cancel_protection_job_run_param import CancelProtectionJobRunParam
from cohesity_management_sdk.models.protection_job_request_body import ProtectionJobRequestBody
from cohesity_management_sdk.models.run_protection_job_param import RunProtectionJobParam

try:
    # => When unit testing, we need to look in the correct location however, when run via ansible,
    # => the expectation is that the modules will live under ansible.
    from ansible_collections.cohesity.cohesity_collection.plugins.module_utils.cohesity_auth import get__cohesity_auth__token
    from ansible_collections.cohesity.cohesity_collection.plugins.module_utils.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler, REQUEST_TIMEOUT
    from ansible_collections.cohesity.cohesity_collection.plugins.module_utils.cohesity_hints import get_cohesity_client
except Exception as e:
    pass # pass

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'supported_by': 'community',
    'status': ['preview']
}


class ParameterViolation(Exception):
    pass


class ProtectionException(Exception):
    pass


def create_recover_job(module, token, database_info):
    '''
    '''
    # Fetch latest successful run id.
    job_run_id = None
    action = 'kRecoverApp'
    vm_action='kRecoverVMs'
    job_id = database_info['vmDocument']['objectId']['jobId']
    resp = cohesity_client.protection_runs.get_protection_runs(job_id=job_id)
    if not resp:
        module.exit_json(msg='Job %s is currently not available.' % job_id)

    for job in resp:
        status = job.backup_run.status
        if status == 'kSuccess':
            job_run_id = job.backup_run.job_run_id
            start_time = job.backup_run.stats.start_time_usecs
    if not job_run_id:
        module.exit_json(msg='No successful run available for job %s.' % job_id)

    owner_object = dict(jobUid=database_info['vmDocument']['objectId']['jobUid'],
                        jobId=database_info['vmDocument']['objectId']['jobId'],
                        jobInstanceId=job_run_id,
                        startTimeUsecs=start_time,
                        entity=dict(id=database_info['vmDocument']['objectId']['entity']['parentId']))
    oracle_db_config = dict(controlFilePathVec=[],
                             enableArchiveLogMode=True,
                             redoLogConf=dict(
                                 groupMemberVec=[],
                                 memberPrefix='redo',
                                 sizeMb=20),
                             fraSizeMb=module.params.get('fra_size_mb'))

    # Alternate location params.
    alternate_location_params = None
    server = module.params.get('cluster') 
    clone_app_view = module.params.get('clone_app_view')
    source_db = module.params.get('source_db') 
    source_server = module.params.get('source_server') 
    validate_certs = module.params.get('validate_certs') 
    target_db = newDatabaseName=module.params.get('target_db') 
    target_server = newDatabaseName=module.params.get('target_server')
    oracle_restore_params = dict(captureTailLogs=False)
   
    if clone_app_view:
        action = 'kCloneAppView'
        vm_action = 'kCloneVMs'
        oracle_restore_params['oracleCloneAppViewParamsVec'] = [dict()]

    elif source_server != target_server or source_db != target_db:
        alternate_location_params = dict(newDatabaseName=module.params.get('target_db'),
                                    homeDir=module.params.get('oracle_home'),
                                    baseDir=module.params.get('oracle_base'),
                                    oracleDBConfig=oracle_db_config,
                                    databaseFileDestination=module.params.get('oracle_home'))
        oracle_restore_params['alternateLocationParams'] = alternate_location_params
    restore_obj_vec = dict(appEntity=database_info['vmDocument']['objectId']['entity'],
                           restoreParams=dict(oracleRestoreParams=oracle_restore_params))
    owner_restore_info = dict(ownerObject=owner_object,
                              ownerRestoreParams=dict(action=vm_action),
                              performRestore=False)

    body = dict(name=module.params.get('task_name'),
                action=action,
                restoreAppParams=dict(type=19,
                                      ownerRestoreInfo=owner_restore_info,
                                      restoreAppObjectVec=[restore_obj_vec]))
    try:
        uri = 'https://' + server + '/irisservices/api/v1/recoverApplication'
        headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer ' + token}
        response = open_url(url=uri,data=json.dumps(body), method='POST', headers=headers,
                            validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)

        response = json.loads(response.read())
        return response
    except Exception as err:
        module.fail_json(msg='Error while recovery task creation, error message: "%s".' % err)


def check_for_status(module, task_id):
    try:
        while True:
            resp = cohesity_client.restore_tasks.get_restore_tasks(task_ids=task_id)
            if not resp:
                raise Exception('Recovery tasks not available')
            status = resp[0].status
            if status in ['kCancelled', 'kFinished']:
                return status == 'kFinished'
    except Exception as err:
        module.exit_json(msg=err)


def search_for_database(token, module):
    '''
    '''
    server = module.params.get('cluster') 
    sourcedb = module.params.get('source_db') 
    source_server = module.params.get('source_server') 
    validate_certs = module.params.get('validate_certs') 
    try:
        uri = 'https://' + server + '/irisservices/api/v1/searchvms?entityTypes=kOracle&vmName=%s' % sourcedb
        headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer ' + token}
        response = open_url(url=uri, method='GET', headers=headers,
                            validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)

        response = json.loads(response.read())
        if not response:
            raise Exception('Source database %s not available.' % sourcedb)
        vms = response['vms']
        snapshot_timesecs = 0
        search_info = ''
        for vm in vms:
            time_secs = vm['vmDocument']['versions'][0]['snapshotTimestampUsecs']
            if source_server in vm['vmDocument']['objectAliases'] and time_secs > snapshot_timesecs:
                snapshot_timesecs = time_secs
                search_info = vm
        if not search_info:
            raise Exception(
                'Source database %s not available in source %s.' % sourcedb, source_server)
        return search_info
    except Exception as err:
        module.fail_json(msg=str(err))


def main():
    # => Load the default arguments including those specific to the Cohesity Protection Jobs.
    argument_spec = cohesity_common_argument_spec()
    argument_spec.update(
        dict(
            task_name=dict(type=str),
            source_db=dict(type=str, required=True),
            source_server=dict(type=str, required=True),
            target_db=dict(type=str, required=True),
            target_server=dict(type=str, required=True),
            oracle_home=dict(type=str, required=True),
            oracle_base=dict(type=str, required=True),
            oracle_data=dict(type=str, required=True),
            channels=dict(type=str, required=False),
            control_file=dict(type=str, default=''),
            redo_log_path=dict(type=str, default=''),
            audit_path=dict(type=str, default=''),
            diag_path=dict(type=str, default=''),
            fra_path=dict(type=str, default=''),
            fra_size_mb=dict(type=int, default=2048),
            bct_file=dict(type=str, default=''),
            log_time=dict(type=str, default=''),
            clone_app_view=dict(type=bool, default=False),
            overwrite=dict(type=bool, default=False),
            no_recovery=dict(type=bool, default=False)
        )
    )

    # => Create a new module object
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    global cohesity_client
    cohesity_client = get_cohesity_client(module)

    token = get__cohesity_auth__token(module)
    database_info =  search_for_database(token, module)
    resp = create_recover_job(module, token, database_info)
    # Check for restore task status.
    task_id = resp['restoreTask']['performRestoreTaskState']['base']['taskId']
    status = check_for_status(module, task_id)
    if status == False:
        msg = 'Error occured during task recovery.'
        module.fail_json(msg=msg)

    results = dict(
        changed=True,
        msg = 'Successfully created restore task "%s"' % module.params.get('task_name')
    )
    module.exit_json(**results)


if __name__ == '__main__':
    main()
