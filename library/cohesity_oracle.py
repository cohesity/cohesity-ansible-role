#!/usr/bin/python
# Copyright (c) 2018 Cohesity Inc
# Apache License Version 2.0

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import time
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url, urllib_error

try:
    # => When unit testing, we need to look in the correct location however, when run via ansible,
    # => the expectation is that the modules will live under ansible.
    from module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler, REQUEST_TIMEOUT
    from module_utils.storage.cohesity.cohesity_hints import get__prot_source__all
except Exception as e:
    from ansible.module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler, REQUEST_TIMEOUT
    from ansible.module_utils.storage.cohesity.cohesity_hints import get__prot_source__all

DOCUMENTATION = '''
module: cohesity_oracle
short_description: Management of Cohesity Protection Sources
description:
    - Ansible Module used to register or remove the Cohesity Protection Sources to/from a Cohesity Cluster.
    - When executed in a playbook, the Cohesity Protection Source will be validated and the appropriate
    - state action will be applied.
version_added: '2.6.5'
author:
  - Jeremy Goodrum (github.com/exospheredata)
  - Cohesity, Inc

options:
  state:
    description:
      - Determines the state of the Protection Source
    choices:
      - present
      - absent
    default: 'present'
  endpoint:
    description:
      - Specifies the network endpoint of the Protection Source where it is reachable. It could
      - be an URL or hostname or an IP address of the Protection Source.
    required: yes
    aliases:
      - hostname
      - ip_address
  environment:
    description:
      - Specifies the environment type (such as VMware or SQL) of the Protection Source this Job
      - is protecting.
    type: str
    default: Physical
    required: yes
  force_register:
    description:
      - Enabling this option will force the registration of the Cohesity Protection Source.
    type: bool
    default: no

extends_documentation_fragment:
    - cohesity
requirements: []
'''

EXAMPLES = '''
# Register a Physical Cohesity Protection Source on a selected Linux endpoint using Defaults
- cohesity_oracle:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: mylinux.host.lab
    state: present

# Unegister an existing Cohesity Protection Source on a selected endpoint
- cohesity_oracle:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: myvcenter.host.lab
    environment: VMware
    state: absent
'''

RETURN = '''
# Example return from a succesful registration of a Linux Physical Source
{
  "ProtectionSource": {
    "hostType": "kLinux",
    "id": {
      "clusterId": 8621173906188849,
      "clusterIncarnationId": 1538852526333,
      "id": 240
    },
    "name": "10.2.55.72",
    "type": "kHost"
  },
  "changed": true,
  "item": "control",
  "msg": "Registration of Cohesity Protection Source Complete"
}

# Example return from the succesful unregistration of a Protection Source
{
  "changed": true,
  "id": 241,
  "endpoint": "mylinux.host.lab"
  "msg": "Unregistration of Cohesity Protection Source Complete"
}
'''


class ProtectionException(Exception):
    pass

# => Determine if the Endpoint is presently registered to the Cohesity Cluster
# => and if so, then return the Protection Source ID.


def register_oracle_source(module, self, _id):
    """
    Register a physical source as a Oracle source.
    """
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    endpoint = self["endpoint"]
    source_id = _id
    db_user = module.params.get('db_username')
    db_pwd = module.params.get('db_password')

    try:
        uri = "https://" + server + "/irisservices/api/v1/applicationSourceRegistration"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token}
        # Payload to register Oracle source.
        payload = {
          "appEnvVec": [
            19
          ],
          "usesPersistentAgent": True,
          "ownerEntity": {
            "type": 6
          }
        }
        payload["ownerEntity"]["id"] = source_id
        payload["ownerEntity"]["displayName"] = endpoint
        if db_user and db_pwd:
            cred = dict(username=db_user, password=db_pwd)
            payload["appCredentialsVec"] = list() 
            payload["appCredentialsVec"].append(dict(credentials=cred, envType=19))
        data = json.dumps(payload)
        response = open_url(url=uri, data=data, headers=headers,
                            validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)

        response = json.loads(response.read())
        return response
    except Exception as err:
        return payload


def get__protection_source_registration__status(module, self):
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
            if self['environment'] in ["Physical", "Oracle"]:
                for node in source['nodes']:
                    if node['protectionSource']['name'] == self['endpoint']:
                        return node['protectionSource']['id']

        return False
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


# => Register the new Endpoint as a Cohesity Protection Source.
def register_source(module, self):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    try:
        uri = "https://" + server + "/irisservices/api/v1/backupsources"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token}
        #payload = self.copy()
        #payload['environment'] = "k" + self['environment']
        #payload['hostType'] = "k" + self['hostType']
        #payload['physicalType'] = "k" + self['physicalType']
        endpoint = module.params.get('endpoint')
        force_register = module.params.get('force_register')

        # Payload template to register a physical source.
        payload = {
            "entity": {
                "type": 6,
                "physicalEntity": {
                    "name": "",
                    "type": 1,
                    "hostType": 1
                }
            },
            "entityInfo": {
                "endpoint": "",
                "type": 6,
                "hostType": 1
            },
            "sourceSideDedupEnabled": True,
            "throttlingPolicy": {
                "isThrottlingEnabled": False
            },
        }
        payload["forceRegister"] = force_register
        payload["entity"]["physicalEntity"]["name"] = endpoint
        payload["entityInfo"]["endpoint"] = endpoint

        data = json.dumps(payload)
        response = open_url(url=uri, data=data, headers=headers,
                            validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)

        response = json.loads(response.read())

        # => This switcher will allow us to return a standardized output
        # => for all Protection Sources.
        # response = dict(ProtectionSource=response[
        #                     'physicalProtectionSource'])
        return dict(response)
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


# => Unregister an existing Cohesity Protection Source.
def unregister_source(module, self):
    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = self['token']
    try:
        uri = "https://" + server + \
            "/irisservices/api/v1/public/protectionSources/" + str(self['id'])
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token}

        response = open_url(url=uri, method='DELETE', headers=headers,
                            validate_certs=validate_certs, timeout=REQUEST_TIMEOUT)

        return response
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)


def main():
    # => Load the default arguments including those specific to the Cohesity Agent.
    argument_spec = cohesity_common_argument_spec()
    argument_spec.update(
        dict(
            state=dict(choices=['present', 'absent'], default='present'),
            endpoint=dict(type='str', required=True),
            # => Currently, the only supported environments types are list in the choices
            # => For future enhancements, the below list should be consulted.
            # => 'SQL', 'View', 'Puppeteer', 'Pure', 'Netapp', 'HyperV', 'Acropolis', 'Azure'
            environment=dict(default='Physical' ,type='str'),
            force_register=dict(default=False, type='bool'),
            db_username=dict(default='', type='str'),
            db_password=dict(default='', type='str')
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

    # try:
    prot_sources = dict(
        token=get__cohesity_auth__token(module),
        endpoint=module.params.get('endpoint'),
        environment="Physical"
    )
    current_status = get__protection_source_registration__status(
        module, prot_sources)

    if module.check_mode:
        prot_sources["environment"] = "Oracle"
        current_status = get__protection_source_registration__status(
            module, prot_sources)
        check_mode_results = dict(
            changed=False,
            msg="Check Mode: Cohesity Protection Source is not currently registered",
            id="")
        if module.params.get('state') == "present":
            if current_status:
                check_mode_results[
                    'msg'] = "Check Mode: Cohesity Protection Source is currently registered.  No changes"
            else:
                check_mode_results[
                    'msg'] = "Check Mode: Cohesity Protection Source is not currently registered.  This action would register the Protection Source."
                check_mode_results['id'] = current_status
        else:
            if current_status:
                check_mode_results[
                    'msg'] = "Check Mode: Cohesity Protection Source is currently registered.  This action would unregister the Protection Source."
                check_mode_results['id'] = current_status
            else:
                check_mode_results[
                    'msg'] = "Check Mode: Cohesity Protection Source is not currently registered.  No changes."
        module.exit_json(**check_mode_results)

    elif module.params.get('state') == "present":

        if current_status:
            prot_sources = dict(
                token=get__cohesity_auth__token(module),
                endpoint=module.params.get('endpoint'),
                environment="Oracle"
            )
            oracle_status = get__protection_source_registration__status(module, prot_sources)
            if not oracle_status:
                resp = register_oracle_source(module, prot_sources, current_status)
                if resp == True:
                    results = dict(
                        changed=True,
                        msg="Registration of Cohesity Protection Source Complete")
                else:
                    results = dict(
                        changed=False, msg=resp)
                        #msg="Error while registering Cohesity Protection Source")

            else:
                results = dict(
                    changed=False,
                    msg="The Protection Source for this host is already registered",
                    id=current_status,
                    endpoint=module.params.get('endpoint'))
        else:
            sleep_count = 0

            # Register the endpoint as Physical source.
            response = register_source(module, prot_sources)

            # Wait untill Physical source is successfully registered.
            while sleep_count < 5:
                sleep_count += 1
                status = get__protection_source_registration__status(
                    module, dict(environment="Physical", token=prot_sources['token'], endpoint=prot_sources['endpoint']))
                time.sleep(30)

            if status == False:
                module.fail_json(changed=False, msg="Error while registering Cohesity Physical Protection Source")
               
            response = register_oracle_source(module, prot_sources, response["entity"]["id"])
            if response == True:
                results = dict(
                    changed=True,
                    msg="Registration of Cohesity Protection Source Complete"
            )
            else:
                results = dict(
                    changed=False,
                    msg="Error while registering Cohesity Protection Source")

    elif module.params.get('state') == "absent":
        if current_status:
            prot_sources['id'] = current_status

            response = unregister_source(module, prot_sources)

            results = dict(
                changed=True,
                msg="Unregistration of Cohesity Protection Source Complete",
                id=current_status,
                endpoint=module.params.get('endpoint')
            )
        else:
            results = dict(
                changed=False,
                msg="The Protection Source for this host is currently not registered")
    else:
        # => This error should never happen based on the set assigned to the parameter.
        # => However, in case, we should raise an appropriate error.
        module.fail_json(msg="Invalid State selected: {0}".format(
            module.params.get('state')), changed=False)

    # results = dict(changed=True,msg=response)
    module.exit_json(**results)


if __name__ == '__main__':
    main()
