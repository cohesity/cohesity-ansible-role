# Make coding more python3-ish
from __future__ import (absolute_import, division)
__metaclass__ = type

# # NOTE: Required to find the location of the modules when testing
from sys import path as sys_path
from os import path as os_path
from os import environ

# => Import Cohesity Modules and Helpers

current_path = sys_path
# try:
sys_path.append(os_path.join(os_path.dirname(__file__), '../../../../../'))
sys_path.append(os_path.join(os_path.dirname(__file__),
                             '../../../module_utils/storage/cohesity/helpers'))
from library import cohesity_restore
# => Set the default Module and ModuleUtility Paths
global_module_path = 'library'
global_module_util_path = 'module_utils.storage.cohesity'
try:
    from cohesity_helper import unittest, FakeModule, ModuleTestCase, set_module_args, json, \
        patch, AnsibleExitJson, AnsibleFailJson, cohesity___reg_verify__helper, pytest
except Exception as e:
    # => Reset the correct path Location
    sys_path = current_path
    from ansible.modules.storage.cohesity import cohesity_restore
    sys_path.append(os_path.join(environ['PYTHONPATH'], '../test'))
    from units.module_utils.storage.cohesity.helpers.cohesity_helper import unittest, FakeModule, ModuleTestCase, set_module_args, json, \
        patch, AnsibleExitJson, AnsibleFailJson, cohesity___reg_verify__helper, pytest
    # => Set the default Module and ModuleUtility Paths
    global_module_path = 'ansible.modules.storage.cohesity'
    global_module_util_path = 'ansible.module_utils.storage.cohesity'

exit_return_dict = {}


class ParameterViolation(Exception):
    pass


# => Success Test Cases
class TestProtectionSource__Methods(unittest.TestCase):

    def tearDown(self):
        if 'patcher' in dir(self):
            self.patcher.stop()

    def test__check__protection_restore__exists(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        data = dict(
            token='mytoken',
            name="myhost"
        )

        self.patcher = patch(
            global_module_path + '.cohesity_restore.get__restore_job__by_type')
        mock_check = self.patcher.start()
        mock_check.return_value = []

        return_id = cohesity_restore.check__protection_restore__exists(
            module, data)

        assert return_id == "False"

    def test_convert__windows_file_name__no_change(self):
        filename = "/C/data/file"

        return_file = cohesity_restore.convert__windows_file_name(filename)

        assert return_file == filename

    def test_convert__windows_file_name__double_slashes(self):
        filename = "C:\\data\\file"

        return_file = cohesity_restore.convert__windows_file_name(filename)

        assert return_file == "/C/data/file"

    def test_convert__windows_file_name__quad_slashes(self):
        filename = "C:\\\\data\\file"

        return_file = cohesity_restore.convert__windows_file_name(filename)

        assert return_file == "/C/data/file"

    def test_convert__windows_file_name__no_drive_letter_exception(self):
        filename = "\\data\\file"

        with pytest.raises(Exception) as error:
            cohesity_restore.convert__windows_file_name(filename)
        assert str(error.value) == "Windows Based files must be in /Drive/path/to/file or Drive:\\path\\to\\file format."

    def test__get__snapshot_information__for_file(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        source_list = """
        {
          "jobRunId": "123",
          "jobUid": {
            "clusterId": 99,
            "clusterIncarnationId": 98,
            "id": 24
          },
          "protectionSourceId": 12,
          "startedTimeUsecs": "1541603218"
        }
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_restore.get__snapshot_information__for_file')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        data = dict(
            token='mytoken',
            environment='Physical',
            endpoint='myendpoint'
        )

        return_id = cohesity_restore.get__snapshot_information__for_file(module, data)

        assert return_id['jobRunId'] == "123"
        assert return_id['startedTimeUsecs'] == '1541603218'
        assert return_id['jobUid']['id'] == 24

    def test__get__snapshot_information__for_file__find_snapshot(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        source_list = """
        [{
          "name": "myendpoint",
          "uid": {
            "clusterId": 99,
            "clusterIncarnationId": 98,
            "id": 24
          },
          "sourceIds": [12]
        }]
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_restore.get__protection_jobs__by_environment')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        self.patch_url = patch(
            global_module_util_path + '.cohesity_hints.open_url')
        self.open_url = self.patch_url.start()

        # =>
        stream = self.open_url.return_value
        stream.read.return_value = '[{"snapshot":{"jobRunId": "123","startedTimeUsecs": "1541603218"}}]'
        stream.getcode.return_value = 200
        self.open_url.return_value = stream
        mockData = json.loads(stream.read.return_value)

        data = dict(
            token='mytoken',
            environment='Physical',
            job_name='myendpoint',
            file_names=["/C/data/file"]
        )

        return_id = cohesity_restore.get__snapshot_information__for_file(module, data)

        self.assertEqual(1, self.open_url.call_count)
        assert return_id['jobRunId'] == "123"
        assert return_id['startedTimeUsecs'] == "1541603218"
        assert return_id['jobUid']['id'] == 24

        self.patch_url.stop()

    def test__get__snapshot_information__for_file__no_job(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        source_list = """
        []
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_restore.get__protection_jobs__by_environment')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        data = dict(
            token='mytoken',
            environment='Physical',
            job_name='myendpoint',
            file_names=["/C/data/file"]
        )

        with pytest.raises(Exception) as error:
            failure = cohesity_restore.get__snapshot_information__for_file(module, data)

        assert str(error.value) == "FAIL"
        fail_json = module.exit_kwargs
        assert fail_json['changed'] == "False"
        assert fail_json['job_name'] == data['job_name']
        assert fail_json['msg'] == "Failed to find chosen Job name for the selected Environment Type."

    def test__get__snapshot_information__for_file__no_snapshot(self):
        module = FakeModule(
            token='mytoken',
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        source_list = """
        [{
          "name": "myendpoint",
          "uid": {
            "clusterId": 99,
            "clusterIncarnationId": 98,
            "id": 24
          },
          "sourceIds": [12]
        }]
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_restore.get__protection_jobs__by_environment')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(source_list)

        # => Return an empty Array for the file snapshots
        self.patcher2 = patch(
            global_module_path + '.cohesity_restore.get__file_snapshot_information__by_filename')
        mock_check = self.patcher2.start()
        mock_check.return_value = json.loads("[]")

        data = dict(
            token='mytoken',
            environment='Physical',
            job_name='myendpoint',
            file_names=["/C/data/file"]
        )

        with pytest.raises(Exception) as error:
            failure = cohesity_restore.get__snapshot_information__for_file(module, data)

        assert str(error.value) == "FAIL"
        fail_json = module.exit_kwargs
        assert fail_json['changed'] == "False"
        assert fail_json['job_name'] == data['job_name']
        assert fail_json['filename'] == data['file_names'][0]
        assert fail_json['msg'] == "Failed to find a snapshot for the file in the chosen Job name."

        self.patcher2.stop()

    def test__start_restore__files(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        restore_job = """
        {
            "fullViewName": "cohesity_int_15389",
            "id": 15389,
            "name": "Ansible Test Restore",
            "objects": [
                {
                    "jobRunId": 14294,
                    "jobUid": {
                        "clusterId": 8621173906188849,
                        "clusterIncarnationId": 1538852526333,
                        "id": 10539
                    },
                    "protectionSourceId": 531,
                    "startedTimeUsecs": 1541435376134254
                }
            ],
            "startTimeUsecs": 1541613680583185,
            "status": "kReadyToSchedule",
            "type": "kRestoreFiles",
            "viewBoxId": 5
        }
        """

        # =>
        self.patcher = patch(
            global_module_path + '.cohesity_restore.start_restore__files')
        mock_check = self.patcher.start()
        mock_check.return_value = json.loads(restore_job)

        data = dict(
            token='mytoken',
            environment='Physical',
            job_name='myendpoint',
            file_names=["/C/data/file"]
        )

        return_id = cohesity_restore.start_restore__files(module, data)

        assert return_id['id'] == 15389

    def test__start_restore__files__open_url(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        restore_job = """
        {
            "fullViewName": "cohesity_int_15389",
            "id": 15389,
            "name": "Ansible Test Restore",
            "objects": [
                {
                    "jobRunId": 14294,
                    "jobUid": {
                        "clusterId": 8621173906188849,
                        "clusterIncarnationId": 1538852526333,
                        "id": 10539
                    },
                    "protectionSourceId": 531,
                    "startedTimeUsecs": 1541435376134254
                }
            ],
            "startTimeUsecs": 1541613680583185,
            "status": "kReadyToSchedule",
            "type": "kRestoreFiles",
            "viewBoxId": 5
        }
        """

        # =>

        self.patcher = patch(
            global_module_path + '.cohesity_restore.open_url')
        self.open_url = self.patcher.start()
        # =>
        stream = self.open_url.return_value
        stream.read.return_value = restore_job
        stream.getcode.return_value = 201
        self.open_url.return_value = stream
        mockData = json.loads(stream.read.return_value)

        data = dict(
            token='mytoken',
            environment='Physical',
            job_name='myendpoint',
            file_names=["/C/data/file"]
        )

        return_id = cohesity_restore.start_restore__files(module, data)

        assert return_id['id'] == 15389


class TestProtectionSource__Main(ModuleTestCase):
    def load_module_args(self, **kwargs):
        arguments = dict(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True,
            state="present",
            name="Ansible Restore File",
            job_name="myhost",
            endpoint="myhost",
            environment="Physical",
            file_names=list("/C/data/file")
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
            global_module_path + '.cohesity_restore.get__cohesity_auth__token')
        mock_check = token_patcher.start()
        patch_list.update(token_patcher=token_patcher)
        mock_check.return_value = 'mytoken'

        snapshot_list = """
        {
          "jobRunId": "123",
          "jobUid": {
            "clusterId": 99,
            "clusterIncarnationId": 98,
            "id": 24
          },
          "protectionSourceId": 12,
          "startedTimeUsecs": "1541603218"
        }
        """
        start_check_patcher = patch(
            global_module_path + '.cohesity_restore.check__protection_restore__exists')
        mock_check = start_check_patcher.start()
        patch_list.update(start_check_patcher=start_check_patcher)
        mock_check.return_value = False

        snapshot_info_patcher = patch(
            global_module_path + '.cohesity_restore.get__snapshot_information__for_file')
        mock_check = snapshot_info_patcher.start()
        patch_list.update(snapshot_info_patcher=snapshot_info_patcher)
        mock_check.return_value = json.loads(snapshot_list)

        start_job_patcher = patch(
            global_module_path + '.cohesity_restore.start_restore__files')
        mock_check = start_job_patcher.start()
        patch_list.update(start_job_patcher=start_job_patcher)
        mock_check.return_value = source_list
        return patch_list

    def test__main__restore__file(self):
        self.load_module_args()
        # => Configure Patchers
        patch_list = self.patch__methods()

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_restore.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], True, result)
        self.assertEqual(
            result['msg'], 'Registration of Cohesity Restore Job Complete', result)

        self.unload_patchers(patch_list)

    def test__main__restore__file__no_change(self):
        self.load_module_args()
        # => Configure Patchers
        patch_list = self.patch__methods()

        restore_job = """
        [{
          "id": 15389,
          "status": "kReadyToSchedule",
          "name": "myhost"
        }]
        """

        start_check_patcher = patch_list['start_check_patcher']
        start_check_patcher.stop()
        patch_list.pop('start_check_patcher')

        self.patch_url = patch(
            global_module_util_path + '.cohesity_hints.open_url')
        self.open_url = self.patch_url.start()

        # =>
        stream = self.open_url.return_value
        stream.read.return_value = restore_job
        stream.getcode.return_value = 200
        self.open_url.return_value = stream
        mockData = json.loads(stream.read.return_value)

        with self.assertRaises(AnsibleExitJson) as exc:
            cohesity_restore.main()

        result = exc.exception.args[0]
        self.assertEqual(result['changed'], False, result)
        self.assertEqual(
            result['msg'], 'The Restore Job for is already registered', result)

        self.unload_patchers(patch_list)
