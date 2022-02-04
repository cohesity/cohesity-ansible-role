#!/usr/bin/python
# Copyright (c) 2018 Cohesity Inc
# Apache License Version 2.0

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import time
from datetime import datetime
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url, urllib_error

from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.controllers.base_controller import BaseController
from cohesity_management_sdk.exceptions.api_exception import APIException

try:
    # => When unit testing, we need to look in the correct location however, when run via ansible,
    # => the expectation is that the modules will live under ansible.
    from module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler, REQUEST_TIMEOUT
    from module_utils.storage.cohesity.cohesity_hints import get__prot_source_id__by_endpoint, \
        get__protection_jobs__by_environment, get__file_snapshot_information__by_filename, \
        get__prot_source_root_id__by_environment, get__restore_job__by_type
except ImportError:
    from ansible.module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler, REQUEST_TIMEOUT
    from ansible.module_utils.storage.cohesity.cohesity_hints import get__prot_source_id__by_endpoint, \
        get__protection_jobs__by_environment, get__file_snapshot_information__by_filename, \
        get__prot_source_root_id__by_environment, get__restore_job__by_type, get_cohesity_client

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'supported_by': 'community',
    'status': ['preview']
}

DOCUMENTATION = '''
module: cohesity_restore_vmware_file
short_description: Restore Files and Folders from Cohesity Protection Jobs
description:
    - Ansible Module used to start a Cohesity Recovery Job on a Cohesity Cluster.
    - When executed in a playbook, the Cohesity Recovery Job will be validated and the appropriate state action
    - will be applied.
version_added: '2.6.5'
author:
  - Naveena
  - Cohesity, Inc

options:
  state:
    description:
      - Determines the state of the Recovery Job.
      - (C)present a recovery job will be created and started.
      - (C)absent is currently not implemented
    choices:
      - present
      - absent
    default: present
  name:
    description:
      - Descriptor to assign to the Recovery Job.  The Recovery Job name will consist of the job_name:name format.
    required: yes
  job_name:
    description:
      - Name of the Protection Job
    required: yes
  endpoint:
    description:
      - Specifies the name of Vcenter where file is located.
    required: yes
  backup_timestamp:
    description:
      - Future option to identify backups based on a timestamp
      - Currently not implemented.
  file_names:
    description:
      - Array of Files and Folders to restore
    required: yes
  wait_for_job:
    description:
      - Should wait until the Restore Job completes
    type: bool
    default: yes
  wait_minutes:
    description:
      - Number of minutes to wait until the job completes.
    default: 5
  overwrite:
    description:
      - Should the restore operation overwrite the files or folders if they exist.
    type: bool
    default: yes
  preserve_attributes:
    description:
      - Should the restore operation maintain the original file or folder attributes
    type: bool
    default: yes
  restore_location:
    description:
      - Alternate location to which the files will be restored
  backup_timestamp:
    description:
      - protection run timestamp in YYYY-MM-DD:HH:MM format to use as source for the Restore operation. If not specified,
        the most recent timestamp is used
    type: String
  vm_name:
    description:
      - Name of the Vcenter virtual machine, from where the files are located. Required if the environment is VMware.
    type: String
  vm_username:
    description:
      - Username of the virtual machine, where files will be restored. Required if the environment is VMware.
    type: String
  vm_password:
    description:
      - Password of the virtual machine, where files will be restored. Required if the environment is VMware.
    type: String

extends_documentation_fragment:
    - cohesity
requirements: []
notes:
    - File and Folder restores from SMB based backups are currently not supported
'''

EXAMPLES = '''

# Restore multiple files from a specific VMware Backup and wait for up to 10 minutes for the process to complete
- cohesity_restore_vmware_file:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: Restore Single File
    job_name: myhost
    endpoint: myvcenter.host.lab
    file_names:
      - C:\\data\\files
      - C:\\data\\large_directory
    vm_name: "demo"
    vm_username: admin
    vm_password: admin
    wait_for_job: yes
    wait_minutes: 10


# Restore a single file from a VMware VM Backup
- cohesity_restore_vmware_file:
    name: "Ansible File Restore to Virtual Machine"
    environment: "VMware"
    job_name: "myvm.demo"
    endpoint: "myvcenter.cohesity.demo"
    files:
      - "/home/cohesity/sample"
    wait_for_job: True
    state: "present"
    backup_timestamp: 2021-04-11:21:37
    restore_location: /home/cohesity/
    vm_name: "demo"
    vm_username: admin
    vm_password: admin

'''

RETURN = '''
{
    "changed": true,
    "failed": false,
    "filenames": [
        "C:\\data\\files"
    ],
    "msg": "Registration of Cohesity Restore Job Complete",
    "name": "myvcenter: Ansible Test Multi-File Restore",
    "restore_jobs": [
        {
            "fullViewName": "cohesity_int_54295",
            "id": 54295,
            "objects": [
                {
                    "jobRunId": 46979,
                    "jobUid": {
                        "clusterId": 8621173906188849,
                        "clusterIncarnationId": 1538852526333,
                        "id": 46967
                    },
                    "protectionSourceId": 1044,
                    "startedTimeUsecs": 1546967910807987
                }
            ],
            "startTimeUsecs": 1548001636579142,
            "status": "Finished",
            "type": "kRestoreFiles",
            "username": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "viewBoxId": 5
        }
    ]
}

'''


class ParameterViolation(Exception):
    pass


def check__protection_restore__exists(module, self):
    payload = self.copy()
    payload['restore_type'] = "kRestoreFiles"
    payload['count'] = 1

    restore_tasks = get__restore_job__by_type(module, payload)

    if restore_tasks:
        task_list = [
            task for task in restore_tasks if task['name'] == self['name']]
        for task in task_list:
            if task['status'] != 'kFinished':
                return True
    return False


# => Return the Protection Job information based on the Environment and Job Name
def get__job_information__for_restore(module, self):
    # => Gather the Protection Jobs by Environment to allow us
    # => to verify that the Job exists and feed that into the
    # => snapshot collection.
    job_output = get__protection_jobs__by_environment(module, self)

    # => There will be a lot of potential jobs.  Return only the
    # => one that matches our job_name
    job_data = [job for job in job_output if job['name'] == self['job_name']]

    if not job_data:
        failure = dict(
            changed=False,
            job_name=self['job_name'],
            environment=self['environment'],
            msg="Failed to find chosen Job name for the selected Environment Type.")
        module.fail_json(**failure)
    else:
        # => Since we are filtering out any job that matches our name
        # => we will need to properly just grab the first element as
        # => it is returned as an array.
        return job_data[0]

def start_restore__files(module, self):
    payload = self.copy()
    return start_restore(
        module,
        "/irisservices/api/v1/public/restore/files",
        payload)


def start_restore(module, uri, self):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    try:
        uri = "https://" + server + uri
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token,
                   "user-agent": "cohesity-ansible/v2.3.3"}
        payload = self.copy()

        # => Remove the Authorization Token from the Payload
        payload.pop('token', None)

        data = json.dumps(payload)

        response = open_url(url=uri, data=data, headers=headers,
                            validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)

        response = json.loads(response.read())

        # => Remove the Job name as it will be duplicated back to our process.
        response.pop('name')

        return response
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get__job_information__for_file(module, source_object_info):
    try:
        # Based on job id fetch run details based on used provided timestamp.
        # If timestamp is not provided fetch latest successful run details.
        run_id = None
        job_runs = cohesity_client.protection_runs.get_protection_runs(
            job_id=source_object_info["jobId"])
        for run in job_runs:
            if not module.params.get('backup_timestamp') and run.backup_run.status == "kSuccess":
                run_id = run.backup_run.job_run_id
                t_secs = run.backup_run.stats.start_time_usecs
                break
            else:
                snapshot_timestamp = datetime.strptime(
                    module.params.get('backup_timestamp'), '%Y-%m-%d:%H:%M').replace(second=0)
                t = datetime.strptime(
                time.ctime(run.backup_run.stats.start_time_usecs /
                    1000000),
                '%a %b %d %H:%M:%S %Y').replace(
                second=0)
                if snapshot_timestamp != t:
                    continue
                run_id = run.backup_run.job_run_id
                t_secs = run.backup_run.stats.start_time_usecs
                break
        if not run_id :
            module.fail_json(msg="Run details not available")
        source_object_info["jobRunId"] = run_id
        source_object_info["startedTimeUsecs"] = t_secs
    except APIException as err:
        module.fail_json(msg="Error occured while fetching job run details, error details %s" % err)



def wait_restore_complete(module, self):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    wait_counter = int(module.params.get('wait_minutes')) * 2

    wait_results = dict(
        changed=False,
        status="Failed",
        attempts=list(),
        error=list()
    )
    try:
        import time

        uri = "https://" + server + \
            "/irisservices/api/v1/public/restore/tasks/" + str(self['id'])
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + token,
                   "user-agent": "cohesity-ansible/v2.3.3"}
        attempts = 0
        # => Wait for the restore based on a predetermined number of minutes with checks every 30 seconds.
        while attempts < wait_counter:

            response = open_url(
                url=uri,
                headers=headers,
                validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)
            response = json.loads(response.read())

            # => If the status is Finished then break out and check for errors.
            if response['status'] == "kFinished":
                wait_results['changed'] = True
                wait_results['status'] = "Finished"
                break
            # => Otherwise, pause and try again.
            else:
                attempt_tracker = dict(
                    attempt=attempts,
                    status=response['status']
                )
                wait_results['attempts'].append(attempt_tracker)
                attempts += 1
                time.sleep(30)

                if attempts >= wait_counter:
                    wait_results['changed'] = False
                    wait_results['status'] = response['status']
                    wait_results['error'] = "Failed to wait for the restore to complete after " + \
                        module.params.get('wait_minutes') + " minutes."
                    if wait_results['status'] == "kInProgress":
                        wait_results['error'] = wait_results['error'] + \
                            " The restore is still in progress and the timeout might be too short."
        # => If the error key exists in the response, then something happened during the restore
        if 'error' in response:
            wait_results['status'] = "Failed"
            wait_results['changed'] = False
            wait_results['error'] = response['error']['message']

        output = self.copy()
        output.update(**wait_results)

        return output
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def main():
    # => Load the default arguments including those specific to the Cohesity Protection Jobs.
    argument_spec = cohesity_common_argument_spec()
    argument_spec.update(
        dict(
            state=dict(choices=['present', 'absent'], default='present'),
            name=dict(type='str', required=True),
            # => Currently, the only supported environments types are list in the choices
            # => For future enhancements, the below list should be consulted.
            # => 'SQL', 'View', 'Puppeteer', 'Pure', 'Netapp', 'HyperV', 'Acropolis', 'Azure'
            environment=dict(type='str', default='VMware'),
            job_name=dict(type='str', required=True),
            endpoint=dict(type='str', required=True),
            backup_timestamp=dict(type='str', default=''),
            file_names=dict(type='list', required=True),
            wait_for_job=dict(type='bool', default=True),
            overwrite=dict(type='bool', default=True),
            preserve_attributes=dict(type='bool', default=True),
            restore_location=dict(type='str', default=''),
            vm_name=dict(type='str', default=''),
            vm_username=dict(type='str', default=''),
            vm_password=dict(type='str', default='', no_log=True),
            wait_minutes=dict(type='str', default=10)

        )
    )

    # => Create a new module object
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    results = dict(
        changed=False,
        msg="Attempting to manage Protection Source",
        state=module.params.get('state')
    )

    job_details = dict(
        token=get__cohesity_auth__token(module),
        endpoint=module.params.get('endpoint'),
        job_name=module.params.get('job_name'),
        environment=module.params.get('environment'),
        name=module.params.get('job_name') + ": " + module.params.get('name')
    )

    global cohesity_client
    base_controller = BaseController()
    base_controller.global_headers['user-agent'] = 'Ansible-v2.3.3'
    cohesity_client = get_cohesity_client(module)

    if module.params.get('backup_id'):
        job_details['jobRunId'] = module.params.get('backup_id')

    if module.params.get('backup_timestamp'):
        job_details['backup_timestamp'] = module.params.get('backup_timestamp')

    job_exists = check__protection_restore__exists(module, job_details)

    if module.check_mode:
        check_mode_results = dict(
            changed=False,
            msg="Check Mode: Cohesity Protection Restore Job is not currently registered",
            id="")
        if module.params.get('state') == "present":
            if job_exists:
                check_mode_results[
                    'msg'] = "Check Mode: Cohesity Protection Restore Job is currently registered.  No changes"
            else:
                check_mode_results[
                    'msg'] = "Check Mode: Cohesity Protection Restore Job is not currently registered.  This action would register the Cohesity Protection Job."
                check_mode_results['id'] = job_exists
        else:
            if job_exists:
                check_mode_results[
                    'msg'] = "Check Mode: Cohesity Protection Restore Job is currently registered.  This action would unregister the Cohesity Protection Job."
                check_mode_results['id'] = job_exists
            else:
                check_mode_results[
                    'msg'] = "Check Mode: Cohesity Protection Restore Job is not currently registered.  No changes."
        module.exit_json(**check_mode_results)

    elif module.params.get('state') == "present":

        if job_exists:
            results = dict(
                changed=False,
                msg="The Restore Job for is already registered",
                id=job_exists,
                name=module.params.get('job_name') +
                ": " +
                module.params.get('name'))
        else:
            response = []
            environment = module.params.get('environment')
            endpoint = module.params.get('endpoint')

            # => Gather the Source Details
            source_id = None
            vcenter_list = cohesity_client.protection_sources.list_protection_sources_root_nodes(environment='k'+environment)
            for vcenter in vcenter_list:
                if vcenter.protection_source.vmware_protection_source.name == endpoint:
                    source_id = vcenter.protection_source.id
            if not source_id:
                module.fail_json(msg="Vcenter '%s' is not registered to the cluster" % endpoint)

            vm_id = None
            vm_name = module.params.get("vm_name")
            restore_file_list = module.params.get('file_names')
            job_details['endpoint'] = source_id
            job_details['file_names'] = restore_file_list

            # Fetch the virtual machine source id, using which files can be searched.
            objects = cohesity_client.protection_sources.list_virtual_machines(v_center_id=source_id,names=vm_name)
            for each_object in objects:
                if each_object.name == vm_name:
                    vm_id = each_object.id
                    break

            for file_name in job_details['file_names']:
                resp = cohesity_client.restore_tasks.search_restored_files(
                    environments='kVMware',search=file_name, source_ids=vm_id)

                # Fail if the file is not available.
                if not (resp and resp.files):
                    module.fail_json(msg="File '%s' is not available to restore" % file_name)
                for file_obj in resp.files:
                    if file_obj.filename != file_name and file_obj.protection_source.name != vm_name:
                        module.fail_json(
                            msg="File '%s' is not available in virtual machine '%s' to restore" % (file_name, vm_name))
                    source_object_info = dict(jobId=file_obj.job_id,
                        protectionSourceId=file_obj.source_id,
                        environment="kVMware")

                get__job_information__for_file(module, source_object_info)

                # For VMware file restore, VM credentials are mandatory.
                if not (module.params.get('username') or module.params.get('password')):
                    module.fail_json(msg="Please provide VM credentials to to proceed with restore.")
                restore_data = dict(
                    name=module.params.get('job_name') + ": " + module.params.get('name'),
                    filenames=restore_file_list,
                    targetSourceId=vm_id,
                    targetParentSourceId=source_id,
                    sourceObjectInfo=source_object_info,
                    token=job_details['token'],
                    overwrite=module.params.get('overwrite'),
                    username=module.params.get('vm_username'),
                    password=module.params.get('vm_password'),
                    preserveAttributes=module.params.get('preserve_attributes'))

                if module.params.get('restore_location'):
                    restore_data['newBaseDirectory'] = module.params.get(
                        'restore_location')

                response.append(start_restore__files(module, restore_data))

            task = dict(
                changed=False
            )
            for jobCheck in response:
                restore_data['id'] = jobCheck['id']
                restore_data['environment'] = environment
                if module.params.get('wait_for_job'):
                    task = wait_restore_complete(module, restore_data)
                    jobCheck['status'] = task['status']

            results = dict(
                changed=True,
                msg="Registration of Cohesity Restore Job Complete",
                name=module.params.get('job_name') +
                ": " +
                module.params.get('name'),
                restore_jobs=response)
            if 'file_names' in job_details:
                results['filenames'] = job_details['file_names']

            if not task['changed'] and module.params.get('wait_for_job'):
                # => If the task failed to complete, then the key 'changed' will be False and
                # => we need to fail the module.
                results['changed'] = False
                results.pop('msg')
                errorCode = ""
                # => Set the errorCode to match the task['error'] if the key exists
                if 'error' in task:
                    errorCode = task['error']
                module.fail_json(
                    msg="Cohesity Restore Job Failed to complete",
                    error=errorCode,
                    **results)

    elif module.params.get('state') == "absent":

        results = dict(
            changed=False,
            msg="Cohesity Restore: This feature (absent) has not be implemented yet.",
            name=module.params.get('job_name') +
            ": " +
            module.params.get('name'))
    else:
        # => This error should never happen based on the set assigned to the parameter.
        # => However, in case, we should raise an appropriate error.
        module.fail_json(msg="Invalid State selected: {}".format(
            module.params.get('state')), changed=False)

    module.exit_json(**results)


if __name__ == '__main__':
    main()
