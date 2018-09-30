#!/usr/bin/python
# Make coding more python3-ish
from __future__ import (absolute_import, division)
__metaclass__ = type

# => Import native Python Modules
import pytest
import unittest
import json

# try:
#     import library.cohesity_facts as cohesity_facts
# except ImportError:
#     print "skip?"# pytestmark = pytest.mark.skip("This test requires the Cohesity Python libraries")

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
import library.cohesity_facts as cohesity_facts

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
            'module_utils.storage.cohesity.cohesity_auth.Authentication.get_token')
        mock_check = check_patcher.start()
        mock_check.return_value = {
            "accessToken": "mytoken", "tokenType": "Bearer"}

        check_patcher = patch(
            'library.cohesity_facts.get_cluster')
        mock_check = check_patcher.start()
        mock_check.return_value = False, [
            {"name": "cluster01", "clusterSoftwareVersion": "6.0.0"}]

        changed, cluster = cohesity_facts.get_cluster(
            "cohesity-api", "administrator", "password", "no")

        assert changed is False
        assert cluster == [{"name": "cluster01", "clusterSoftwareVersion": "6.0.0"}]

    def test__get__cluster_failed(connection):

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return False. This
        # => should trigger the Code to return back to the `get_token` method.
        check_patcher = patch(
            'module_utils.storage.cohesity.cohesity_auth.Authentication.get_token')
        mock_check = check_patcher.start()
        mock_check.return_value = {
            "accessToken": "mytoken", "tokenType": "Bearer"}

        check_patcher = patch(
            'library.cohesity_facts.get_cluster')
        mock_check = check_patcher.start()
        mock_check.return_value = False, []

        changed, cluster = cohesity_facts.get_cluster(
            "cohesity-api", "administrator", "password", "no")

        assert changed is False
        assert cluster == []

class TestNodeFacts(unittest.TestCase):

    def test__get__nodes(connection):

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return False. This
        # => should trigger the Code to return back to the `get_token` method.
        check_patcher = patch(
            'module_utils.storage.cohesity.cohesity_auth.Authentication.get_token')
        mock_check = check_patcher.start()
        mock_check.return_value = {
            "accessToken": "mytoken", "tokenType": "Bearer"}

        check_patcher = patch(
            'library.cohesity_facts.get_nodes')
        mock_check = check_patcher.start()
        mock_check.return_value = False, [
            {"id": "1234", "clusterPartitionName": "primary"}]

        changed, nodes = cohesity_facts.get_nodes(
            "cohesity-api", "administrator", "password", "no")

        assert changed is False
        assert nodes == [{"id": "1234", "clusterPartitionName": "primary"}]

    def test__get__nodes_empty(connection):

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return False. This
        # => should trigger the Code to return back to the `get_token` method.
        check_patcher = patch(
            'module_utils.storage.cohesity.cohesity_auth.Authentication.get_token')
        mock_check = check_patcher.start()
        mock_check.return_value = {
            "accessToken": "mytoken", "tokenType": "Bearer"}

        check_patcher = patch(
            'library.cohesity_facts.get_nodes')
        mock_check = check_patcher.start()
        mock_check.return_value = False, []

        changed, nodes = cohesity_facts.get_nodes(
            "cohesity-api", "administrator", "password", "no")

        assert changed is False
        assert nodes == []
