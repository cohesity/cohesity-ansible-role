#!/usr/bin/python
# Make coding more python3-ish
from __future__ import (absolute_import, division)
__metaclass__ = type

# => Import native Python Modules
import pytest
import unittest
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
except:
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
    import library.cohesity_facts as cohesity_facts
    # => Set the default Module and ModuleUtility Paths
    global_module_path = 'library'
    global_module_util_path = 'module_utils.storage.cohesity'
except:
    # => Reset the correct path Location
    sys_path = current_path
    import ansible.modules.storage.cohesity.cohesity_facts as cohesity_facts
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
class TestClusterFacts(unittest.TestCase):

    def test__get__clusters(connection):

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return False. This
        # => should trigger the Code to return back to the `get_token` method.
        check_patcher = patch(
            global_module_util_path + '.cohesity_auth.Authentication.get_token')
        mock_check = check_patcher.start()
        mock_check.return_value = {
            "accessToken": "mytoken", "tokenType": "Bearer"}

        check_patcher = patch(
            global_module_path + '.cohesity_facts.get__cluster')
        mock_check = check_patcher.start()
        mock_check.return_value = False, [
            {"name": "cluster01", "clusterSoftwareVersion": "6.0.0"}]

        changed, cluster = cohesity_facts.get__cluster(
            "cohesity-api", "administrator", "password", "no")

        assert changed is False
        assert cluster == [{"name": "cluster01",
                            "clusterSoftwareVersion": "6.0.0"}]

    def test__get__cluster_failed(connection):

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return False. This
        # => should trigger the Code to return back to the `get_token` method.
        check_patcher = patch(
            global_module_util_path + '.cohesity_auth.Authentication.get_token')
        mock_check = check_patcher.start()
        mock_check.return_value = {
            "accessToken": "mytoken", "tokenType": "Bearer"}

        check_patcher = patch(
            global_module_path + '.cohesity_facts.get__cluster')
        mock_check = check_patcher.start()
        mock_check.return_value = False, []

        changed, cluster = cohesity_facts.get__cluster(
            "cohesity-api", "administrator", "password", "no")

        assert changed is False
        assert cluster == []


class TestNodeFacts(unittest.TestCase):

    def test__get__nodes(connection):

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return False. This
        # => should trigger the Code to return back to the `get_token` method.
        check_patcher = patch(
            global_module_util_path + '.cohesity_auth.Authentication.get_token')
        mock_check = check_patcher.start()
        mock_check.return_value = {
            "accessToken": "mytoken", "tokenType": "Bearer"}

        check_patcher = patch(
            global_module_path + '.cohesity_facts.get__nodes')
        mock_check = check_patcher.start()
        mock_check.return_value = False, [
            {"id": "1234", "clusterPartitionName": "primary"}]

        changed, nodes = cohesity_facts.get__nodes(
            "cohesity-api", "administrator", "password", "no")

        assert changed is False
        assert nodes == [{"id": "1234", "clusterPartitionName": "primary"}]

    def test__get__nodes_empty(connection):

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return False. This
        # => should trigger the Code to return back to the `get_token` method.
        check_patcher = patch(
            global_module_util_path + '.cohesity_auth.Authentication.get_token')
        mock_check = check_patcher.start()
        mock_check.return_value = {
            "accessToken": "mytoken", "tokenType": "Bearer"}

        check_patcher = patch(
            global_module_path + '.cohesity_facts.get__nodes')
        mock_check = check_patcher.start()
        mock_check.return_value = False, []

        changed, nodes = cohesity_facts.get__nodes(
            "cohesity-api", "administrator", "password", "no")

        assert changed is False
        assert nodes == []
