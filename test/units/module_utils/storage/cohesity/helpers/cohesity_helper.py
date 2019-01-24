import re

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
except Exception as e:
    # => With this change, we need to include the 'test' directory
    # => in our path
    sys_path.append(os_path.join(environ['PYTHONPATH'], '../test'))
    from units.compat import unittest
    from units.compat.mock import call, create_autospec, patch

from units.modules.utils import set_module_args, AnsibleExitJson, AnsibleFailJson, ModuleTestCase
from ansible.module_utils.six import StringIO
import ansible.module_utils.six.moves.urllib.error as urllib_error


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


class cohesity___reg_verify__helper:
    """Assert that a given string meets some expectations."""

    def __init__(self, pattern, flags=0):
        self._regex = re.compile(pattern, flags)

    def __check__(self, actual):
        return bool(self._regex.match(actual))

    def __repr__(self):
        return self._regex.pattern
