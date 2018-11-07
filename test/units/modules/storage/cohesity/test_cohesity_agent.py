# Make coding more python3-ish
from __future__ import (absolute_import, division)
__metaclass__ = type

# => Import native Python Modules
import pytest
import json

# # NOTE: Required to find the location of the modules when testing
from sys import path as sys_path
from os import path as os_path
from os import environ


# => Import Ansible Test Modules
# => Due to the following change (https://github.com/ansible/ansible/pull/46996),
# => We will need to provide the following Try..Except validation to provide for
# => Backwards compatibility:
# =>
# => 2018-10-22
try:
    from ansible.compat.tests import unittest
    from ansible.compat.tests.mock import call, create_autospec, patch
except Exception as e:
    # => With this change, we need to include the 'test' directory
    # => in our path
    sys_path.append(os_path.join(environ['PYTHONPATH'], '../test'))
    from units.compat import unittest
    from units.compat.mock import call, create_autospec, patch


from ansible.module_utils.six import StringIO
import ansible.module_utils.six.moves.urllib.error as urllib_error

# => Import Cohesity Modules and Helpers

current_path = sys_path
try:
    # => If we are testing within the role, then we should modify the
    # => path to include this Role (assuming we are at the root.)
    sys_path.append(os_path.realpath('.'))
    from library import cohesity_agent
    # => Set the default Module and ModuleUtility Paths
    global_module_path = 'library'
    global_module_util_path = 'module_utils.storage.cohesity'
except Exception as e:
    # => Reset the correct path Location
    sys_path = current_path
    from ansible.modules.storage.cohesity import cohesity_agent
    # => Set the default Module and ModuleUtility Paths
    global_module_path = 'ansible.modules.storage.cohesity'
    global_module_util_path = 'ansible.module_utils.storage.cohesity'

exit_return_dict = {}


class FakeModule(object):

    def __init__(self, **kwargs):
        self.params = kwargs

    def fail_json(self, *args, **kwargs):
        self.exit_args = args
        self.exit_kwargs = kwargs
        raise Exception('FAIL')

    def exit_json(self, *args, **kwargs):
        self.exit_args = args
        self.exit_kwargs = kwargs


# => Success Test Cases
class TestAgentInstallation(unittest.TestCase):

    def setUp(self):
        self.patchers = dict()

        token_patcher = patch(
            global_module_path + '.cohesity_agent.get__cohesity_auth__token')
        mock_check = token_patcher.start()
        self.patchers.update(token_patcher=token_patcher)
        mock_check.return_value = 'mytoken'

        download_patcher = patch(
            global_module_path + '.cohesity_agent.download_agent')
        mock_check = download_patcher.start()
        self.patchers.update(download_patcher=download_patcher)
        mock_check.return_value = "/tmp/cohesity_agent_installer"

    def tearDown(self):
        for patcher in self.patchers.keys():
            try:
                self.patchers[patcher].stop()
            except Exception as e:
                pass

    def test__download__agent(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password"
        )

        # self.patchers['download_patcher'].stop()

        filename = cohesity_agent.download_agent(module, "/tmp")

        assert filename == "/tmp/cohesity_agent_installer"

    def test__install__agent(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password"
        )

        check_patcher = patch(
            global_module_path + '.cohesity_agent.install_agent')

        mock_check = check_patcher.start()
        mock_check.return_value = True, "Successfully Installed the Cohesity agent"

        filename = "/tmp/cohesity_agent_installer"
        changed, message = cohesity_agent.install_agent(module, filename)

        assert changed is True
        assert message == "Successfully Installed the Cohesity agent"

    def test__remove__agent(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password"
        )

        check_patcher = patch(
            global_module_path + '.cohesity_agent.remove_agent')

        mock_check = check_patcher.start()
        mock_check.return_value = True, "Successfully Removed the Cohesity agent"

        filename = "/tmp/cohesity_agent_installer"
        changed, message = cohesity_agent.remove_agent(module, filename)

        assert changed is True
        assert message == "Successfully Removed the Cohesity agent"
