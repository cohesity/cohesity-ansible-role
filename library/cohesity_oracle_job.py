#!/usr/bin/python
# Copyright (c) 2020 Cohesity Inc
# Apache License Version 2.0

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import copy
import json
import time
from ansible.module_utils.basic import AnsibleModule
from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.exceptions.api_exception import APIException
from cohesity_management_sdk.models.delete_protection_job_param import DeleteProtectionJobParam
from cohesity_management_sdk.models.cancel_protection_job_run_param import CancelProtectionJobRunParam
from cohesity_management_sdk.models.environment_type_job_parameters import EnvironmentTypeJobParameters
from cohesity_management_sdk.models.oracle_special_parameters import OracleSpecialParameters
from cohesity_management_sdk.models.oracle_env_job_parameters import OracleEnvJobParameters
from cohesity_management_sdk.models.protection_job_request_body import ProtectionJobRequestBody
from cohesity_management_sdk.models.source_special_parameter import SourceSpecialParameter
from cohesity_management_sdk.models.run_protection_job_param import RunProtectionJobParam

try:
    # => When unit testing, we need to look in the correct location however, when run via ansible,
    # => the expectation is that the modules will live under ansible.
    from module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from module_utils.storage.cohesity.cohesity_hints import get_cohesity_client
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler
except Exception as e:
    from ansible.module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from ansible.module_utils.storage.cohesity.cohesity_hints import get_cohesity_client
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'supported_by': 'community',
    'status': ['preview']
}


EXAMPLES = '''
# Create a new Oracle Server Protection Job
- cohesity_oracle_job:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: myhost
    endpoint: cohesity-cluster-vip
    protection_policy: Bronze
    storage_domain: Default

'''

RETURN = '''
Returns the registered Protection Job ID
'''


class ParameterViolation(Exception):
    pass


class ProtectionException(Exception):
    pass


def get_timezone():
    # Function to get ansible control node timezone.
    # :returns timezone
    default_timezone = "America/Los_Angeles"
    try:
        import subprocess
        cmd = "timedatectl status"
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        out, err = proc.communicate()
        for line in out.split("\n"):
            if "Time zone" in line:
                default_timezone = line.split()[2]
    except Exception as err:
        pass
    finally:
        return default_timezone



def get_source_id_by_endpoint(module):
    # Fetch source id using endpoint
    try:
        endpoint = module.params.get('endpoint')
        env = module.params.get('environment')
        resp = cohesity_client.protection_sources.list_protection_sources(environments=env)
        if resp:
            parent_id = resp[0].protection_source.id
            nodes = resp[0].nodes
            for node in nodes:
                if node['protectionSource']['name'] == endpoint:
                    source = node['protectionSource']
                    return parent_id, source['id']
        return None, None
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def check__mandatory__params(module):
    # => This method will perform validations of optionally mandatory parameters
    # => required for specific states and environments.
    success = True
    missing_params = list()
    environment = module.params.get('environment')

    if module.params.get('state') == 'present':
        action = 'creation'

        if not module.params.get('endpoint'):
            success = False
            missing_params.append('endpoint')
        if not module.params.get('protection_policy'):
            success = False
            missing_params.append('protection_policy')
        if not module.params.get('storage_domain'):
            success = False
            missing_params.append('storage_domain')

    else:
        action = 'remove'

    if not success:
        module.fail_json(
            msg='The following variables are mandatory for this action (' +
            action +
            ') when working with environment type (' +
            environment +
            ')',
            missing=missing_params)


def get__prot_policy_id__by_name(module):
    try:
        name = module.params.get('protection_policy')
        resp = cohesity_client.protection_policies.get_protection_policies(names=name)
        if not resp:
            module.exit_json(output='Please provide a valid protection policy name')
        return resp[0].id
    except Exception as error:
        raise__cohesity_exception__handler(error, module)



def get__storage_domain_id__by_name(module):
    try:
        name = module.params.get('storage_domain')
        resp = cohesity_client.view_boxes.get_view_boxes(names=name)
        if not resp:
            module.exit_json(output='Please provide a valid storage domain name')
        return resp[0].id
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def get_protection_run__status__by_id(module, job_id):
    try:
        job_run = cohesity_client.protection_runs.get_protection_runs(
            job_id=job_id)
        if not job_run:
            return False, '', ''
        # Fetch the status of last job run.
        last_run = job_run[0]
        status = last_run.backup_run.status
        if status == 'kAccepted':
            return True, status, last_run
        elif status in ['kCanceled', 'kSuccess']:
            return False, status, last_run
        return False, status, ''
    except Exception as error:
        raise__cohesity_exception__handler(error, module)

def check__protection_job__exists(module):
    try:
        name = module.params.get('name')
        environment = module.params.get('environment')
        job_list = cohesity_client.protection_jobs.get_protection_jobs(
            names=name, environments=environment, is_active=True)

        for job in job_list:
            if job.name == name:
                return job.id, job

        return False, ''
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def wait__for_job_state__transition(module, job_id, state='start'):
    if state != 'start':
        state = 'stop'
    loop_cnt = 0
    while loop_cnt <= 3:
        # => If the backup finishes before we check, we need to look
        # => at previous backups to see if the last job is successful.
        currently_active, status, last_run = get_protection_run__status__by_id(
            module, job_id)
        if state == 'start' and status == 'kAccepted':
            return
        elif state == 'stop' and status in ['kSuccess', 'kCanceled']:
            return
        else:
            time.sleep(5)
            loop_cnt += 1

    if loop_cnt == 21:
        module.fail_json(msg='Failed to successfully ' + state +
            ' the Cohesity Protection Job',
            changed=False,
            id=job_id,
            loop_cnt=loop_cnt)


def start_job(module):
    # => Get job id.
    job_exists, job = check__protection_job__exists(module)
    if not job_exists:
        name=module.params.get('name')
        results = dict(
            changed=False,
            msg='Protection Job with name ' + name + ' is not available.'
        )
        module.exit_json(**results)
    job_id = job.uid.id
    currently_active, status, last_run = get_protection_run__status__by_id(module, job_id)
    if currently_active == True:
        results = dict(
            changed=False,
            msg='The Protection Job for this host is currently running',
            name=module.params.get('name')
        )
        module.exit_json(**results)

    try:
        body = RunProtectionJobParam()
        body.run_type = 'k' + module.params.get('ondemand_run_type')
        response = cohesity_client.protection_jobs.create_run_protection_job(
            job_id, body)

        # => This dictionary will allow us to return a standardized output
        # => for all Protection Job.
        output = dict(
            id=job_id
        )

        # => It can take a few moments for the job to actually stop.  In this case,
        # => We will introduce a delay and check every (5) seconds for up to a minute
        # => to see if the job stopped.
        wait__for_job_state__transition(
            module, job_id, state='start')

        return output
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def stop_job(module, _id):
    currently_active, status, last_run = get_protection_run__status__by_id(module, _id)
    if not currently_active:
        results = dict(
            changed=False,
            msg='The Protection Job for this host is not currently running',
            name=module.params.get('name')
        )
        module.exit_json(**results)
    if not module.params.get('cancel_active') and currently_active:
        module.fail_json(
            changed=False,
            msg='The Protection Job for this host is active and cannot be stopped')
    try:

        output = dict(
            id=_id,
            cancel_active=module.params.get('cancel_active'),
            jobRunIds=list()
        )
        body = CancelProtectionJobRunParam()
        body.job_run_id = last_run.backup_run.job_run_id
        resp = cohesity_client.protection_runs.create_cancel_protection_job_run(_id, body)

        # => It can take a few moments for the job to actually stop.  In this case,
        # => We will introduce a delay and check every (5) seconds for up to a minute
        # => to see if the job stopped.
        wait__for_job_state__transition(
            module, _id, state='stop')

        return output
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def unregister_job(module, _id):
    '''
    Unregister a protection job.
    '''
    try:
        body = DeleteProtectionJobParam()
        body.delete_snapshots = module.params.get('delete_backups')
        resp = cohesity_client.protection_jobs.delete_protection_job(_id, body)
        return resp
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def main():
    # => Load the default arguments including those specific to the Cohesity Protection Jobs.
    argument_spec = cohesity_common_argument_spec()
    argument_spec.update(
        dict(
            state=dict(choices=['present', 'absent',
                                'started', 'stopped'], default='present'),
            name=dict(type='str', required=True, aliases=['job_name']),
            description=dict(type='str', default=''),
            environment=dict(default='kOracle'),
            protection_policy=dict(type='str', aliases=['policy'], default='Bronze'),
            storage_domain=dict(type='str', default='DefaultStorageDomain'),
            time_zone=dict(type='str', default=''),
            start_time=dict(type='str', default=''),
            delete_backups=dict(type='bool', default=False),
            ondemand_run_type=dict(
                choices=['Regular', 'Full', 'Log', 'System'], default='Regular'),
            cancel_active=dict(type='bool', default=False),
            validate_certs=dict(type='bool', default=False),
            endpoint=dict(type=str, default=''),
            databases=dict(type=list, default=[]),
        )
    )

    # => Create a new module object
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    if not module.params.get("time_zone"):
        module.params["time_zone"] = get_timezone()
    global cohesity_client
    cohesity_client = get_cohesity_client(module)

    results = dict(
        changed=False,
        msg='Attempting to manage Protection Source',
        state=module.params.get('state')
    )

    job_exists, job_meta_data = check__protection_job__exists(module)

    if module.check_mode:
        check_mode_results = dict(
            changed=False,
            msg='Check Mode: Cohesity Protection Job is not currently registered',
            id='')
        if module.params.get('state') == 'present':
            if job_exists:
                check_mode_results[
                    'msg'] = 'Check Mode: Cohesity Protection Job is currently registered.  No changes'
            else:
                check_mode_results[
                    'msg'] = 'Check Mode: Cohesity Protection Job is not currently registered.  This action would register the Cohesity Protection Job.'
                check_mode_results['id'] = job_exists
        else:
            if job_exists:
                check_mode_results[
                    'msg'] = 'Check Mode: Cohesity Protection Job is currently registered.  This action would unregister the Cohesity Protection Job.'
                check_mode_results['id'] = job_exists
            else:
                check_mode_results[
                    'msg'] = 'Check Mode: Cohesity Protection Job is not currently registered.  No changes.'
        module.exit_json(**check_mode_results)

    elif module.params.get('state') == 'present':
        parent_id, source_id = get_source_id_by_endpoint(module)
        if not (parent_id and source_id):
            module.fail_json(msg="Source '%s' is not registered to cluster, Please register the source and try again." % module.params.get('endpoint'))
        check__mandatory__params(module)
        body = ProtectionJobRequestBody()
        body.name = module.params.get('name')
        body.parent_source_id = source_id
        body.source_ids = [source_id]
        body.view_box_id = get__storage_domain_id__by_name(module)
        body.environment = module.params.get('environment')
        body.policy_id = get__prot_policy_id__by_name(module)
        body.timezone = module.params.get('time_zone').strip()
        body.description = module.params.get('description')
        databases = module.params.get('databases')
        if databases:
            entity_ids = list()
            application_nodes = []
            body.source_special_parameters = list()
            resp = cohesity_client.protection_sources.list_protection_sources(
                environment='kOracle', id=parent_id)

            if not resp:
                module.fail_json(msg="Oracle source is not available to protect")

            for node in resp[0].nodes:
                application_nodes.extend(node.get("applicationNodes", []))

            # Make copy of database list and remove once entity id fetched. This check
            # is to ensure availability of databases in server.
            copy_database = copy.deepcopy(databases)
            for database in databases:
                for node in application_nodes:
                    if node["protectionSource"]["name"] == database.strip():
                        entity_ids.append(node["protectionSource"]["id"])
                        copy_database.remove(database)
                if len(databases) == len(entity_ids):
                    break
            if copy_database:
                module.fail_json("Following list of databases are not available in the "
                                 "Oracle Server: %s" % ", ".join(copy_database))
            spl_params = SourceSpecialParameter()
            spl_params.source_id = source_id
            spl_params.oracle_special_parameters = OracleSpecialParameters()
            spl_params.oracle_special_parameters.application_entity_ids = entity_ids
            body.source_special_parameters.append(spl_params)

        if module.params.get('start_time'):
            start_time = list(module.params.get(
                'start_time').replace(':', ''))
            if not len(start_time) == 4:
                # => There are only so many options here but if we get more characters
                # => than four then we need to escape quickly.
                module.fail_json(
                    msg='Invalid start_time selected (' +
                    module.params.get('start_time') +
                    ').  Please review and submit the correct Protection Job Starting time.')
            body.start_time = dict(
                hour=int(start_time[0] + start_time[1]),
                minute=int(start_time[2] + start_time[3])
            )
        try:
            if job_exists:
                response = cohesity_client.protection_jobs.update_protection_job(body, job_exists)
                msg = 'Updation of Cohesity Protection Job Complete'
            else:
                response = cohesity_client.protection_jobs.create_protection_job(body)
                msg = 'Creation of Cohesity Protection Job Complete'
            response = dict(id=response.id,
                            name=response.name,
                            environment=response.environment)

            results = dict(
                changed=True,
                msg=msg,
                **response
            )
        except APIException as err:
            module.fail_json(msg=err.message)

    elif module.params.get('state') == 'absent':
        if job_exists:
            job_id = job_meta_data.uid.id
            status, _, _ = get_protection_run__status__by_id(module, job_id)
            if status:
                stop_job(module, job_id)
                while True: 
                    status, _, _ = get_protection_run__status__by_id(module, job_id)
                    if not status:
                        time.sleep(10)
                        break
            response = unregister_job(module, job_exists)

            results = dict(
                changed=True,
                msg='Unregistration of Cohesity Protection Job Complete',
                id=job_exists,
                name=module.params.get('name')
            )
        else:
            results = dict(
                changed=False,
                msg='The Protection Job for this host is currently not registered',
                name=module.params.get('name'))

    elif module.params.get('state') == 'started':
        if job_exists:
            response = start_job(module)

            results = dict(
                changed=True,
                msg='The Protection Job for this host has been started',
                id=job_exists,
                name=module.params.get('name')
            )
        else:
            results = dict(
                changed=False,
                msg='The Protection Job for this host is currently not registered',
                name=module.params.get('name'))

    elif module.params.get('state') == 'stopped':
        if job_exists:
            job_id = job_meta_data.uid.id
            response = stop_job(module, job_id)

            results = dict(
                changed=True,
                msg='The Protection Job for this host has been stopped',
                id=job_id,
                name=module.params.get('name')
            )
        else:
            results = dict(
                changed=False,
                msg='The Protection Job for this host is currently not registered',
                name=module.params.get('name'))
    else:
        # => This error should never happen based on the set assigned to the parameter.
        # => However, in case, we should raise an appropriate error.
        module.fail_json(msg='Invalid State selected: {0}'.format(
            module.params.get('state')), changed=False)

    module.exit_json(**results)


if __name__ == '__main__':
    main()
