#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'supported_by': 'community',
    'status': ['preview']
}

DOCUMENTATION = '''
module: cohesity_agent
short_description: Installs and Remove the Cohesity Agent.
description:
    - Installation and Management of the Cohesity Agent.
version_added: '2.6.5'
author: 'Jeremy Goodrum (github.com/goodrum)'

extends_documentation_fragment:
    - cohesity
requirements: []
'''

EXAMPLES = '''
# Install the current version of the agent on Linux
- cohesity_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present

# Install the current version of the agent with custom User and Group
- cohesity_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present
    user: cagent
    group: cagent
    create_user: True
'''

RETURN = '''
'''

import os
import shutil
import json
import traceback
from tempfile import mkstemp, mkdtemp
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


class InstallError(Exception):
    pass


def verify_dependencies():
    # => TODO:  Need to add package dependency checks for:
    # => wget, rsync, lsof, nfs-utils, lvm2
    pass


def check_agent(module, results):
    # => Determine if the Cohesity Agent is currently installed
    if not os.path.exists("/etc/init.d/cohesity-agent"):
        # => If the file is not found then let's return False
        # => immediately
        results['version'] = False
        return results

    cmd = "/etc/init.d/cohesity-agent version"
    rc, out, err = module.run_command(cmd)

    version = out.split("\n")[1]
    if version.startswith('Version'):
        # => When the agent is installed, we should be able to return
        # => the version information
        results['version'] = version
    else:
        # => If this didn't return a Version, then we have bigger problems
        # => and probably should try to re-install or force the uninstall.
        results['version'] = "unknown"
        results['check_agent'] = dict(
            stdout=out,
            stderr=err
        )
    return results


def download_agent(module, path):

    os_type = "Linux"

    server = module.params.get('server')
    validate_certs = module.params.get('validate_certs')
    auth = Authentication()
    auth.username = module.params.get('username')
    auth.password = module.params.get('password')
    ####

    # TODO:  Add Domain Information

    ####
    token = auth.get_token(server)

    try:
        uri = "https://" + server + \
            "/irisservices/api/v1/public/physicalAgents/download?hostType=k" + os_type
        headers = {
            "Accept": "application/octet-stream",
            "Authorization": "Bearer " + token}
        agent = open_url(url=uri, headers=headers,
                         validate_certs=validate_certs)
        resp_headers = agent.info().dict
        filename = resp_headers['content-disposition'].split("=")[1]
        filename = path + "/" + filename
        try:
            f = open(filename, "w")
            f.write(agent.read())
            os.chmod(filename, 0o755)
        except Exception as e:
            raise InstallError(e)
        finally:
            f.close()
    except urllib_error.HTTPError as e:
        try:
            msg = json.loads(e.read())['message']
        except:
            # => For HTTPErrors that return no JSON with a message (bad errors), we
            # => will need to handle this by setting the msg variable to some default.
            msg = "no-json-data"
        else:
            raise InstallError(e)
    return filename


def installation_failures(module, stdout, message):
    # => The way that this installer works, we will not get back messages in stderr
    # => when a failure occurs.  For this reason, we need to jump through some hoops
    # => to extract the error messages.  The install will *Partially* complete even
    # => if certain dependencies are missing.
    # =>
    # => This block of code will first split the stdout into a List of strings that
    # => we will filter for any line which contains *Error:*.  Those lines will be
    # => returned to a new list *stderr* which will be formatted into a \n delimited
    # => string as the final step, we will raise a module failure to halt progress.
    stdout_lines = stdout.split("\n")
    stderr = [k for k in stdout_lines if 'Error:' in k]
    stderr = "\n".join(stderr)
    module.fail_json(changed=False, msg=message, error=stderr)


def install_agent(module, filename):

    # => This command will run the self-extracting installer for the agent on machine and
    # => suppress opening a new window (nox11) and not show the extraction (noprogress) results
    # => which end up in stderr.
    #
    # => Note: Python 2.6 doesn't fully support the new string formatters, so this
    # => try..except will give us a clean backwards compatibility.
    try:
        cmd = "{} --nox11 --noprogress -- --install --yes".format(filename)
    except:
        cmd = "%s --nox11 --noprogress -- --install --yes" % filename

    rc, stdout, stderr = module.run_command(cmd)

    # => Any return code other than 0 is considered a failure.
    if rc:
        installation_failures(
            module, stdout, "Cohesity Agent is partially installed")
    return (True, "Successfully Installed the Cohesity agent")


def remove_agent(module, filename):

    # => This command will run the self-extracting installer for the agent on machine and
    # => suppress opening a new window (nox11) and not show the extraction (noprogress) results
    # => which end up in stderr.
    #
    # => Note: Python 2.6 doesn't fully support the new string formatters, so this
    # => try..except will give us a clean backwards compatibility.
    try:
        cmd = "{} --nox11 --noprogress -- --full-uninstall --yes".format(
            filename)
    except:
        cmd = "%s --nox11 --noprogress -- --full-uninstall --yes" % filename
    rc, out, err = module.run_command(cmd)

    # => Any return code other than 0 is considered a failure.
    if rc:
        installation_failures(
            module, stdout, "Cohesity Agent is partially installed")
    return (True, "Successfully Removed the Cohesity agent")


def main():
    # => Load the default arguments including those specific to the Cohesity Agent.
    argument_spec = cohesity_common_argument_spec()
    argument_spec.update(
        dict(
            state=dict(choices=['present', 'absent'], default='present'),
            user=dict(default='cohesityagent', aliases=['service_user']),
            group=dict(default='cohesityagent', aliases=['service_group']),
            create_user=dict(default=True, type='bool')
        )
    )

    # => Create a new module object
    module = AnsibleModule(argument_spec=argument_spec)
    results = dict(
        changed=False,
        version=False,
        state=module.params.get('state')
    )

    # => Make a temporary directory to house the downloaded installer.
    tempdir = mkdtemp(
        prefix="ansible."
    )
    success = True
    try:
        if module.params.get('state') == "present":
            # => Check if the Cohesity Agent is currently installed and only trigger the install
            # => if the agent does not exist.
            results = check_agent(module, results)
            if not results['version']:
                results['filename'] = download_agent(module, tempdir)
                results['changed'], results['message'] = install_agent(
                    module, results['filename'])
                results = check_agent(module, results)
            elif results['version'] == "unknown":
                # => There is a problem that we should invesitgate.
                module.fail_json(
                    msg="Cohesity Agent is partially installed", **results)
            else:
                pass
        elif module.params.get('state') == "absent":
            # => Check if the Cohesity Agent is currently installed and only trigger the uninstall
            # => if the agent exists.
            results = check_agent(module, results)

            # => If anything is returned, we should remove the agent.  We also don't care if there
            # => is any output from the check so we will pop that out of the results to clean up
            # => our return data.
            if results['version']:
                results.pop('check_agent', None)
                # => When removing the agent, we will need to download the installer once again,
                # => and then run the --full-uninstall command.
                results['filename'] = download_agent(module, tempdir)
                results['changed'], results['message'] = remove_agent(
                    module, results['filename'])
        else:
            # => This error should never happen based on the set assigned to the parameter.
            # => However, in case, we should raise an appropriate error.
            raise "Invalid State selected: {}".format(
                module.params.get('state'))
    except Exception as error:
        module.fail_json(msg="Unexpected error caused while managing the Cohesity Agent.",
                         exception=traceback.format_exc())
    finally:
        # => We should delete the downloaded installer regardless of our success.  This could be debated
        # => either way but seems like a better choice.
        shutil.rmtree(tempdir)

    if success:
        # -> Return Ansible JSON
        module.exit_json(**results)
    else:
        module.fail_json(msg="Cohesity Agent Failed", **results)


if __name__ == '__main__':
    main()
