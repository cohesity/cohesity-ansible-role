#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import shutil
import json
from tempfile import mkstemp, mkdtemp
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url, urllib_error
from ansible.module_utils._text import to_bytes, to_native

try:
    # => When unit testing, we need to look in the correct location however, when run via ansible,
    # => the expectation is that the modules will live under ansible.
    from module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler
except:
    from ansible.module_utils.storage.cohesity.cohesity_auth import get__cohesity_auth__token
    from ansible.module_utils.storage.cohesity.cohesity_utilities import cohesity_common_argument_spec, raise__cohesity_exception__handler


ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'supported_by': 'community',
    'status': ['preview']
}

DOCUMENTATION = '''
module: cohesity_agent
short_description: Management of Cohesity Physical Agent
description:
    - Ansible Module used to deploy or remove the Cohesity Physical Agent from supported Linux Machines.
    - When executed in a playbook, the Cohesity Agent installation will be validated and the appropriate
    - state action will be applied.  The most recent version of the Cohesity Agent will be automatically
    - downloaded to the host.
version_added: '2.6.5'
author:
  - Jeremy Goodrum (github.com/exospheredata)
  - Cohesity, Inc

options:
  state:
    description:
      - Determines if the agent should be C(present) or C(absent) from the host
    choices:
      - present
      - absent
    default: 'present'
  download_location:
    description:
      - Optional directory path to which the installer will be downloaded.  If not selected, then a temporary
      - directory will be created in the default System Temp Directory.  When choosing an alternate directory,
      - the directory and installer will not be deleted at the end of the execution.
  service_user:
    description:
      - Username underwhich the Cohesity Agent will be installed and run.
      - This user must exist unless I(create_user=True) is also configured.
    default: 'cohesityagent'
  service_group:
    description:
      - Group underwhich permissions will be configured for the Cohesity Agent configuration.
      - This group must exist unless I(create_user=True) is also configured.
    default: 'cohesityagent'
  create_user:
    description:
      - When enabled, will create a new user and group based on the values of I(service_user) and I(service_group)
    type: bool
    default: True

extends_documentation_fragment:
    - cohesity
requirements: []
'''

EXAMPLES = '''
# Install the current version of the agent on Linux
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    state: present

# Install the current version of the agent with custom User and Group
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    state: present
    service_user: cagent
    service_group: cagent
    create_user: True

# Removes the current installed agent from the host
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    state: absent

# Download the agent installer to a custom location.
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    download_location: /software/installers
    state: present
'''

RETURN = '''
'''


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

    server = module.params.get('cluster')
    validate_certs = module.params.get('validate_certs')
    token = get__cohesity_auth__token(module)

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
        error_msg = json.loads(e.read())
        if 'message' in error_msg:
            module.fail_json(
                msg="Failed to download the Cohesity Agent", reason=error_msg['message'])
        else:
            raise__cohesity_exception__handler(e, module)
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)

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
        cmd = "{0} --nox11 --noprogress -- --install --yes".format(filename)
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
        cmd = "{0} --nox11 --noprogress -- --full-uninstall --yes".format(
            filename)
    except:
        cmd = "%s --nox11 --noprogress -- --full-uninstall --yes" % filename
    rc, out, err = module.run_command(cmd)

    # => Any return code other than 0 is considered a failure.
    if rc:
        installation_failures(
            module, out, "Cohesity Agent is partially installed")
    return (True, "Successfully Removed the Cohesity agent")

def create_download_dir(module, dir_path):
    # => Note: 2018-12-06
    # => Added this method to provide an alternate parameter to download the installer.
    # => This code was almost entirely pulled out of the Ansible File module.
    curpath = ''
    # => Determine if the download directory exists and if not then create it.
    for dirname in dir_path.strip('/').split('/'):
        curpath = '/'.join([curpath, dirname])
        # Remove leading slash if we're creating a relative path
        if not os.path.isabs(dir_path):
            curpath = curpath.lstrip('/')
        b_curpath = to_bytes(curpath, errors='surrogate_or_strict')
        if not os.path.exists(b_curpath):
            try:
                os.mkdir(b_curpath)
            except OSError as ex:
                import errno
                # Possibly something else created the dir since the os.path.exists
                # check above. As long as it's a dir, we don't need to error out.
                if not (ex.errno == errno.EEXIST and os.path.isdir(b_curpath)):
                    raise


def main():
    # => Load the default arguments including those specific to the Cohesity Agent.
    argument_spec = cohesity_common_argument_spec()
    argument_spec.update(
        dict(
            state=dict(choices=['present', 'absent'], default='present'),
            download_location=dict(),
            service_user=dict(default='cohesityagent'),
            service_group=dict(default='cohesityagent'),
            create_user=dict(default=True, type='bool')
        )
    )

    # => Create a new module object
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    results = dict(
        changed=False,
        version=False,
        state=module.params.get('state')
    )

    # => Make a temporary directory to house the downloaded installer.
    if module.params.get('download_location'):
        tempdir = module.params.get('download_location')
        create_download_dir(module, tempdir)
    else:
        tempdir = mkdtemp(
            prefix="ansible."
        )
    success = True
    try:
        if module.check_mode:
            results = check_agent(module, results)
            check_mode_results = dict(
                changed=False,
                msg="Check Mode: Agent is Currently not Installed",
                version=""
            )
            if module.params.get('state') == "present":
                if results['version']:
                    check_mode_results[
                        'msg'] = "Check Mode: Agent is currently installed.  No changes"
                else:
                    check_mode_results[
                        'msg'] = "Check Mode: Agent is currently not installed.  This action would install the Agent."
                    check_mode_results['version'] = results['version']
            else:
                if results['version']:
                    check_mode_results[
                        'msg'] = "Check Mode: Agent is currently installed.  This action would uninstall the Agent."
                    check_mode_results['version'] = results['version']
                else:
                    check_mode_results[
                        'msg'] = "Check Mode: Agent is currently not installed.  No changes."
            module.exit_json(**check_mode_results)

        elif module.params.get('state') == "present":
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
                # => If we received a valid version then the assumption will be
                # => that the Agent is installed.  We should simply pass it foward
                # => and act like things are normal.
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
            module.fail_json(msg="Invalid State selected: {0}".format(
                module.params.get('state')), changed=False)
    except Exception as error:
        # => The exception handler should still trigger but just in case, let's set this
        # => variable 'success' to be False.
        success = False

        # => Call the proper error handler.
        msg = "Unexpected error caused while managing the Cohesity Linux Agent."
        raise__cohesity_exception__handler(error, module, msg)

    finally:
        # => We should delete the downloaded installer regardless of our success.  This could be debated
        # => either way but seems like a better choice.
        if module.params.get('download_location'):
            pass
        else:
            shutil.rmtree(tempdir)

    if success:
        # -> Return Ansible JSON
        module.exit_json(**results)
    else:
        module.fail_json(msg="Cohesity Agent Failed", **results)


if __name__ == '__main__':
    main()
