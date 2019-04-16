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

try:
    # => When unit testing, we need to look in the correct location however, when run via ansible,
    # => the expectation is that the modules will live under ansible.
    from module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler
    from module_utils.storage.cohesity.cohesity_hints import get__prot_source_id__by_endpoint, \
        get__protection_jobs__by_environment, get__file_snapshot_information__by_filename, \
        get__prot_source_root_id__by_environment, get__restore_job__by_type
except ImportError:
    from ansible.module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler
    from ansible.module_utils.storage.cohesity.cohesity_hints import get__prot_source_id__by_endpoint, \
        get__protection_jobs__by_environment, get__file_snapshot_information__by_filename, \
        get__prot_source_root_id__by_environment, get__restore_job__by_type

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'supported_by': 'community',
    'status': ['preview']
}

DOCUMENTATION = '''
module: cohesity_restore_file
short_description: Restore Files and Folders from Cohesity Protection Jobs
description:
    - Ansible Module used to start a Cohesity Recovery Job on a Cohesity Cluster.
    - When executed in a playbook, the Cohesity Recovery Job will be validated and the appropriate state action
    - will be applied.
version_added: '2.6.5'
author:
  - Jeremy Goodrum (github.com/exospheredata)
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
  environment:
    description:
      - Specifies the environment type (such as PhysicalFiles or GenericNas) of the Protection Source this Job
      - is protecting. Supported environment types include 'PhysicalFiles', 'GenericNas'
    required: yes
    choices:
      - PhysicalFiles
      - GenericNas
  job_name:
    description:
      - Name of the Protection Job
    required: yes
  endpoint:
    description:
      - Specifies the network endpoint of the Protection Source where it is reachable. It could
      - be an URL or hostname or an IP address of the Protection Source or a NAS Share/Export Path.
    required: yes
    aliases:
      - hostname
      - ip_address
  backup_id:
    description:
      - Optional Cohesity ID to use as source for the Restore operation.  If not selected, the most recent RunId will be used
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


extends_documentation_fragment:
    - cohesity
requirements: []
notes:
    - File and Folder restores from SMB based backups are currently not supported
'''

EXAMPLES = '''
# Restore a single file from a Physical Windows Backup
- cohesity_restore_file:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: Restore Single File
    job_name: myhost
    environment: PhysicalFiles
    endpoint: mywindows.host.lab
    file_names:
      - C:\\data\\big_file
    wait_for_job: no

# Restore a single file from a GenericNas NFS Backup and wait for the job to complete
- cohesity_restore_file:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: Restore Single File to NFS Location
    job_name: mynfs
    environment: GenericNas
    endpoint: mynfs.host.lab:/exports
    file_names:
      - /data
    restore_location: /restore
    wait_for_job: yes

# Restore multiple files from a specific Physical Windows Backup and wait for up to 10 minutes for the process to complete
- cohesity_restore_file:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: Restore Single File
    job_name: myhost
    environment: PhysicalFiles
    endpoint: mywindows.host.lab
    file_names:
      - C:\\data\\files
      - C:\\data\\large_directory
    wait_for_job: yes
    wait_minutes: 10
'''

RETURN = '''
{
    "changed": true,
    "failed": false,
    "filenames": [
        "C:\\data\\files"
    ],
    "msg": "Registration of Cohesity Restore Job Complete",
    "name": "mywindows: Ansible Test Multi-File Restore",
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


# => This method will convert the Windows Based file paths into correctly formatted
# => versions consumable by Cohesity Restore Jobs.
def convert__windows_file_name(filename):

    # => Raise an exception if the Path format is incorrect
    if '\\' in filename and ':' not in filename:
        msg = "Windows Based files must be in /Drive/path/to/file or Drive:\\path\\to\\file format."
        raise ParameterViolation(msg)

    get_file_source = filename.split(":")
    if len(get_file_source) > 1:
        drive_letter = "/" + get_file_source[0]
        file_path = get_file_source[1]
    else:
        drive_letter = ""
        file_path = filename

    # => Replace the back slashes with forward slashes.
    for char in ("\\\\", "\\"):
        file_path = file_path.replace(char, "/")

    # => Combine the Drive Letter and the Formmated File Path for the restore
    filename = drive_letter + file_path
    return filename


# => Remove the Prefix from a File Path.  This is used to remove the Share
# => or Export path from the restored file information.
def strip__prefix(prefix, file_path):

    if file_path.startswith(prefix):
        return file_path[len(prefix):]
    return file_path


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


# => Return an Object containing information for the file based restore
def get__snapshot_information__for_file(module, self):
    restore_objects = []
    # => Return the Protection Job information based on the Environment and Job Name
    job_data = get__job_information__for_restore(module, self)

    for filename in self['file_names']:
        # => Build the Restore Dictionary Object
        restore_details = dict(
            jobRunId="",
            jobUid=dict(
                clusterId=job_data['uid']['clusterId'],
                clusterIncarnationId=job_data['uid']['clusterIncarnationId'],
                id=job_data['uid']['id']
            ),
            protectionSourceId=self['endpoint'],
            startedTimeUsecs=""
        )
        self['restore_obj'] = restore_details.copy()
        self['restore_obj']['filename'] = filename
        output = get__file_snapshot_information__by_filename(module, self)
        if not output:
            failure = dict(
                changed=False,
                job_name=self['job_name'],
                filename=filename,
                environment=self['environment'],
                msg="Failed to find a snapshot for the file in the chosen Job name.")
            module.fail_json(**failure)

        # => TODO: Add support for selecting a previous backup.
        # => For now, let's just grab the most recent snapshot.
        if 'jobRunId' in self:
            output = [jobRun for jobRun in output if jobRun['snapshot']
                      ['jobRunId'] == int(self['jobRunId'])]

        if 'backup_timestamp' in self:
            snapshot_timestamp = datetime.strptime(
                self['backup_timestamp'], '%Y-%m-%d:%H:%M').replace(second=0)
            jobRuns = output
            output = []
            for jobRun in jobRuns:
                t = datetime.strptime(
                    time.ctime(
                        jobRun['snapshot']['startedTimeUsecs'] /
                        1000000),
                    '%a %b %d %H:%M:%S %Y').replace(
                    second=0)
                if snapshot_timestamp == t:
                    output.append(jobRun)
                    break

        # => If the file has no snapshot, then we will need to fail out this call
        if len(output) == 0:
            # failed_file = filename.replace("/","",1).replace("/","\\").replace("\\",":\\",1)
            module.fail_json(
                msg="Cohesity Restore failed",
                error="No snapshot exists for the file " +
                filename)
        snapshot_info = output[0]
        restore_details['jobRunId'] = snapshot_info['snapshot']['jobRunId']
        restore_details['startedTimeUsecs'] = snapshot_info['snapshot']['startedTimeUsecs']

        exists = [item for item in restore_objects if item['jobRunId']
                  == restore_details['jobRunId']]
        if not exists:
            restore_objects.append(restore_details)
    return restore_objects


# => Perform the Restore of a File to the selected ProtectionSource Target
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
                   "Authorization": "Bearer " + token}
        payload = self.copy()

        # => Remove the Authorization Token from the Payload
        payload.pop('token', None)

        data = json.dumps(payload)

        response = open_url(url=uri, data=data, headers=headers,
                            validate_certs=validate_certs)

        response = json.loads(response.read())

        # => Remove the Job name as it will be duplicated back to our process.
        response.pop('name')

        return response
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


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
            "Authorization": "Bearer " + token}
        attempts = 0
        # => Wait for the restore based on a predetermined number of minutes with checks every 30 seconds.
        while attempts < wait_counter:

            response = open_url(
                url=uri,
                headers=headers,
                validate_certs=validate_certs)
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
            environment=dict(
                choices=['PhysicalFiles', 'GenericNas'],
                default='PhysicalFiles'
            ),
            job_name=dict(type='str', required=True),
            endpoint=dict(type='str', required=True),
            backup_id=dict(type='str'),
            backup_timestamp=dict(type='str'),
            file_names=dict(type='list', required=True),
            wait_for_job=dict(type='bool', default=True),
            overwrite=dict(type='bool', default=True),
            preserve_attributes=dict(type='bool', default=True),
            restore_location=dict(type='str'),
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
            # check__mandatory__params(module)
            environment = module.params.get('environment')
            response = []

            if environment == "PhysicalFiles" or environment == "GenericNas":
                # => Gather the Source Details
                job_details['file_names'] = module.params.get('file_names')
                prot_source = dict(
                    environment="Physical",
                    token=job_details['token'],
                    endpoint=module.params.get('endpoint')

                )
                if environment == "GenericNas":
                    prot_source['environment'] = "GenericNas"
                source_id = get__prot_source_id__by_endpoint(
                    module, prot_source)
                if not source_id:
                    module.fail_json(
                        msg="Failed to find the endpoint on the cluster",
                        changed=False)
                job_details['endpoint'] = source_id
                source_object_info = get__snapshot_information__for_file(
                    module, job_details)

                # => For every file to be restored, we need to ensure that Windows style names
                # => have been converted into Unix style names else, the restore job will
                # => fail.
                #
                # => However, only if this is a PhysicalFiles Type
                restore_file_list = []
                for restore_file in job_details['file_names']:
                    if environment == "PhysicalFiles":
                        restore_file_list.append(
                            convert__windows_file_name(restore_file))
                    elif environment == "GenericNas":
                        restore_file_list.append(strip__prefix(
                            job_details['endpoint'], restore_file))
                    else:
                        restore_file_list = restore_file

                for objectInfo in source_object_info:
                    restore_data = dict(
                        name=module.params.get('job_name') +
                        ": " +
                        module.params.get('name'),
                        filenames=restore_file_list,
                        targetSourceId=objectInfo['protectionSourceId'],
                        sourceObjectInfo=objectInfo,
                        token=job_details['token'],
                        overwrite=module.params.get('overwrite'),
                        preserveAttributes=module.params.get('preserve_attributes'))

                    if module.params.get('restore_location'):
                        restore_data['newBaseDirectory'] = module.params.get(
                            'restore_location')

                    response.append(start_restore__files(module, restore_data))

            else:
                # => This error should never happen based on the set assigned to the parameter.
                # => However, in case, we should raise an appropriate error.
                module.fail_json(
                    msg="Invalid Environment Type selected: {0}".format(
                        module.params.get('environment')), changed=False)

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
