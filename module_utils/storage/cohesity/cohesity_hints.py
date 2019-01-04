#
# cohesity_hints
#
# Copyright (c) 2018 Cohesity Inc
# Apache License Version 2.0
#


'''
The **CohesityHints** utils module provides standard methods for returning query data
from Cohesity Platforms.
'''

import json
import traceback
from ansible.module_utils.urls import open_url, urllib_error

try:
    # => TODO:  Find a better way to handle this!!!
    # => When unit testing, we need to look in the correct location however, when run via ansible,
    # => the expectation is that the modules will live under ansible.
    from module_utils.storage.cohesity.cohesity_auth import Authentication, TokenException, ParameterViolation
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec
except:
    from ansible.module_utils.storage.cohesity.cohesity_auth import Authentication, TokenException, ParameterViolation
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec


class ParameterViolation(Exception):
    pass


class ProtectionException(Exception):
    pass


class HTTPException(Exception):
    pass


def get__cluster(self):

    try:
        uri = "https://" + self['server'] + \
            "/irisservices/api/v1/public/basicClusterInfo"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + self['token']}
        cluster = open_url(url=uri, headers=headers,
                           validate_certs=self['validate_certs'])
        cluster = json.loads(cluster.read())
    except urllib_error.HTTPError as e:
        try:
            msg = json.loads(e.read())['message']
        except:
            # => For HTTPErrors that return no JSON with a message (bad errors), we
            # => will need to handle this by setting the msg variable to some default.
            msg = "no-json-data"
        else:
            raise HTTPException(e.read())
    return cluster


def get__nodes(self):

    try:
        uri = "https://" + self['server'] + "/irisservices/api/v1/public/nodes"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + self['token']}
        nodes = open_url(url=uri, headers=headers,
                         validate_certs=self['validate_certs'])
        nodes = json.loads(nodes.read())
    except urllib_error.HTTPError as e:
        try:
            msg = json.loads(e.read())['message']
        except:
            # => For HTTPErrors that return no JSON with a message (bad errors), we
            # => will need to handle this by setting the msg variable to some default.
            msg = "no-json-data"
        else:
            raise HTTPException(e.read())
    return nodes


def get__prot_source__all(self):
    try:
        uri = "https://" + self['server'] + \
            "/irisservices/api/v1/public/protectionSources"

        if 'environment' in self:
            uri = uri + "?environments=k" + self['environment']
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + self['token']}
        objects = open_url(url=uri, headers=headers,
                           validate_certs=self['validate_certs'])
        objects = json.loads(objects.read())
        if len(objects):
            objects = objects[0]
        return objects
    except urllib_error.URLError as error:
        raise HTTPException(error.read())


def get__prot_source__roots(self):
    try:
        uri = "https://" + self['server'] + \
            "/irisservices/api/v1/public/protectionSources/rootNodes"

        if 'environment' in self:
            uri = uri + "?environments=k" + self['environment']
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + self['token']}
        objects = open_url(url=uri, headers=headers,
                           validate_certs=self['validate_certs'])
        objects = json.loads(objects.read())
        return objects
    except urllib_error.URLError as error:
        raise HTTPException(error.read())


def get__prot_policy__all(self):
    try:
        uri = "https://" + self['server'] + \
            "/irisservices/api/v1/public/protectionPolicies"

        if 'policyId' in self:
            uri = uri + "?names=" + self['policyId']
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + self['token']}
        objects = open_url(url=uri, headers=headers,
                           validate_certs=self['validate_certs'])
        objects = json.loads(objects.read())
        return objects
    except urllib_error as error:
        raise HTTPException(error.read())


def get__prot_job__all(self):
    try:
        uri = "https://" + self['server'] + \
            "/irisservices/api/v1/public/protectionJobs"
        if 'environment' in self:
            uri = uri + "?environments=k" + self['environment']
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + self['token']}
        objects = open_url(url=uri, headers=headers,
                           validate_certs=self['validate_certs'])
        objects = json.loads(objects.read())

        if 'is_deleted' in self:
            if not self['is_deleted']:
                objects = [objects_item for objects_item in objects if not objects_item.get(
                    'name').startswith('_DELETED_')]
        return objects
    except urllib_error as error:
        raise HTTPException(error.read())


def get__storage_domain_id__all(self):
    try:
        uri = "https://" + self['server'] + \
            "/irisservices/api/v1/public/viewBoxes"
        if 'viewBoxId' in self:
            if 'type' not in self:
                self['type'] = 'name'
                if isinstance(self['viewBoxId'], int):
                    self['type'] = 'id'
            uri = uri + "?" + self['type'] + "=" + self['viewBoxId']

        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + self['token']}
        objects = open_url(url=uri, headers=headers,
                           validate_certs=self['validate_certs'])
        objects = json.loads(objects.read())
        return objects
    except urllib_error.URLError as error:
        raise HTTPException(error.read())


def get__protection_run__all(self):
    try:
        uri = "https://" + self['server'] + \
            "/irisservices/api/v1/public/protectionRuns"

        if 'id' in self:
            uri = uri + "?jobId=" + str(self['id'])
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + self['token']}
        objects = open_url(url=uri, headers=headers,
                           validate_certs=self['validate_certs'])
        objects = json.loads(objects.read())

        if 'is_deleted' in self:
            if not self['is_deleted']:
                objects = [objects_item for objects_item in objects if not objects_item.get(
                    'jobName').startswith('_DELETED_')]

        if 'active_only' in self:
            if self['active_only']:
                objects = [objects_item for objects_item in objects if objects_item[
                    'backupRun'].get('status') == "kAccepted"]
        return objects
    except urllib_error.URLError as error:
        raise HTTPException(error.read())

# => Filtered Queries


def get__prot_source_root_id__by_environment(module, self):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    try:
        source_obj = dict(
            server=server,
            token=token,
            validate_certs=validate_certs,
            environment=self['environment']
        )

        root_nodes = get__prot_source__roots(source_obj)

        for node in root_nodes:
            if node['protectionSource']['environment'] == ("k" + self['environment']):
                return node['protectionSource']['id']

        raise ProtectionException(
            "There was a very serious situation where the chosen environment did not return a valid Root Node ID")
    except Exception as error:
        module.fail_json(msg="Unexpected error caused while managing the Cohesity Protection Source.",
                         exception=traceback.format_exc())


def get__prot_policy_id__by_name(module, self):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    try:
        source_obj = dict(
            server=server,
            token=token,
            validate_certs=validate_certs,
            policyId=self['policyId']
        )
        objects = get__prot_policy__all(source_obj)

        for obj in objects:
            if obj['name'] == self['policyId']:
                return obj['id']

        raise ProtectionException(
            "There was a very serious situation where the chosen Protection Policy Name (" + self['policyId'] + ") did not return a valid ID")
    except Exception as error:
        module.fail_json(msg="Unexpected error caused while managing the Cohesity Protection Source.",
                         exception=traceback.format_exc())


def get__storage_domain_id__by_name(module, self):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    try:
        source_obj = dict(
            server=server,
            token=token,
            validate_certs=validate_certs,
            viewBoxId=self['viewBoxId']
        )
        for obj_type in ['names', 'ids']:
            source_obj['type'] = obj_type
            objects = get__storage_domain_id__all(source_obj)
            if objects:
                break

        for obj in objects:
            if obj['name'] == self['viewBoxId']:
                return int(obj['id'])
            elif obj['id'] == int(self['viewBoxId']):
                return int(obj['id'])
            else:
                # => We really should land here but if so then
                pass

        raise ProtectionException(
            "There was a very serious situation where the chosen Storage Domain Name (" + self['viewBoxId'] + ") did not return a valid ID")
    except Exception as error:
        module.fail_json(msg="Unexpected error caused while managing the Cohesity Protection Source.",
                         exception=traceback.format_exc())


def get__prot_source_id__by_endpoint(module, self):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    try:
        source_obj = dict(
            server=server,
            token=token,
            validate_certs=validate_certs,
            environment=self['environment']
        )
        source = get__prot_source__all(source_obj)
        if source:
            env_types = ['Physical', 'GenericNas']
            if self['environment'] in env_types:
                for node in source['nodes']:
                    if node['protectionSource']['name'] == self['endpoint']:
                        return node['protectionSource']['id']
            else:
                if source['registrationInfo']['accessInfo']['endpoint'] == self['endpoint']:
                    return source['protectionSource']['id']

        return False
    except Exception as error:
        module.fail_json(msg="Unexpected error caused while managing the Cohesity Protection Source.",
                         exception=traceback.format_exc())


def get__protection_jobs__by_environment(module, self):

    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    try:
        source_obj = dict(
            server=server,
            token=token,
            validate_certs=validate_certs,
            environment=self['environment']
        )
        return get__prot_job__all(source_obj)

    except Exception as error:
        module.fail_json(msg="Unexpected error caused while managing the Cohesity Protection Jobs.",
                         exception=traceback.format_exc())


def get__protection_run__all__by_id(module, self):

    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    try:
        source_obj = dict(
            server=server,
            token=token,
            validate_certs=validate_certs,
            id=self['id']
        )
        if 'active_only' in self:
            source_obj['active_only'] = self['active_only']

        if 'is_deleted' in self:
            source_obj['is_deleted'] = self['is_deleted']

        return get__protection_run__all(source_obj)

    except Exception as error:
        module.fail_json(msg="Unexpected error caused while managing the Cohesity Protection Jobs.",
                         exception=traceback.format_exc())
