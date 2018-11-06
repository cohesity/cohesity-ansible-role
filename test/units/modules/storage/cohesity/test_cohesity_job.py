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
    from library import cohesity_job
    # => Set the default Module and ModuleUtility Paths
    global_module_path = 'library'
    global_module_util_path = 'module_utils.storage.cohesity'
    from cohesity_helper import unittest, FakeModule, ModuleTestCase, set_module_args, json, \
        patch, AnsibleExitJson, AnsibleFailJson, cohesity___reg_verify__helper, pytest
except:
    # => Reset the correct path Location
    sys_path = current_path
    from ansible.modules.storage.cohesity import cohesity_job
    sys_path.append(os_path.join(environ['PYTHONPATH'], '../test'))
    from units.module_utils.storage.cohesity.helpers.cohesity_helper import unittest, FakeModule, ModuleTestCase, set_module_args, json, \
        patch, AnsibleExitJson, AnsibleFailJson, cohesity___reg_verify__helper, pytest
    # => Set the default Module and ModuleUtility Paths
    global_module_path = 'ansible.modules.storage.cohesity'
    global_module_util_path = 'ansible.module_utils.storage.cohesity'

exit_return_dict = {}

# => Success Test Cases
class TestProtectionSource__Methods(unittest.TestCase):

    def tearDown(self):
        self.patcher.stop()

    def test__check__protection_job__exists(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        source_list = """
        [{
          "id": 1,
          "name": "myendpoint"
        }]
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_job.get__protection_jobs__by_environment')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        data = dict(
            token='mytoken',
            environment='Physical',
            name='myendpoint'
        )

        return_id = cohesity_job.check__protection_job__exists(
            module, data)

        assert return_id == 1

    def test__register_job__physical(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        source_list = """
        {
          "environment": "Physical",
          "id": 24,
          "name": "myendpoint",
          "priority": "Low",
          "start_time": {
            "hour": "02",
            "minute": "00"
          }
        }
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_job.register_job')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        data = dict(
            token='mytoken',
            environment='Physical',
            endpoint='myendpoint'
        )

        return_id = cohesity_job.register_job(module, data)

        assert return_id['environment'] == "Physical"
        assert return_id['name'] == 'myendpoint'
        assert return_id['id'] == 24

    def test__start_job__physical(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_job.start_job')
        mock_check = self.patcher.start()
        mock_check.return_value = dict(id=24)

        data = dict(
            token='mytoken',
            id=24
        )

        return_id = cohesity_job.start_job(module, data)

        assert return_id['id'] == 24

    def test__stop_running_job__pass(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_job.stop_job')
        mock_check = self.patcher.start()
        mock_check.return_value = dict(id=24)

        data = dict(
            token='mytoken',
            id=24
        )

        return_id = cohesity_job.stop_job(module, data)

        assert return_id['id'] == 24

    def test__stop_non_running_job__no_change(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )
        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_job.get__protection_run__all__by_id')
        mock_check = self.patcher.start()
        mock_check.return_value = dict()

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_job.stop_job')
        mock_check = self.patcher.start()
        mock_check.return_value = dict(id=24)

        data = dict(
            token='mytoken',
            id=24
        )

        return_id = cohesity_job.stop_job(module, data)

        assert return_id['id'] == 24

    def test__stop_running_job__fail(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True,
            cancel_active=False
        )

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_job.get__protection_run__all__by_id')
        mock_check = self.patcher.start()
        mock_check.return_value = [
            dict(
                id=24,
                backupRun=dict(
                    jobRunId='751'
                )
            )
        ]

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_job.open_url')
        mock_check = self.patcher.start()
        check_var = mock_check.return_value

        # =>
        check_var.read.return_value = ''
        check_var.getcode.return_value = 204
        mock_check.return_value = check_var

        data = dict(
            token='mytoken',
            id=24
        )
        with pytest.raises(Exception) as error:
            cohesity_job.stop_job(module, data)

        assert str(error.value) == 'FAIL'
        assert module.exit_kwargs == dict(
            changed=False,
            msg='The Protection Job for this host is active and cannot be stopped'
        )

    def test__stop_running_job__force__pass(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True,
            cancel_active=True
        )

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_job.get__protection_run__all__by_id')
        mock_check = self.patcher.start()
        mock_check.return_value = [
            dict(
                id=24,
                backupRun=dict(
                    jobRunId='751'
                )
            )
        ]

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_job.open_url')
        mock_check = self.patcher.start()
        check_var = mock_check.return_value

        # =>
        check_var.read.return_value = ''
        check_var.getcode.return_value = 204
        mock_check.return_value = check_var

        data = dict(
            token='mytoken',
            id=24
        )
        self.patcher_transition = patch(
            global_module_path + '.cohesity_job.wait__for_job_state__transition')
        self.patcher_transition.start()
        return_id = cohesity_job.stop_job(module, data)

        self.patcher_transition.stop()
        assert return_id['id'] == 24

    def test__unregister_job__physical(self):
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
            global_module_path + '.cohesity_job.unregister_job')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        data = dict(
            token='mytoken',
            environment='Physical',
            endpoint='myendpoint'
        )

        return_id = cohesity_job.unregister_job(module, data)

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
            name="myhost",
            environment="Physical",
            protection_sources=list("myhost")
        )
        arguments.update(**kwargs)
        return set_module_args(arguments)

    def unload_patchers(self, patchers):
        for patcher in patchers.keys():
            patchers[patcher].stop()

    def set__default__return(self):
        source_list = """
        {
          "environment": "Physical",
          "id": 24,
          "name": "myendpoint",
          "priority": "Low",
          "start_time": {
            "hour": "02",
            "minute": "00"
          }
        }
        """
        return json.loads(source_list)

    def patch__methods(self, reg_return=False):
        source_list = self.set__default__return()
        patch_list = dict()

        token_patcher = patch(
            global_module_path + '.cohesity_job.get__cohesity_auth__token')
        mock_check = token_patcher.start()
        patch_list.update(token_patcher=token_patcher)
        mock_check.return_value = 'mytoken'

        registration_patcher = patch(
            global_module_path + '.cohesity_job.check__protection_job__exists')
        mock_check = registration_patcher.start()
        patch_list.update(registration_patcher=registration_patcher)
        mock_check.return_value = reg_return

        mandatory_patcher = patch(
            global_module_path + '.cohesity_job.check__mandatory__params')
        mock_check = mandatory_patcher.start()
        patch_list.update(mandatory_patcher=mandatory_patcher)
        mock_check.return_value = False

        prot_source_patcher = patch(
            global_module_path + '.cohesity_job.get__prot_source_id__by_endpoint')
        mock_check = prot_source_patcher.start()
        patch_list.update(prot_source_patcher=prot_source_patcher)
        mock_check.return_value = 1

        prot_root_patcher = patch(
            global_module_path + '.cohesity_job.get__prot_source_root_id__by_environment')
        mock_check = prot_root_patcher.start()
        patch_list.update(prot_root_patcher=prot_root_patcher)
        mock_check.return_value = 1

        prot_policy_patcher = patch(
            global_module_path + '.cohesity_job.get__prot_policy_id__by_name')
        mock_check = prot_policy_patcher.start()
        patch_list.update(prot_policy_patcher=prot_policy_patcher)
        mock_check.return_value = 1

        storage_domain_patcher = patch(
            global_module_path + '.cohesity_job.get__storage_domain_id__by_name')
        mock_check = storage_domain_patcher.start()
        patch_list.update(storage_domain_patcher=storage_domain_patcher)
        mock_check.return_value = 1

        register_patcher = patch(
            global_module_path + '.cohesity_job.register_job')
        mock_check = register_patcher.start()
        patch_list.update(register_patcher=register_patcher)
        mock_check.return_value = source_list

        unregister_patcher = patch(
            global_module_path + '.cohesity_job.unregister_job')
        mock_check = unregister_patcher.start()
        patch_list.update(unregister_patcher=unregister_patcher)
        mock_check.return_value = source_list

        start_job_patcher = patch(
            global_module_path + '.cohesity_job.start_job')
        mock_check = start_job_patcher.start()
        patch_list.update(start_job_patcher=start_job_patcher)
        mock_check.return_value = source_list

        stop_job_patcher = patch(
            global_module_path + '.cohesity_job.stop_job')
        mock_check = stop_job_patcher.start()
        patch_list.update(stop_job_patcher=stop_job_patcher)
        mock_check.return_value = source_list

        return patch_list

    def test__main__register_job__physical(self):
        self.load_module_args()
        # => Configure Patchers
        patch_list = self.patch__methods()

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_job.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], True, result)
        self.assertEqual(
            result['msg'], 'Registration of Cohesity Protection Job Complete', result)

        self.unload_patchers(patch_list)

    def test__main__register_job__no_change(self):
        self.load_module_args()
        # => Configure Patchers
        patch_list = self.patch__methods(reg_return=1)

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_job.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], False, result)
        self.assertEqual(
            result['msg'], 'The Protection Job for this host is already registered', result)

        self.unload_patchers(patch_list)

    def test__main__register_job__custom_start_time(self):
        self.load_module_args(start_time="04:15")
        # => Configure Patchers
        patch_list = self.patch__methods()

        source_list = self.set__default__return()
        source_list.update(dict(
            start_time=dict(
                hour="04",
                minute="15"
            )
        ))

        register_patcher = patch_list['register_patcher']
        register_patcher.stop()
        mock_check = register_patcher.start()
        mock_check.return_value = source_list

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_job.main()

        return_time = dict(
            hour="04",
            minute="15"
        )

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], True, result)
        self.assertEqual(
            result['msg'], 'Registration of Cohesity Protection Job Complete', result)
        self.assertEqual(result['start_time'],
                         return_time, [result, return_time])

        self.unload_patchers(patch_list)

    def test__main__register_job__custom_start_time_error(self):
        self.load_module_args(start_time="04:150")
        # => Configure Patchers
        patch_list = self.patch__methods()

        with self.assertRaises(AnsibleFailJson) as exc:
            cohesity_job.main()

        return_time = dict(
            hour="04",
            minute="15"
        )

        result = exc.exception.args[0]
        self.assertTrue(result['failed'], result)
        assert cohesity___reg_verify__helper(
            '.+(Please review and submit the correct Protection Job Starting time).+').__check__(str(result))

        self.unload_patchers(patch_list)

    def test__main__unregister_job__physical(self):
        self.load_module_args(state="absent")
        # => Configure Patchers
        patch_list = self.patch__methods(reg_return=1)

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_job.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], True, result)
        self.assertEqual(
            result['msg'], 'Unregistration of Cohesity Protection Job Complete', result)

        self.unload_patchers(patch_list)

    def test__main__unregister_job__no_change(self):
        self.load_module_args(state="absent")
        # => Configure Patchers
        patch_list = self.patch__methods(reg_return=False)

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_job.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], False, result)
        self.assertEqual(result[
                         'msg'], 'The Protection Job for this host is currently not registered', result)

        self.unload_patchers(patch_list)

    def test__main__start_job__physical(self):
        self.load_module_args(state="started")
        # => Configure Patchers
        patch_list = self.patch__methods(reg_return=1)

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_job.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], True, result)
        self.assertEqual(
            result['msg'], 'The Protection Job for this host has been started', result)

    def test__main__stop_job__not_running(self):
        self.load_module_args(state="stopped")
        # => Configure Patchers
        patch_list = self.patch__methods(reg_return=1)

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_job.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], True, result)
        self.assertEqual(
            result['msg'], 'The Protection Job for this host has been stopped', result)
