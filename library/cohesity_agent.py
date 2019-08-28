#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# Apache License Version 2.0

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
except Exception as e:
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
      - This user must be an existing user for native installation.
    default: 'cohesityagent' for script based installation
  service_group:
    description:
      - Group underwhich permissions will be configured for the Cohesity Agent configuration.
      - This group must exist unless I(create_user=True) is also configured.
      - This parameter doesn't apply for native installation
    default: 'cohesityagent' for script based installation
  create_user:
    description:
      - When enabled, will create a new user and group based on the values of I(service_user) and I(service_group)
      - This parameter does not apply for native installations
    type: bool
    default: True
  file_based:
    description:
      - When enabled, will install the agent in non-LVM mode and support only file based backups
    type: bool
    default: False
  native_package:
    description:
      - When enabled, native installer packages are used based on the operating system
    type: bool
    default: False
  download_uri:
    description:
      - The download uri from where the installer can be downloaded
    default: ''
  operating_system:
    description:
      - ansible_distribution from facts, this value is automatically populated. Not given by module user
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

# Install the current version of the agent on Linux using native installers, the service user here should be an
# existing user
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    state: present
    service_user: cagent
    native_package: True

# Install the cohesity agent using native package downloaded from given URI. Here, the Cohesity cluster credentials are not required
- cohesity_agent:
    state: present
    service_user: cagent
    native_package: True
    download_uri: 'http://10.2.145.47/files/bin/installers/el-cohesity-agent-6.3-1.x86_64.rpm'

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
    if os.path.exists("/etc/init.d/cohesity-agent"):
        cmd = "/etc/init.d/cohesity-agent version"
        rc, out, err = module.run_command(cmd)
        split_out = out.split("\n")
        version = ""
        for v in split_out:
            if v.startswith('Version'):
                version = v.split(" ")[-1]
                break
        if version:
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
    elif os.path.exists("/etc/cohesity-agent"):
        # => If the file is found then let's return an unknown state
        # => immediately
        results['version'] = "unknown"
        return results
    else:
        cmd = "ps -aux | grep crux/bin/linux_agent | grep -v python | awk '{print $2}'"
        rc, out, err = module.run_command(
            cmd, check_rc=True, use_unsafe_shell=True)
        if out:
            orphaned_agents = out.split("\n")
            for process in orphaned_agents:
                if process:
                    try:
                        cmd = "kill -9 {0}".format(process)
                    except BaseException:
                        cmd = "kill -9 %s" % (process)
                    rc, out, err = module.run_command(cmd)

                    if err:
                        pattern = "No such process"
                        if pattern in err:
                            # => Since the kill command returned 'No such process' we will just continue
                            pass
                        else:
                            results['changed'] = False
                            results['Failed'] = True
                            results['check_agent'] = dict(
                                stdout=out,
                                stderr=err
                            )
                            results['process_id'] = process
                            module.fail_json(
                                msg="Failed to remove an orphaned Cohesity Agent service which is still running",
                                **results)
                    else:
                        pass
            results['version'] = False
            return results

        else:
            # => If the files are not found then let's return False
            # => immediately
            results['version'] = False
            return results


def download_agent(module, path):
    try:
        if not module.params.get('download_uri'):
            os_type = "Linux"
            server = module.params.get('cluster')
            token = get__cohesity_auth__token(module)
            package_type = 'kScript'
            if module.params.get('native_package'):
                if module.params.get('operating_system') in ('CentOS', 'RedHat'):
                    package_type = 'kRPM'
                elif module.params.get('operating_system') == 'SLES':
                    package_type = 'kSuseRPM'
                elif module.params.get('operating_system') == 'Ubuntu':
                    package_type = 'kDEB'
            uri = "https://" + server + \
                "/irisservices/api/v1/public/physicalAgents/download?hostType=k" + os_type + '&pkgType=' + package_type
            headers = {
                "Accept": "application/octet-stream",
                "Authorization": "Bearer " + token}
        else:
            uri = module.params.get('download_uri')
            headers = {
                "Accept": "application/octet-stream"}

        agent = open_url(url=uri, headers=headers,
                         validate_certs=False, timeout=120)
        resp_headers = agent.info().dict
        if 'content-disposition' in resp_headers.keys():
            filename = resp_headers['content-disposition'].split("=")[1]
        else:
            filename = 'cohesity-agent-installer'
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
                msg="Failed to download the Cohesity Agent",
                reason=error_msg['message'])
        else:
            raise__cohesity_exception__handler(e, module)
    except urllib_error.URLError as e:
        # => Capture and report any error messages.
        raise__cohesity_exception__handler(e.read(), module)
    except Exception as error:
        raise__cohesity_exception__handler(error, module)
    return filename


def installation_failures(module, stdout, rc, message):
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

    # => Grab any Line that begins with Error:
    stderr = [k for k in stdout_lines if 'Error:' in k]
    stderr = "\n".join(stderr)

    # => Grab any Line that begins with WARNING:
    stdwarn = [k for k in stdout_lines if 'WARNING:' in k]
    stdwarn = "\n".join(stdwarn)
    module.fail_json(
        changed=False,
        msg=message,
        error=stderr,
        output=stdout,
        warn=stdwarn,
        exitcode=rc)


def install_agent(module, installer, native):

    # => This command will run the self-extracting installer for the agent on machine and
    # => suppress opening a new window (nox11) and not show the extraction (noprogress) results
    # => which end up in stderr.
    #
    # => Note: Python 2.6 doesn't fully support the new string formatters, so this
    # => try..except will give us a clean backwards compatibility.
    if not native:
        install_opts = "--create-user " + \
            str(int(module.params.get('create_user'))) + " "
        if module.params.get('service_user'):
            install_opts += "--service-user " + \
                module.params.get('service_user') + " "
        if module.params.get('service_group'):
            install_opts += "--service-group " + \
                module.params.get('service_group') + " "
        if module.params.get('file_based'):
            install_opts += "--skip-lvm-check "
        try:
            cmd = "{0}/setup.sh --install --yes {1}".format(
                installer, install_opts)
        except Exception as e:
            cmd = "%s/setup.sh --install --yes %s" % (installer, install_opts)
    else:
        try:
            if module.params.get('service_user'):
                user = module.params.get('service_user')
            if module.params.get('operating_system') == "Ubuntu":
                cmd = "sudo COHESITYUSER={0} dpkg -i {1}".format(user, installer)
            elif module.params.get('operating_system') in ("CentOS", "RedHat"):
                cmd = "sudo COHESITYUSER={0} rpm -i {1}".format(user, installer)
            else:
                installation_failures(
                    module, "", "",
                    str(module.params.get('operating_system')) + " isn't supported by cohesity ansible module")
        except Exception as e:
            if module.params.get('operating_system') == "Ubuntu":
                cmd = "sudo COHESITYUSER=%s dpkg -i %s" % (user, installer)
            elif module.params.get('operating_system') in ("CentOS", "RedHat"):
                cmd = "sudo COHESITYUSER=%s  rpm -i %s" % (user, installer)

    rc, stdout, stderr = module.run_command(cmd, cwd=installer)
    # => Any return code other than 0 is considered a failure.
    if rc:
        installation_failures(
            module, stdout, rc, "Cohesity Agent is partially installed")
    return (True, "Successfully Installed the Cohesity agent")


def extract_agent(module, filename):

    # => This command will run the self-extracting installer in no execution mode
    #
    # => Note: Python 2.6 doesn't fully support the new string formatters, so this
    # => try..except will give us a clean backwards compatibility.
    import os
    directory = os.path.dirname(os.path.abspath(filename))
    target = directory + "/install_files"
    create_download_dir(module, target)
    try:
        cmd = "{0} --nox11 --noexec --target {1} ".format(filename, target)
    except Exception as e:
        cmd = "%s --nox11 --noexec --target %s " % (filename, target)

    rc, stdout, stderr = module.run_command(cmd)

    # => Any return code other than 0 is considered a failure.
    if rc:
        installation_failures(
            module, stdout, rc, "Cohesity Agent is partially installed")
    return (True, "Successfully Installed the Cohesity agent", target)


def remove_agent(module, installer, native):

    # => This command will run the self-extracting installer for the agent on machine and
    # => suppress opening a new window (nox11) and not show the extraction (noprogress) results
    # => which end up in stderr.
    #
    # => Note: Python 2.6 doesn't fully support the new string formatters, so this
    # => try..except will give us a clean backwards compatibility.
    if not native:
        try:
            cmd = "{0}/setup.sh --full-uninstall --yes".format(installer)
        except Exception as e:
            cmd = "%s/setup.sh --full-uninstall --yes" % (installer)
        rc, out, err = module.run_command(cmd, cwd=installer)

        # => Any return code other than 0 is considered a failure.
        if rc:
            installation_failures(
                module, out, rc, "Cohesity Agent is partially installed")
    else:
        if module.params.get('operating_system') == "Ubuntu":
            cmd = "sudo dpkg -P cohesity-agent"
            rc, stdout, stderr = module.run_command(cmd)
            if rc:
                installation_failures(
                    module, stdout, rc, "Failed to uninstall cohesity agent ")
        elif module.params.get('operating_system') in ("CentOS", "RedHat"):
            cmd = "sudo rpm -e cohesity-agent"
            rc, stdout, stderr = module.run_command(cmd)
            if rc:
                installation_failures(
                    module, stdout, rc, "Failed to uninstall cohesity agent")
            cmd = "sudo rm -rf /etc/cohesity-agent"
            rc, stdout, stderr = module.run_command(cmd)
            if rc:
                installation_failures(
                    module, stdout, rc, "The cohesity agent is uninstalled but failed to remove /etc/cohesity-agent")
        else:
            installation_failures(
                module, "", "",
                str(module.params.get('operating_system')) + " is not supported by cohesity ansible module")

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
                # check above. As long as it's a dir, we don't need to error
                # out.
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
            create_user=dict(default=True, type='bool'),
            file_based=dict(default=False, type='bool'),
            native_package=dict(default=False, type='bool'),
            download_uri=dict(),
            operating_system=dict(defalut="", type='str')
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
                if not module.params.get('native_package'):
                    results['filename'] = download_agent(module, tempdir)
                    results['changed'], results['message'], results['installer'] = extract_agent(
                        module, results['filename'])
                    results['changed'], results['message'] = install_agent(
                        module, results['installer'], False)
                    results = check_agent(module, results)
                else:
                    results['filename'] = download_agent(module, tempdir)
                    results['changed'], results['message'] = install_agent(module, results['filename'], True)
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
                if not module.params.get('native_package'):
                    results.pop('check_agent', None)
                    # => When removing the agent, we will need to download the installer once again,
                    # => and then run the --full-uninstall command.
                    results['filename'] = download_agent(module, tempdir)
                    results['changed'], results['message'], results['installer'] = extract_agent(
                        module, results['filename'])
                    results['changed'], results['message'] = remove_agent(
                        module, results['installer'], False)
                else:
                    results['changed'], results['message'] = remove_agent(module, "", True)
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
            if 'installer' in results:
                shutil.rmtree(results['installer'])
        else:
            shutil.rmtree(tempdir)

    if success:
        # -> Return Ansible JSON
        module.exit_json(**results)
    else:
        module.fail_json(msg="Cohesity Agent Failed", **results)


if __name__ == '__main__':
    main()
