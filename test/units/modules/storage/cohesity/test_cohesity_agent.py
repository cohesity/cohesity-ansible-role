#!/usr/bin/python
# Make coding more python3-ish
from __future__ import (absolute_import, division)
__metaclass__ = type

# => Import native Python Modules
import pytest
import unittest
import json

# # NOTE: Required to find the location of the modules when testing
# # TODO:  Strip this from the final
import sys
import os
sys.path.append(os.path.realpath('.'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))
print sys.path

# => Import Ansible Test Modules
from ansible.compat.tests import unittest
from ansible.compat.tests.mock import call, create_autospec, patch
from ansible.module_utils.six import StringIO
import ansible.module_utils.six.moves.urllib.error as urllib_error

# => Import Cohesity Modules and Helpers
import library.cohesity_agent as cohesity_agent

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

    def test__download__agent(connection):
        module = FakeModule(
            server = "cohesity.lab",
            username = "admin",
            password = "password"
          )

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return False. This
        # => should trigger the Code to return back to the `get_token` method.
        check_patcher = patch(
            'module_utils.storage.cohesity.cohesity_auth.Authentication.get_token')
        mock_check = check_patcher.start()
        mock_check.return_value = "mytoken"

        check_patcher = patch(
            'library.cohesity_agent.download_agent')
        mock_check = check_patcher.start()
        mock_check.return_value = "/tmp/cohesity_agent_installer"

        filename = cohesity_agent.download_agent(module, "/tmp")

        assert filename == "/tmp/cohesity_agent_installer"

    def test__install__agent(connection):
        module = FakeModule(
            server = "cohesity.lab",
            username = "admin",
            password = "password"
          )

        check_patcher = patch(
            'library.cohesity_agent.install_agent')
        mock_check = check_patcher.start()
        mock_check.return_value = True, "Successfully Installed the Cohesity agent"

        filename = "/tmp/cohesity_agent_installer"
        changed, message = cohesity_agent.install_agent(module, filename)

        assert changed == True
        assert message == "Successfully Installed the Cohesity agent"

    def test__remove__agent(connection):
        module = FakeModule(
            server = "cohesity.lab",
            username = "admin",
            password = "password"
          )

        check_patcher = patch(
            'library.cohesity_agent.remove_agent')
        mock_check = check_patcher.start()
        mock_check.return_value = True, "Successfully Removed the Cohesity agent"

        filename = "/tmp/cohesity_agent_installer"
        changed, message = cohesity_agent.remove_agent(module, filename)

        assert changed == True
        assert message == "Successfully Removed the Cohesity agent"
