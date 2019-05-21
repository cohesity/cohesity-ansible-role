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
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler
    from module_utils.storage.cohesity.cohesity_hints import get__prot_source__all
except Exception as e:
    from ansible.module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler
    from ansible.module_utils.storage.cohesity.cohesity_hints import get__prot_source__all

DOCUMENTATION = '''
module: cohesity_source
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
      - be an URL or hostname or an IP address of the Protection Source or a NAS Share/Export Path.
    required: yes
    aliases:
      - hostname
      - ip_address
  environment:
    description:
      - Specifies the environment type (such as VMware or SQL) of the Protection Source this Job
      - is protecting. Supported environment types include 'Physical', 'VMware', 'GenericNas'
    choices:
      - VMware
      - Physical
      - GenericNas
    required: yes
  host_type:
    description:
      - Specifies the optional OS type of the Protection Source (such as C(Windows) or C(Linux)).
      - C(Linux) indicates the Linux operating system.
      - C(Windows) indicates the Microsoft Windows operating system.
      - C(Aix) indicates the IBM AIX operating system.
      - Optional when I(state=present) and I(environment=Physical).
    choices:
      - Linux
      - Windows
      - Aix
    default:
      - Linux
  physical_type:
    description:
      - Specifies the entity type such as C(Host) if the I(environment=Physical).
      - C(Host) indicates a single physical server.
      - C(WindowsCluster) indicates a Microsoft Windows cluster.
      - Optional when I(state=present) and I(environment=Physical).
    choices:
      - Host
      - WindowsCluster
    default:
      - Host
  force_register:
    description:
      - Enabling this option will force the registration of the Cohesity Protection Source.
    type: bool
    default: no
  vmware_type:
    description:
      - Specifies the entity type such as C(VCenter) if the environment is C(VMware).
    choices:
      - VCenter
      - Folder
      - Datacenter
      - ComputeResource
      - ClusterComputeResource
      - ResourcePool
      - Datastore
      - HostSystem
      - VirtualMachine
      - VirtualApp
      - StandaloneHost
      - StoragePod
      - Network
      - DistributedVirtualPortgroup
      - TagCategory
      - Tag
    default: 'VCenter'
  source_username:
    description:
      - Specifies username to access the target source.
      - Required when I(state=present) and I(environment=VMware)
  source_password:
    description:
      - Specifies the password to access the target source.
      - This parameter will not be logged.
      - Required when I(state=present) and I(environment=VMware)
  nas_protocol:
    description:
      - Specifies the type of connection for the NAS Mountpoint.
      - SMB Share paths must be in \\\\server\\share format.
      - Required when I(state=present) and I(environment=GenericNas)
    choices:
      - NFS
      - SMB
    default: 'NFS'
  nas_username:
    description:
      - Specifies username to access the target NAS Environment.
      - Supported Format is Username or Domain\\Username
      - Required when I(state=present) and I(environment=GenericNas) and I(nas_protocol=SMB)
  nas_password:
    description:
      - Specifies the password to accessthe target NAS Environment.
      - This parameter will not be logged.
      - Required when I(state=present) and I(environment=GenericNas) and I(nas_protocol=SMB)

extends_documentation_fragment:
    - cohesity
requirements: []
'''

EXAMPLES = '''
# Register a Physical Cohesity Protection Source on a selected Linux endpoint using Defaults
- cohesity_source:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: mylinux.host.lab
    state: present

# Register a Physical Cohesity Protection Source on a selected Windows endpoint
- cohesity_source:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: mywindows.host.lab
    environment: Physical
    host_type: Windows
    state: present

# Register a VMware Cohesity Protection Source on a selected endpoint
- cohesity_source:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: myvcenter.host.lab
    environment: VMware
    source_username: admin@vcenter.local
    source_password: vmware
    vmware_type: Vcenter
    state: present

# Register a NAS Cohesity Protection Source on a selected NFS mountpoint
- cohesity_source:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: mynfs.host.lab:/exports
    environment: GenericNas
    state: present

# Register a NAS Cohesity Protection Source on a selected SMB share
- cohesity_source:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: \\\\myfileserver.host.lab\\data
    environment: GenericNas
    nas_protocol: SMB
    nas_username: administrator
    nas_password: password
    state: present

# Unegister an existing Cohesity Protection Source on a selected endpoint
- cohesity_source:
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

# Example return from a succesful registration of a VMware Source
{
  "ProtectionSource": {
    "id": {
      "uuid": "ebd9bfce-b845-4aa3-842a-3f0dc381bbab"
    },
    "name": "vc-67.eco.eng.cohesity.com",
    "type": "kVCenter"
  },
  "changed": true,
  "msg": "Registration of Cohesity Protection Source Complete"
}

# Example return from a succesful registration of a GenericNas Source
{
  "ProtectionSource ": {
    "environment ": "kGenericNas ",
    "id": 396,
    "name ": "10.2.145.19:/export_path",
    "path": "10.2.145.19:/export_path",
    "protocol ": "NFS"
  }
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


def check__mandatory__params(module):
    # => This method will perform validations of optionally mandatory parameters
    # => required for specific states and environments.
    success = True
    missing_params = list()
    environment = module.params.get('environment')
    nas_protocol = module.params.get('nas_protocol')

    if module.params.get('state') == 'present':
        action = 'creation'
        # module.fail_json(**module.params)
        if environment == "GenericNas" and nas_protocol == "SMB":
            if not module.params.get('nas_username'):
                success = False
                missing_params.append('nas_username')
            if not module.params.get('nas_password'):
                success = False
                missing_params.append('nas_password')

    else:
        action = 'remove'

    if not success:
        module.fail_json(
            msg="The following variables are mandatory for this action (" +
            action +
            ") when working with environment type (" +
            environment +
            ")",
            missing=missing_params,
            changed=False)


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
            env_types = ['Physical', 'GenericNas']
            if self['environment'] in env_types:
                for node in source['nodes']:
                    if node['protectionSource']['name'] == self['endpoint']:
                        return node['protectionSource']['id']
            else:
                for node in source:
                    if node['registrationInfo']['accessInfo']['endpoint'] == self['endpoint']:
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
        uri = "https://" + server + "/irisservices/api/v1/public/protectionSources/register"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token}
        payload = self.copy()

        payload['environment'] = "k" + self['environment']
        if self['environment'] == "Physical":
            payload['hostType'] = "k" + self['hostType']
            payload['physicalType'] = "k" + self['physicalType']
        elif self['environment'] == "VMware":
            payload['vmwareType'] = "k" + self['vmwareType']
        elif self['environment'] == "GenericNas":
            # => 2018-10-26
            # => As of this point, the GenericNas integration into the
            # => the public API is not complete so we will need to call
            # => the backupsources API instead and construct the Go model
            # => required to create the Source.
            uri = "https://" + server + "/irisservices/api/v1/backupsources"
            environment_type = 11  # kGenericNas
            protocol = 1  # 1=kNfs3 and 2=kCifs1
            entity_type = 1  # 1=kHost

            payload = dict(
                entity=dict(
                    type=environment_type,
                    genericNasEntity=dict(
                        protocol=protocol,
                        type=entity_type,
                        path=self['endpoint']
                    )
                ),
                entityInfo=dict(
                    endpoint=self['endpoint'],
                    type=environment_type
                )
            )
            if self['nas_protocol'] == "SMB":
                payload['entity']['genericNasEntity']['protocol'] = 2

                if "\\" in self['nas_username']:
                    user_details = self['nas_username'].split("\\")
                    self['nas_username'] = user_details[1]
                    domain_name = user_details[0]
                else:
                    domain_name = "."

                cred_obj = dict(
                    username=self['nas_username'],
                    password=self['nas_password'],
                    nasMountCredentials=dict(
                        protocol=2,
                        username=self['nas_username'],
                        password=self['nas_password'],
                        domainName=domain_name
                    )
                )
                payload['entityInfo']['credentials'] = cred_obj

        else:
            pass

        data = json.dumps(payload)
        response = open_url(url=uri, data=data, headers=headers,
                            validate_certs=validate_certs)

        response = json.loads(response.read())

        # => This switcher will allow us to return a standardized output
        # => for all Protection Sources.
        if self['environment'] == 'Physical':
            response = dict(ProtectionSource=response[
                            'physicalProtectionSource'])
        elif self['environment'] == 'VMware':
            response = dict(ProtectionSource=response[
                            'vmWareProtectionSource'])
        elif self['environment'] == 'GenericNas':
            # => 2018-10-26
            # => Because of the current limitations on the public API
            # => we will need to construct our own output to standardize
            # => information similar to what we would see from the public
            # => API.
            entity = response['entity']
            response_output = dict(
                id=entity['id'],
                environment="kGenericNas",
                name=entity['displayName'],
                protocol=self['nas_protocol'],
                path=entity['genericNasEntity']['path']
            )
            response = dict(ProtectionSource=response_output)

        return response
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
            "/irisservices/api/v1/backupsources/" + str(self['id'])
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + token}

        response = open_url(url=uri, method='DELETE', headers=headers,
                            validate_certs=validate_certs)

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
            environment=dict(
                choices=['VMware', 'Physical', 'GenericNas'],
                required=True
            ),
            host_type=dict(choices=['Linux', 'Windows',
                                    'Aix'], default='Linux'),
            physical_type=dict(
                choices=['Host', 'WindowsCluster'], default='Host'),
            force_register=dict(default=False, type='bool'),
            vmware_type=dict(choices=[
                'VCenter', 'Folder', 'Datacenter', 'ComputeResource', 'ClusterComputeResource', 'ResourcePool',
                'Datastore', 'HostSystem', 'VirtualMachine', 'VirtualApp', 'StandaloneHost', 'StoragePod',
                'Network', 'DistributedVirtualPortgroup', 'TagCategory', 'Tag'
            ],
                default='VCenter'
            ),
            source_username=dict(type='str'),
            source_password=dict(type='str', no_log=True),
            nas_protocol=dict(choices=['NFS', 'SMB'], default='NFS'),
            nas_username=dict(type='str'),
            nas_password=dict(type='str', no_log=True)
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
        environment=module.params.get('environment')
    )
    current_status = get__protection_source_registration__status(
        module, prot_sources)
    if module.check_mode:
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
        check__mandatory__params(module)
        if prot_sources['environment'] == "Physical":
            prot_sources['hostType'] = module.params.get('host_type')
            prot_sources['physicalType'] = module.params.get(
                'physical_type')
        if prot_sources['environment'] == "VMware":
            prot_sources['username'] = module.params.get('source_username')
            prot_sources['password'] = module.params.get('source_password')
            prot_sources['vmwareType'] = module.params.get('vmware_type')
        if prot_sources['environment'] == "GenericNas":
            prot_sources['nas_protocol'] = module.params.get(
                'nas_protocol')
            prot_sources['nas_username'] = module.params.get(
                'nas_username')
            prot_sources['nas_password'] = module.params.get(
                'nas_password')

        prot_sources['forceRegister'] = module.params.get('force_register')

        results['changed'] = True
        results['source_vars'] = prot_sources

        if current_status:
            results = dict(
                changed=False,
                msg="The Protection Source for this host is already registered",
                id=current_status,
                endpoint=module.params.get('endpoint'))
        else:

            response = register_source(module, prot_sources)

            results = dict(
                changed=True,
                msg="Registration of Cohesity Protection Source Complete",
                **response
            )

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

    module.exit_json(**results)


if __name__ == '__main__':
    main()
