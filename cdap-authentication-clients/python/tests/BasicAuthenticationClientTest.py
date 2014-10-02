# -*- coding: utf-8 -*-
# Copyright © 2014 Cask Data, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

try:
    import SocketServer as sserv
except ImportError:
    import socketserver as sserv

import socket
import threading
import os

from AuthDisabledHandler import AuthDisabledHandler
from EmptyUrlListHandler import EmptyUrlListHandler

try:
    import unittest2 as unittest
except ImportError:
    import unittest as unittest

from cdap_auth_client import Config
from cdap_auth_client import BasicAuthenticationClient
from AuthHandler import AuthenticationHandler
import TestConstants


class BasicAuthenticationClientTest(unittest.TestCase):
    AUTH_CONFIG_FILE = os.path.join(os.path.dirname(__file__), u"auth_config.json")
    EMPTY_USERNAME_CONFIG = os.path.join(os.path.dirname(__file__), u"empty_username_config.json")

    def setUp(self):
        self.__authentication_client = BasicAuthenticationClient()
        self.__local_test_server = SimpleTCPServer(
            (u"localhost", TestConstants.SERVER_PORT), AuthenticationHandler)
        self.__server_thread = threading.\
            Thread(target=self.__local_test_server.serve_forever)
        self.__server_thread.start()
        self.__authentication_client.\
            set_connection_info(u'localhost',
                                TestConstants.SERVER_PORT, False)
        AuthenticationHandler.AUTH_HOST = u'localhost'
        AuthenticationHandler.AUTH_PORT = TestConstants.SERVER_PORT
        self.empty_response_server = SimpleTCPServer(
            (u"localhost", TestConstants.SERVER_PORT+1), EmptyUrlListHandler)
        threading.Thread(target=self.empty_response_server.serve_forever)\
            .start()

        self.auth_disabled_server = \
            SimpleTCPServer((u"localhost", TestConstants.SERVER_PORT+2),
                            AuthDisabledHandler)
        threading.Thread(target=self.auth_disabled_server.serve_forever)\
            .start()

    def tearDown(self):
        self.__local_test_server.shutdown()
        self.__local_test_server.server_close()
        self.empty_response_server.shutdown()
        self.empty_response_server.server_close()
        self.auth_disabled_server.shutdown()
        self.auth_disabled_server.server_close()

    def test_auth_is_auth_enabled(self):
        config = Config().read_from_file(self.AUTH_CONFIG_FILE)
        self.__authentication_client.configure(config)
        assert(self.__authentication_client.is_auth_enabled())

    def test_success_get_access_token(self):
        config = Config().read_from_file(self.AUTH_CONFIG_FILE)
        self.__authentication_client.configure(config)
        access_token = self.__authentication_client.get_access_token()
        cached_access_token = self.__authentication_client.get_access_token()
        self.assertEqual(access_token, cached_access_token)
        self.assertIsNotNone(access_token)
        self.assertEqual(TestConstants.TOKEN, access_token.value)
        self.assertEqual(TestConstants.TOKEN_TYPE, access_token.token_type)
        self.assertEqual(TestConstants.TOKEN_LIFE_TIME,
                         access_token.expires_in)

    def test_not_authorization_get_access_token(self):
        self.__authentication_client.username = u"fail"
        self.__authentication_client.password = u"fail"
        self.assertRaises(Exception,
                          self.__authentication_client.get_access_token)

    def test_empty_token_get_access_token(self):
        self.__authentication_client.username =\
            TestConstants.EMPTY_TOKEN_USERNAME
        self.__authentication_client.password = TestConstants.PASSWORD
        self.assertRaises(IOError,
                          self.__authentication_client.get_access_token)

    def test_expired_token_get_access_token(self):
        AuthenticationHandler.request_counter = 0
        self.__authentication_client.username =\
            TestConstants.EXPIRED_TOKEN_USERNAME
        self.__authentication_client.password = TestConstants.PASSWORD
        access_token = self.__authentication_client.get_access_token()
        self.assertEqual(TestConstants.TOKEN, access_token.value)
        access_token = self.__authentication_client.get_access_token()
        self.assertIsNotNone(access_token)
        self.assertEqual(TestConstants.NEW_TOKEN, access_token.value)
        self.assertEqual(TestConstants.TOKEN_TYPE, access_token.token_type)

    def test_empty_username_configure(self):
        config = Config().read_from_file(self.EMPTY_USERNAME_CONFIG)
        self.assertRaises(ValueError,
                          self.__authentication_client.configure, config)

    def test_is_auth_enabled(self):
        config = Config().read_from_file(self.AUTH_CONFIG_FILE)
        self.__authentication_client.configure(config)
        self.assertTrue(self.__authentication_client.is_auth_enabled())

    def test_empty_url_list(self):
        empty_auth_client = BasicAuthenticationClient()
        empty_auth_client.set_connection_info(u'localhost',
                                              TestConstants.SERVER_PORT+1,
                                              False)
        config = Config().read_from_file(self.AUTH_CONFIG_FILE)
        empty_auth_client.configure(config)
        self.assertRaises(IOError, empty_auth_client.is_auth_enabled)

    def test_auth_disabled_is_auth_enabled(self):
        dis_auth_client = BasicAuthenticationClient()
        dis_auth_client.set_connection_info(u'localhost',
                                            TestConstants.SERVER_PORT+2,
                                            False)
        config = Config().read_from_file(self.AUTH_CONFIG_FILE)
        dis_auth_client.configure(config)
        self.assertFalse(dis_auth_client.is_auth_enabled())


class SimpleTCPServer(sserv.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

if u'__main__' == __name__:
    unittest.main()
