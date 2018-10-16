#!/usr/bin/python
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
    sys_path.append(os_path.join(os_path.dirname(
        __file__), '../../../../../module_utils'))
    sys_path.append(os_path.join(os_path.dirname(__file__),
                                 'helpers'))
    from storage.cohesity.cohesity_auth import Authentication, TokenException, ParameterViolation, get__cohesity_auth__token
    # => Set the default Module and ModuleUtility Paths
    global_module_path = 'library'
    global_module_util_path = 'storage.cohesity'
    from cohesity_helper import *
except:
    # => Reset the correct path Location
    sys_path = current_path
    from ansible.modules_utils.storage.cohesity.cohesity_auth import Authentication, TokenException, ParameterViolation, get__cohesity_auth__token
    sys_path.append(os_path.join(environ['PYTHONPATH'], '../test'))
    from units.module_utils.storage.cohesity.helpers.cohesity_helper import *
    # => Set the default Module and ModuleUtility Paths
    global_module_path = 'ansible.modules.storage.cohesity'
    global_module_util_path = 'ansible.module_utils.storage.cohesity'

# => Success Test Cases


class TestAuthentication(unittest.TestCase):
    ''' Cohesity Authentication Successful Tests '''

    def setUp(self):
        self.patcher = patch(
            global_module_util_path + '.cohesity_auth.open_url')
        self.open_url = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test__get__auth_token(self):
        ''' Test that we are able to gather an authentication token '''
        server = "cohesity-api"
        uri = "https://" + server + "/irisservices/api/v1/public/accessTokens"

        # => Mock the URL Return Data
        stream = self.open_url.return_value
        stream.read.return_value = '{"accessToken": "mytoken","tokenType": "Bearer"}'
        stream.getcode.return_value = 201
        self.open_url.return_value = stream
        mockData = json.loads(stream.read.return_value)

        # => Stage the return data and Class::Authentication object
        auth = Authentication()
        auth.url = uri
        auth.token = 'mytoken'

        # => Establish the real Class::Authentication call and return the output
        # => of the method.
        cohesity_auth = Authentication()
        cohesity_auth.username = "administrator"
        cohesity_auth.password = "password"
        data = cohesity_auth.get_token(server)

        # => Assert Test Cases are valid
        self.assertEqual(auth.token, data)
        self.assertEqual(1, self.open_url.call_count)
        self.assertEqual(201, self.open_url.return_value.getcode.return_value)
        expected = call(url=uri, data=json.dumps({
                        "username": "administrator", "password": "password"}), headers={'Accept': 'application/json'}, validate_certs=False)
        self.assertEqual(expected, self.open_url.call_args)

    def test__current__auth_token(self):
        ''' Test to see if the token is expired and if so then trigger a refresh. '''

        server = "cohesity-api"
        uri = "https://" + server + "/irisservices/api/v1/public/nodes"

        # =>
        stream = self.open_url.return_value
        stream.read.return_value = '[{"id": "1234","clusterPartitionName": "primary"}]'
        stream.getcode.return_value = 200
        self.open_url.return_value = stream
        mockData = json.loads(stream.read.return_value)

        # Exercise
        auth = Authentication()
        auth.url = uri

        cohesity_auth = Authentication()
        cohesity_auth.token = "mytoken"
        data = cohesity_auth.get_token(server)

        # Verify

        self.assertEqual(1, self.open_url.call_count)
        expected = call(url=uri, headers={
                        "Accept": "application/json", "Authorization": "Bearer mytoken"}, validate_certs=False)
        self.assertEqual(expected, self.open_url.call_args)

    def test__get__cohesity_auth__token(self):
        module = FakeModule(
            cluster="cohesity.lab",
            username="admin",
            password="password",
            validate_certs=True
        )

        check_patcher = patch(
            global_module_util_path + '.cohesity_auth.Authentication.get_token')
        mock_check = check_patcher.start()
        mock_check.return_value = 'mytoken'

        return_id = get__cohesity_auth__token(module)

        assert return_id == 'mytoken'
        check_patcher.stop()

# => Failure Test Cases


class TestFailedAuthentication(unittest.TestCase):

    def test_raise_exception_when_url_invalid(self):

        cohesity_auth = Authentication()
        cohesity_auth.username = "administrator"
        cohesity_auth.password = "password"
        with pytest.raises(TokenException) as error:
            cohesity_auth.get_token('bad-host-domain')
        assert error.type == TokenException
        assert cohesity___reg_verify__helper(
            '.+(Name or service not known).+').__check__(str(error.value))

    def test__get__auth_token_no_username(self):
        ''' Test to see if the token is expired and if so then trigger a refresh. '''
        server = "cohesity-api"

        # => Assert Test Cases are valid
        with pytest.raises(ParameterViolation) as error:
            Authentication().get_token(server)
        assert error.type == ParameterViolation
        error_list = str(error.value)

        assert error_list.index('Username is a required Parameter')

    def test__get__auth_token_no_password(self):
        ''' Test to see if the token is expired and if so then trigger a refresh. '''
        server = "cohesity-api"
        cohesity_auth = Authentication()
        cohesity_auth.username = "administrator"

        # => Assert Test Cases are valid
        with pytest.raises(ParameterViolation) as error:
            cohesity_auth.get_token(server)
        assert error.type == ParameterViolation
        error_list = str(error.value)

        assert error_list.index('Password is a required Parameter')

# => Failure Test Cases


class TestTokenRefresh(unittest.TestCase):

    def setUp(self):
        self.patcher = patch(
            global_module_util_path + '.cohesity_auth.open_url')
        self.open_url = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test__refresh__get_token(self):
        ''' Test to see if the token is expired and if so then trigger a refresh. '''

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return False. This
        # => should trigger the Code to return back to the `get_token` method.
        check_patcher = patch(
            global_module_util_path + '.cohesity_auth.Authentication.check_token')
        mock_check = check_patcher.start()
        mock_check.return_value = False

        server = "cohesity-api"
        uri = "https://" + server + "/irisservices/api/v1/public/accessTokens"

        # => Mock the URL Return Data with a new Token.
        stream = self.open_url.return_value
        stream.read.return_value = '{"accessToken": "mynewtoken","tokenType": "Bearer"}'
        stream.getcode.return_value = 201
        self.open_url.return_value = stream

        # => Create a new object of the Class::Authentication and
        # => assign the credentials including a pre-existing Token.
        cohesity_auth = Authentication()
        cohesity_auth.username = "administrator"
        cohesity_auth.password = "password"
        cohesity_auth.token = "mytoken"
        data = cohesity_auth.get_token(server)

        # => Assert Test Cases are valid
        self.assertEqual('mynewtoken', data)
        self.assertEqual(1, self.open_url.call_count)
        self.assertEqual(201, self.open_url.return_value.getcode.return_value)
        expected = call(url=uri, data=json.dumps({
                        "username": "administrator", "password": "password"}), headers={"Accept": "application/json"}, validate_certs=False)
        self.assertEqual(expected, self.open_url.call_args)

    def test__valid__get_token(self):
        ''' Test to see if the token is valid and if so then do not trigger a refresh. '''

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return True. This
        # => should trigger the Code to return back the current Token from the
        # => `get_token` method.
        check_patcher = patch(
            global_module_util_path + '.cohesity_auth.Authentication.check_token')
        mock_check = check_patcher.start()
        mock_check.return_value = True

        server = "cohesity-api"
        uri = "https://" + server + "/irisservices/api/v1/public/accessTokens"

        # => Create a new object of the Class::Authentication and
        # => assign the credentials including a pre-existing Token.
        cohesity_auth = Authentication()
        cohesity_auth.username = "administrator"
        cohesity_auth.password = "password"
        cohesity_auth.token = "mytoken"
        data = cohesity_auth.get_token(server)

        # => Assert Test Cases are valid
        self.assertEqual('mytoken', data)
        self.assertEqual(0, self.open_url.call_count)

    def test__fail__check_token(self):
        ''' Test to see if the token is expired and if so then trigger a refresh. '''

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return False. This
        # => should trigger the Code to return back to the `get_token` method.
        check_patcher = patch(
            global_module_util_path + '.cohesity_auth.open_url')
        mock_check = check_patcher.start()
        check_var = mock_check.return_value

        # =>
        check_var.read.return_value = '[{"id": "1234","clusterPartitionName": "primary"}]'
        check_var.getcode.return_value = 200
        mock_check.return_value = check_var

        server = "cohesity-api"
        uri = "https://" + server + "/irisservices/api/v1/public/nodes"

        # => Create a new object of the Class::Authentication and
        # => assign the credentials including a pre-existing Token.
        cohesity_auth = Authentication()
        cohesity_auth.username = "administrator"
        cohesity_auth.password = "password"
        cohesity_auth.token = "mytoken"
        data = cohesity_auth.check_token(server)

        # => Assert Test Cases are valid
        self.assertEqual('mytoken', data.token)
        self.assertEqual(1, mock_check.call_count)
        self.assertEqual(200, mock_check.return_value.getcode.return_value)
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer mytoken"}
        expected = call(url=uri, headers=headers, validate_certs=False)
        self.assertEqual(expected, mock_check.call_args)

    def test__invalid__check_token(self):
        ''' Test to see if the token is expired and handles the exception. '''

        server = "cohesity-api"
        uri = "https://" + server + "/irisservices/api/v1/public/nodes"

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return False. This
        # => should trigger the Code to return back to the `get_token` method.
        check_patcher = patch(
            global_module_util_path + '.cohesity_auth.open_url')
        mock_check = check_patcher.start()
        mock_check.side_effect = urllib_error.HTTPError(
            uri,
            401,
            'Unauthorized',
            {'Content-Type': 'application/json'},
            StringIO('{"message": "Some kind of failure."}')
        )

        # => Create a new object of the Class::Authentication and
        # => assign the credentials including an expired Token.
        cohesity_auth = Authentication()
        cohesity_auth.username = "administrator"
        cohesity_auth.password = "password"
        cohesity_auth.token = "mytoken"

        # => Assert Test Cases are valid
        with pytest.raises(TokenException) as error:
            cohesity_auth.check_token(server)
        assert error.type == TokenException
        assert cohesity___reg_verify__helper('.+(Unauthorized)').__check__(str(error.value))

    def test__exception__check_token(self):
        ''' Test to see if a token refresh will handle an exception. '''

        server = "cohesity-api"
        uri = "https://" + server + "/irisservices/api/v1/public/nodes"

        # => In order to properly test this behavior, we will first need to Mock out
        # => the call to the method `check_token` and force it to return False. This
        # => should trigger the Code to return back to the `get_token` method.
        check_patcher = patch(
            global_module_util_path + '.cohesity_auth.open_url')
        mock_check = check_patcher.start()
        mock_check.side_effect = urllib_error.HTTPError(
            uri,
            500,
            'Internal Server Error',
            {'Content-Type': 'application/json'},
            StringIO('Internal Server Error')
        )

        # => Create a new object of the Class::Authentication and
        # => assign the credentials including an expired Token.
        cohesity_auth = Authentication()
        cohesity_auth.username = "administrator"
        cohesity_auth.password = "password"
        cohesity_auth.token = "mytoken"

        # => Assert Test Cases are valid
        with pytest.raises(TokenException) as error:
            cohesity_auth.check_token(server)
        assert error.type == TokenException
        assert cohesity___reg_verify__helper(
            '.+(Internal Server Error)').__check__(str(error.value))
