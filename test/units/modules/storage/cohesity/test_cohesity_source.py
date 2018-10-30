# Make coding more python3-ish
from __future__ import (absolute_import, division)
__metaclass__ = type

# # NOTE: Required to find the location of the modules when testing
from sys import path as sys_path
from os import path as os_path
from os import environ

# => Import Cohesity Modules and Helpers

current_path = sys_path
try:
    sys_path.append(os_path.join(os_path.dirname(__file__), '../../../../../'))
    sys_path.append(os_path.join(os_path.dirname(__file__),
                                 '../../../module_utils/storage/cohesity/helpers'))
    from library import cohesity_source
    # => Set the default Module and ModuleUtility Paths
    global_module_path = 'library'
    global_module_util_path = 'module_utils.storage.cohesity'
    from cohesity_helper import unittest, FakeModule, ModuleTestCase, set_module_args, json, \
        patch, AnsibleExitJson, AnsibleFailJson, cohesity___reg_verify__helper, pytest
except:
    # => Reset the correct path Location
    sys_path = current_path
    from ansible.modules.storage.cohesity import cohesity_source
    sys_path.append(os_path.join(environ['PYTHONPATH'], '../test'))
    from units.module_utils.storage.cohesity.helpers.cohesity_helper import unittest, FakeModule, \
        ModuleTestCase, set_module_args, json, \
        patch, AnsibleExitJson, AnsibleFailJson, \
        cohesity___reg_verify__helper, pytest
    # => Set the default Module and ModuleUtility Paths
    global_module_path = 'ansible.modules.storage.cohesity'
    global_module_util_path = 'ansible.module_utils.storage.cohesity'

exit_return_dict = {}

# => Success Test Cases


class TestProtectionSource__Methods(unittest.TestCase):

    def tearDown(self):
        self.patcher.stop()

    def test__protection_source_registration__status_physical(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        source_list = """
        {
          "nodes": [{
            "protectionSource": {
              "id": 1,
              "name": "myendpoint"
            }
          }]
        }
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_source.get__prot_source__all')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        data = dict(
            token='mytoken',
            environment='Physical',
            endpoint='myendpoint'
        )

        return_id = cohesity_source.get__protection_source_registration__status(
            module, data)

        assert return_id == 1

    def test__protection_source_registration__status_generic_nas(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        source_list = """
        {
          "nodes": [{
            "protectionSource": {
              "id": 1,
              "name": "myendpoint"
            }
          }]
        }
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_source.get__prot_source__all')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        data = dict(
            token='mytoken',
            environment='GenericNas',
            endpoint='myendpoint'
        )

        return_id = cohesity_source.get__protection_source_registration__status(
            module, data)

        assert return_id == 1

    def test__protection_source_registration__status_vmware(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        source_list = """
        {
          "registrationInfo": {
            "accessInfo": {
              "id": 1,
              "endpoint": "myendpoint"
            }
          },
          "protectionSource": {
            "id": 1
          }
        }
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_source.get__prot_source__all')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        data = dict(
            token='mytoken',
            environment='VMware',
            endpoint='myendpoint'
        )

        return_id = cohesity_source.get__protection_source_registration__status(
            module, data)

        assert return_id == 1

    def test__register_source__physical(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        source_list = """
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
          }
        }
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_source.register_source')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        data = dict(
            token='mytoken',
            environment='Physical',
            endpoint='myendpoint'
        )

        return_id = cohesity_source.register_source(module, data)

        assert return_id['ProtectionSource']['hostType'] == "kLinux"
        assert return_id['ProtectionSource']['id']['id'] == 240

    def test__register_source__vmware(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        source_list = """
        {
          "ProtectionSource": {
            "id": {
              "uuid": "ebd9bfce-b845-4aa3-842a-3f0dc381bbab"
            },
            "name": "vc-67.eco.eng.cohesity.com",
            "type": "kVCenter"
          }
        }
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_source.register_source')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        data = dict(
            token='mytoken',
            environment='Vmware',
            endpoint='myendpoint'
        )

        return_id = cohesity_source.register_source(module, data)

        assert return_id['ProtectionSource']['type'] == "kVCenter"
        assert return_id['ProtectionSource']['id'][
            'uuid'] == "ebd9bfce-b845-4aa3-842a-3f0dc381bbab"

    def test__unregister_source__physical(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        source_list = """
        {
          "id": 241,
          "endpoint": "mylinux.host.lab"
        }
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_source.unregister_source')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        data = dict(
            token='mytoken',
            environment='Physical',
            endpoint='myendpoint'
        )

        return_id = cohesity_source.unregister_source(module, data)

        assert return_id['endpoint'] == "mylinux.host.lab"
        assert return_id['id'] == 241


class TestProtectionSource__Main(ModuleTestCase):

    def load_module_args(self, **kwargs):
        arguments = dict(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True,
            state="present",
            endpoint="myhost",
            environment="Physical"
        )
        arguments.update(**kwargs)
        return set_module_args(arguments)

    def unload_patchers(self, patchers):
        for patcher in patchers.keys():
            patchers[patcher].stop()

    def patch__methods(self, reg_return=False):
        source_list = """
        {
          "ProtectionSource": {
            "id": {
              "uuid": "ebd9bfce-b845-4aa3-842a-3f0dc381bbab"
            },
            "name": "vc-67.eco.eng.cohesity.com",
            "type": "kVCenter"
          }
        }
        """
        patch_list = dict()

        token_patcher = patch(
            global_module_path + '.cohesity_source.get__cohesity_auth__token')
        mock_check = token_patcher.start()
        patch_list.update(token_patcher=token_patcher)
        mock_check.return_value = 'mytoken'

        registration_patcher = patch(
            global_module_path + '.cohesity_source.get__protection_source_registration__status')
        mock_check = registration_patcher.start()
        patch_list.update(registration_patcher=registration_patcher)
        mock_check.return_value = reg_return

        register_patcher = patch(
            global_module_path + '.cohesity_source.register_source')
        mock_check = register_patcher.start()
        patch_list.update(register_patcher=register_patcher)
        mock_check.return_value = json.loads(source_list)

        unregister_patcher = patch(
            global_module_path + '.cohesity_source.unregister_source')
        mock_check = unregister_patcher.start()
        patch_list.update(unregister_patcher=unregister_patcher)
        mock_check.return_value = json.loads(source_list)

        return patch_list

    def test__main__register_source__physical(self):
        patchers = dict(patchers=[])
        self.load_module_args()
        # => Configure Patchers
        patch_list = self.patch__methods()

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_source.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], True, result)
        self.assertEqual(
            result['msg'], 'Registration of Cohesity Protection Source Complete', result)
        self.unload_patchers(patch_list)

    def test__main__register_source__no_change(self):
        self.load_module_args()
        # => Configure Patchers
        patch_list = self.patch__methods(reg_return=1)

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_source.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], False, result)
        self.assertEqual(
            result['msg'], 'The Protection Source for this host is already registered', result)
        self.unload_patchers(patch_list)

    def test__main__unregister_source__physical(self):
        self.load_module_args(state="absent")
        # => Configure Patchers
        patch_list = self.patch__methods(reg_return=1)

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_source.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], True, result)
        self.assertEqual(
            result['msg'], 'Unregistration of Cohesity Protection Source Complete', result)
        self.unload_patchers(patch_list)

    def test__main__unregister_source__no_change(self):
        self.load_module_args(state="absent")
        # => Configure Patchers
        patch_list = self.patch__methods(reg_return=False)

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_source.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], False, result)
        self.assertEqual(result[
                         'msg'], 'The Protection Source for this host is currently not registered', result)
        self.unload_patchers(patch_list)

    def test__main__register_source__nas_smb__check_pass(self):
        patchers = dict(patchers=[])
        override_args = dict(
            endpoint="\\\\server\\share",
            environment="GenericNas",
            nas_protocol="SMB",
            nas_username="cohesity",
            nas_password="cohesity"
        )
        self.load_module_args(**override_args)
        # => Configure Patchers
        patch_list = self.patch__methods()

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_source.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], True, result)
        self.assertEqual(
            result['msg'], 'Registration of Cohesity Protection Source Complete', result)
        self.unload_patchers(patch_list)

    def test__main__register_source__nas_smb__check_fail(self):
        patchers = dict(patchers=[])
        override_args = dict(
            endpoint="\\\\server\\share",
            environment="GenericNas",
            nas_protocol="SMB"
        )
        self.load_module_args(**override_args)
        # => Configure Patchers
        patch_list = self.patch__methods()
        # patch_list['register_patcher'].stop()

        with self.assertRaises(AnsibleFailJson) as exc:
            cohesity_source.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], False, result)
        self.assertEqual(
            result['msg'], 'The following variables are mandatory for this action (creation) when working with environment type (GenericNas)', result)
        self.unload_patchers(patch_list)
