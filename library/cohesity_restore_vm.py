#!/usr/bin/python
# Copyright (c) 2018 Cohesity Inc
# Apache License Version 2.0

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url, urllib_error

try:
    # => When unit testing, we need to look in the correct location however, when run via ansible,
    # => the expectation is that the modules will live under ansible.
    from module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler, REQUEST_TIMEOUT
    from module_utils.storage.cohesity.cohesity_hints import get__prot_source_id__by_endpoint, \
        get__protection_jobs__by_environment, get__file_snapshot_information__by_filename, get__vmware_snapshot_information__by_vmname, \
        get__prot_source_root_id__by_environment, get__restore_job__by_type
except ImportError:
    from ansible.module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler, REQUEST_TIMEOUT
    from ansible.module_utils.storage.cohesity.cohesity_hints import get__prot_source_id__by_endpoint, \
        get__protection_jobs__by_environment, get__file_snapshot_information__by_filename, get__vmware_snapshot_information__by_vmname, \
        get__prot_source_root_id__by_environment, get__restore_job__by_type

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'supported_by': 'community',
    'status': ['preview']
}

DOCUMENTATION = '''
module: cohesity_restore_vm
short_description: Restore one or more Virtual Machines from Cohesity Protection Jobs
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
      - Specifies the environment type (such as VMware) of the Protection Source this Job
      - is protecting. Supported environment types include 'VMware'
    required: yes
    choices:
      - VMware
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
  vm_names:
    description:
      - Array of Virtual Machines to restore
    required: yes
  wait_for_job:
    description:
      - Should wait until the Restore Job completes
    type: bool
    default: yes
  wait_minutes:
    description:
      - Number of minutes to wait until the job completes.
    default: 20
  datastore_id:
    description:
      - Specifies the datastore where the files should be recovered to. This field is mandatory to recover objects to
      - a different resource pool or to a different parent source. If not specified, objects are recovered to their original
      - datastore locations in the parent source.
  datastore_folder_id:
    description:
      - Specifies the folder where the restore datastore should be created. This is applicable only when the VMs are being cloned.
  network_connected:
    description:
      - Specifies whether the network should be left in disabled state. Attached network is enabled by default. Set this flag to true to disable it.
    type: bool
    default: yes
  network_id:
    description:
      - Specifies a network configuration to be attached to the cloned or recovered object. Specify this field to override
      - the preserved network configuration or to attach a new network configuration to the cloned or recovered objects. You can
      - get the networkId of the kNetwork object by setting includeNetworks to 'true' in the GET /public/protectionSources operation.
      - In the response, get the id of the desired kNetwork object, the resource pool, and the registered parent Protection Source.
  power_state:
    description:
      - Specifies the power state of the cloned or recovered objects. By default, the cloned or recovered objects are powered off.
    type: bool
    default: yes
  resource_pool_id:
    description:
      - Specifies the resource pool where the cloned or recovered objects are attached.
  prefix:
    description:
      - Specifies a prefix to prepended to the source object name to derive a new name for the recovered or cloned object.
  suffix:
    description:
      - Specifies a suffix to appended to the original source object name to derive a new name for the recovered or cloned object
  vm_folder_id:
    description:
      - Specifies a folder where the VMs should be restored


extends_documentation_fragment:
    - cohesity
requirements: []

'''

EXAMPLES = '''

# Restore a single Virtual Machine
- name: Restore a Virtual Machine
  cohesity_restore_vm:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: "Ansible Test VM Restore"
    endpoint: "myvcenter.cohesity.demo"
    environment: "VMware"
    job_name: "myvcenter.cohesity.demo"
    vm_names:
      - chs-win-01

# Restore multiple Virtual Machines from a specific snapshot with a new prefix and disable the network
- name: Restore a Virtual Machine
  cohesity_restore_vm:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: "Ansible Test VM Restore"
    endpoint: "myvcenter.cohesity.demo"
    environment: "VMware"
    job_name: "myvcenter.cohesity.demo"
    backup_id: "48291"
    vm_names:
      - chs-win-01
      - chs-win-02
    prefix: "rst-"
    network_connected: no

'''

RETURN = '''

{
    "changed": true,
    "msg": "Registration of Cohesity Restore Job Complete",
    "name": "myvcenter.cohesity.demo Ansible Test VM Restore",
    "restore_jobs": [
        {
            "continueOnError": true,
            "fullViewName": "cohesity_int_54879",
            "id": 54879,
            "newParentId": 1,
            "objects": [
                {
                    "jobRunId": 48291,
                    "jobUid": {
                        "clusterId": 8621173906188849,
                        "clusterIncarnationId": 1538852526333,
                        "id": 46969
                    },
                    "protectionSourceId": 1049,
                    "startedTimeUsecs": 1547151172462136
                }
            ],
            "poweredOn": false,
            "prefix": "rst-",
            "startTimeUsecs": 1548083898761275,
            "status": "Finished",
            "targetViewCreated": true,
            "type": "kRecoverVMs",
            "username": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "viewBoxId": 5,
            "vm_names": [
                "chs-win-01"
            ],
            "vmwareParameters": {}
        }
    ]
}

'''


class ParameterViolation(Exception):
    pass


def check__protection_restore__exists(module, self):
    payload = self.copy()
    payload['restore_type'] = "kRecoverVMs"
    payload['count'] = 1

    restore_tasks = get__restore_job__by_type(module, payload)

    if restore_tasks:
        task_list = [
            task for task in restore_tasks if task['name'] == self['name']]
        for task in task_list:
            if task['status'] != 'kFinished':
                return True
    return False


def get_source_details(module, restore_to_source):
    '''
    Get VMware protection source details
    :param module: object that holds parameters passed to the module
    :param restore_to_source: boolean flag to get target source details or
    vm's parent source details
    :return:
    '''
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = get__cohesity_auth__token(module)
    try:
        uri = "https://" + server + \
              "/irisservices/api/v1/public/protectionSources/rootNodes?environments=kVMware"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token,
                   "user-agent": "cohesity-ansible/v2.2.0"}
        response = open_url(
            url=uri,
            headers=headers,
            validate_certs=validate_certs,
            method="GET", timeout=REQUEST_TIMEOUT)
        response = json.loads(response.read())
        source_details = dict()
        for source in response:
            if not restore_to_source and source['protectionSource']['name'] == module.params.get('endpoint'):
                source_details['id'] = source['protectionSource']['id']
            elif restore_to_source and source['protectionSource']['name'] == module.params.get('restore_to_source'):
                source_details['id'] = source['protectionSource']['id']
        if not source_details:
            module.fail_json(
                changed=False,
                msg="Can't find the endpoint on the cluster")
        return source_details
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_vmware_source_objects(module, source_id):
    '''
    :param module: object that holds parameters passed to the module
    :param source_id: protection source id
    :return:
    '''
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = get__cohesity_auth__token(module)
    try:
        uri = "https://" + server + "/irisservices/api/v1/public/protectionSources?id=" + str(
            source_id) + "&excludeTypes=kVirtualMachine" + "&includeDatastores=true"

        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token,
                   "user-agent": "cohesity-ansible/v2.2.0"}

        response = open_url(
            url=uri,
            method='GET',
            headers=headers,
            validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)
        response = json.loads(response.read())
        return response
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_vmware_object_id(source_objects, object_name, object_type):
    '''
    :param source_objects: protection source object tree
    :param object_name: resource pool name or datastore name
    :param object_type: type of the object like kResourcePool, kDatastore
    :return:
    '''
    nodes = []
    for node in source_objects:
        if 'nodes' in node:
            nodes.append(node['nodes'])
        if ('protectionSource' in node) and (node['protectionSource']['name'] == object_name) and\
                node['protectionSource']['vmWareProtectionSource']['type'] == object_type:
            return node['protectionSource']['id']

    while len(nodes) != 0:
        objects = nodes.pop()
        for node in objects:
            if 'nodes' in node:
                nodes.append(node['nodes'])
            if ('protectionSource' in node) and (node['protectionSource']['name'] == object_name) and \
                    node['protectionSource']['vmWareProtectionSource']['type'] == object_type:
                return node['protectionSource']['id']
    return None


def get__vmware_snapshot_information__by_source(module, self, source_details):
    '''
    Get the snapshot information using environment, VMname and source id filters
    :param module: object that holds parameters passed to the module
    :param self: restore task details
    :param source_details: parent protection source details
    :return:
    '''
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    try:
        uri = "https://" + server + \
            "/irisservices/api/v1/public/restore/objects" + \
            "?environments=kVMware&search=" + self['restore_obj']['vmname'] +\
              "&registeredSourceIds=" + str(source_details['id'])

        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token,
                   "user-agent": "cohesity-ansible/v2.2.0"}
        objects = open_url(url=uri, headers=headers,
                           validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)
        objects = json.loads(objects.read())
        return objects
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


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
            msg="Failed to find chosen Job name for the selected Environment Type."
        )
        module.fail_json(**failure)
    else:
        # => Since we are filtering out any job that matches our name
        # => we will need to properly just grab the first element as
        # => it is returned as an array.
        return job_data[0]


def get_snapshot_information_for_vmname(module, self):
    restore_objects = []
    job_data = dict()
    job_data['uid'] = dict(
        clusterId='',
        clusterIncarnationId='',
        id=''
    )
    if self['job_name']:
        # => Return the Protection Job information based on the Environment and Job Name
        job_data = get__job_information__for_restore(module, self)
    else:
        source_details = get_source_details(module, False)
    # => Create a restore object for each Virtual Machine
    for vmname in self['vm_names']:
        # => Build the Restore Dictionary Object
        restore_details = dict(
            jobRunId="",
            jobUid=dict(
                clusterId=job_data['uid']['clusterId'],
                clusterIncarnationId=job_data['uid']['clusterIncarnationId'],
                id=job_data['uid']['id']
            ),
            startedTimeUsecs=""
        )
        self['restore_obj'] = restore_details.copy()
        self['restore_obj']['vmname'] = vmname
        if self['job_name']:
            output = get__vmware_snapshot_information__by_vmname(module, self)
        else:
            output = get__vmware_snapshot_information__by_source(module, self, source_details)

        if not output or output['totalCount'] == 0:
            failure = dict(
                changed=False,
                job_name=self['job_name'],
                vmname=vmname,
                environment=self['environment'],
                msg="Failed to find a snapshot on the cluster"
            )
            module.fail_json(**failure)

        # => TODO: Add support for selecting a previous backup.
        # => For now, let's just grab the most recent snapshot.
        success = False
        # when job name is given, select the most recent snapshot from the job
        if self['job_name']:
            for snapshot_info in output.get('objectSnapshotInfo', []):
                if snapshot_info['objectName'] == vmname:
                    snapshot_detail = snapshot_info['versions'][0]
                    if 'jobRunId' in self:
                        snapshot_detail = [jobRun for jobRun in snapshot_info['versions']
                                           if jobRun['jobRunId'] == int(self['jobRunId'])][0]

                    restore_details['protectionSourceId'] = snapshot_info['snapshottedSource']['id']
                    restore_details['jobRunId'] = snapshot_detail['jobRunId']
                    restore_details['startedTimeUsecs'] = snapshot_detail['startedTimeUsecs']
                    success = True
        else:
            # when job name is not given, select the most recent snapshot across all the jobs
            timestamp = 0
            for snapshot_info in output['objectSnapshotInfo']:
                if snapshot_info['objectName'] == vmname and snapshot_info['versions'][0]['startedTimeUsecs'] >= timestamp:
                    timestamp = snapshot_info['versions'][0]['startedTimeUsecs']
                    restore_details['protectionSourceId'] = snapshot_info['snapshottedSource']['id']
                    restore_details['jobRunId'] = snapshot_info['versions'][0]['jobRunId']
                    restore_details['jobUid'] = snapshot_info['jobUid']
                    restore_details['startedTimeUsecs'] = snapshot_info['versions'][0]['startedTimeUsecs']
                    success = True
        if not success:
            module.fail_json(msg="No Snapshot Found for the VM: " + vmname)
        restore_objects.append(restore_details)
    return restore_objects


# => Perform the Restore of a Virtual Machine to the selected ProtectionSource Target
def start_restore__vms(module, self):
    payload = self.copy()
    payload.pop('vm_names', None)
    return start_restore(module, "/irisservices/api/v1/public/restore/recover", payload)


def start_restore(module, uri, self):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    try:
        uri = "https://" + server + uri
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token,
                   "user-agent": "cohesity-ansible/v2.2.0"}
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
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token,
                   "user-agent": "cohesity-ansible/v2.2.0"}
        attempts = 0
        # => Wait for the restore based on a predetermined number of minutes with checks every 30 seconds.
        while attempts < wait_counter:

            response = open_url(url=uri, headers=headers,
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
            if self['environment'] == "VMware":
                wait_results['error'] = [elem['error']['message']
                                         for elem in response['restoreObjectState']]
            else:
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
            name=dict(type='str', required=True),
            state=dict(choices=['present', 'absent',
                                'started', 'stopped'], default='present'),
            endpoint=dict(type='str', required=True),
            restore_to_source=dict(type='str', default=''),
            job_name=dict(type='str', default=''),
            backup_id=dict(type='str'),
            backup_timestamp=dict(type='str'),
            # => Currently, the only supported environments types are list in the choices
            # => For future enhancements, the below list should be consulted.
            # => 'SQL', 'View', 'Puppeteer', 'Pure', 'Netapp', 'HyperV', 'Acropolis', 'Azure'
            environment=dict(
                choices=['VMware'],
                default='VMware'
            ),
            vm_names=dict(type='list'),
            wait_for_job=dict(type='bool', default=True),
            wait_minutes=dict(type='str', default=20),
            datastore_id=dict(type='str'),
            datastore_name=dict(type='str', default=''),
            datastore_folder_id=dict(type='str'),
            network_connected=dict(type='bool', default=True),
            network_id=dict(type='str'),
            power_state=dict(type='bool', default=True),
            prefix=dict(type='str'),
            resource_pool_id=dict(type='str'),
            resource_pool_name=dict(type='str', default=''),
            suffix=dict(type='str'),
            vm_folder_id=dict(type='str')

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

    )
    if module.params.get('job_name'):
        job_details['name'] = module.params.get('job_name') + ": " + module.params.get('name')
    else:
        job_details['name'] = module.params.get('name')

    if module.params.get('backup_id'):
        job_details['jobRunId'] = module.params.get('backup_id')

    if module.params.get('backup_timestamp'):
        job_details['backup_timestamp'] = module.params.get('backup_timestamp')

    job_exists = check__protection_restore__exists(module, job_details)

    if module.check_mode:
        check_mode_results = dict(
            changed=False,
            msg="Check Mode: Cohesity Protection Restore Job is not currently registered",
            id=""
        )
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
                name=job_details['name']
            )
        else:
            # check__mandatory__params(module)
            environment = module.params.get('environment')
            response = []

            if environment == "VMware":
                job_details['vm_names'] = module.params.get('vm_names')
                source_object_info = get_snapshot_information_for_vmname(
                    module, job_details)

                restore_data = dict(
                    name=job_details['name'],
                    vm_names=module.params.get('vm_names'),
                    objects=source_object_info,
                    token=job_details['token'],
                    type="kRecoverVMs",
                    vmwareParameters=dict(
                        poweredOn=module.params.get('power_state'),
                        disableNetwork=module.params.get('network_connected')
                    )
                )

                if module.params.get('prefix'):
                    restore_data['vmwareParameters']['prefix'] = module.params.get(
                        'prefix')
                if module.params.get('suffix'):
                    restore_data['vmwareParameters']['suffix'] = module.params.get(
                        'suffix')

                if module.params.get('restore_to_source'):
                    datastore_id = module.params.get('datastore_id')
                    resource_pool_id = module.params.get('resource_pool_id')
                    restore_to_source_details = get_source_details(module, True)
                    restore_to_source_objects = get_vmware_source_objects(module, restore_to_source_details['id'])
                    if (module.params.get('resource_pool_id') or module.params.get('resource_pool_name')) and\
                            (module.params.get('datastore_id') or module.params.get('datastore_name')):

                        if module.params.get('resource_pool_name'):
                            resource_pool_id =\
                                get_vmware_object_id(restore_to_source_objects,
                                                     module.params.get('resource_pool_name'), 'kResourcePool')
                        if module.params.get('datastore_name'):
                            datastore_id = get_vmware_object_id(restore_to_source_objects,
                                                                module.params.get('datastore_name'), 'kDatastore')

                        if not datastore_id or not resource_pool_id:
                            module.fail_json(msg="Failed to find the resource pool"
                                                 " or datastore on the target source")

                        restore_data['newParentId'] = restore_to_source_details['id']
                        restore_data['vmwareParameters']['resourcePoolId'] = resource_pool_id
                        restore_data['vmwareParameters']['datastoreId'] = datastore_id

                        # => Optional VMware Parameters
                        if module.params.get('datastore_folder_id'):
                            restore_data['vmwareParameters']['datastoreFolderId'] = module.params.get(
                                'datastore_folder_id')
                        if module.params.get('network_id'):
                            restore_data['vmwareParameters']['networkId'] = module.params.get(
                                'network_id')
                        if module.params.get('vm_folder_id'):
                            restore_data['vmwareParameters']['vmFolderId'] = module.params.get(
                                'vm_folder_id')
                    else:
                        module.fail_json(msg="The resource pool and datastore details are"
                                             " required for restoring to a new location")

                # => Start the Virtual Machine Restore operation
                job_start = start_restore__vms(module, restore_data)
                job_start['vm_names'] = job_details['vm_names']
                response.append(job_start)

            else:
                # => This error should never happen based on the set assigned to the parameter.
                # => However, in case, we should raise an appropriate error.
                module.fail_json(msg="Invalid Environment Type selected: {0}".format(
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
                name=module.params.get('job_name') + ": " +
                module.params.get('name'),
                restore_jobs=response
            )

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
                    msg="Cohesity Restore Job Failed to complete", error=errorCode, **results)

    elif module.params.get('state') == "absent":

        results = dict(
            changed=False,
            msg="Cohesity Restore: This feature (absent) has not be implemented yet.",
            name=module.params.get('job_name') + ": " + module.params.get('name')
        )
    else:
        # => This error should never happen based on the set assigned to the parameter.
        # => However, in case, we should raise an appropriate error.
        module.fail_json(msg="Invalid State selected: {}".format(
            module.params.get('state')), changed=False)

    module.exit_json(**results)


if __name__ == '__main__':
    main()
