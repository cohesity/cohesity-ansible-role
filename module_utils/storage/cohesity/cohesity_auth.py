#
# cohesity_authentication
#
# Copyright (c) 2018 Cohesity Inc
# Apache License Version 2.0
#


'''
The **CohesityAuth** utils module provides the authentication token manage
for Cohesity Platforms.
'''


import json
from ansible.module_utils.urls import open_url, urllib_error
import ansible.module_utils.six.moves.urllib.error as urllib_error
from ansible.module_utils._text import to_bytes, to_native, to_text


class ParameterViolation(Exception):
    pass


class TokenException(Exception):
    pass


class Authentication(object):
    ''' Cohesity API Authentication Mechanism '''

    def __init__(self):
        self.token = ""
        self.username = ""
        self.password = ""
        self.domain = ""
        self.ssl_validation = False

    def get_token(self, server):
        '''
        Retrieve a Bearer Token

        requires:
          username
          password
          domain

        returns:
          accessToken
          privileges
          tokenType
        '''

        # => Parameter Validation Handler.  Only run this validation, if no Token exists
        errors = []
        if self.token == "":
            if self.username == "":
                errors += ["Username is a required Parameter"]
            if self.password == "":
                errors += ["Password is a required Parameter"]
            if errors:
                raise ParameterViolation(errors)

        valid_token = False
        # => The generated token is valid for 24 hours. If a request is made with an expired
        # => token, the 'Token expired' error message is returned.
        if self.token:
            valid_token = self.check_token(server)

        # => Without a valid token, we will need to make a call to request the accessToken.
        if not valid_token:
            uri = "https://" + server + "/irisservices/api/v1/public/accessTokens"
            headers = {"Accept": "application/json"}
            payload = {"username": self.username, "password": self.password}
            # => If the domain property is set, then we should include this into the Dict
            if self.domain:
                payload['domain'] = self.domain
            data = json.dumps(payload)
            try:
                # => Attempt to POST the data to the /public/accessTokens endpoint and get back
                # => a valid Token that will be placed into `self.token`.
                data = open_url(url=uri, data=data, headers=headers,
                                validate_certs=self.ssl_validation)
                response = json.loads(data.read())
                self.token = response['accessToken']
                return self.token
            except urllib_error.URLError as error:
                try:
                    # => Fixing this to deal with issues during unit testing
                    error = error.read()
                except Exception as e:
                    pass
                raise TokenException(error)
            except IOError as error:
                raise TokenException(error)
        else:
            return self.token

    def check_token(self, server):
        '''
        Verify an existing Bearer Token

        If the token is expired, then clear the stored Token and return execute
        the method `get_token` to generate a new token.

        requires:
          username
          password
          domain
          token
        '''
        # => This method will validate an existing Token if configured to see if
        # => this object needs to be refreshed.
        check_uri = "https://" + server + "/irisservices/api/v1/public/nodes"
        headers = {"Accept": "application/json",
                   "Authorization": "Bearer " + self.token}
        try:
            open_url(url=check_uri, headers=headers,
                     validate_certs=self.ssl_validation)
            return self
        except urllib_error.HTTPError as e:
            try:
                msg = json.loads(e.read())['message']
            except Exception as e:
                # => For HTTPErrors that return no JSON with a message (bad errors), we
                # => will need to handle this by setting the msg variable to some default.
                msg = "no-json-data"
            if msg == "Token expired":
                self.token = ""
                self.get_token(server)
            else:
                raise TokenException(e)


def get__cohesity_auth__token(self):
    server = self.params.get('cluster')
    validate_certs = self.params.get('validate_certs')

    auth = Authentication()
    auth.username = self.params.get('username')
    auth.password = self.params.get('password')

    if self.params.get('domain'):
        auth.domain = self.params.get('domain')

    if "\\" in auth.username:
        user_domain = auth.username.split("\\")
        auth.username = user_domain[2]
        auth.domain = user_domain[0]

    if "@" in auth.username:
        user_domain = auth.username.split("@")
        auth.username = user_domain[0]
        auth.domain = user_domain[2]

    return auth.get_token(server)
