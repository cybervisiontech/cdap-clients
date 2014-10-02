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
    from BaseHTTPServer import BaseHTTPRequestHandler as brh
except ImportError:
    from http.server import SimpleHTTPRequestHandler as brh
try:
    import httplib as hl
except ImportError:
    import http.client as hl

import base64
import json
import TestConstants


class AuthenticationHandler(brh):
    AUTH_PORT = None
    AUTH_HOST = None
    request_counter = 0

    @property
    def auth_host(self):
        return self.AUTH_HOST

    @auth_host.setter
    def auth_host(self, auth_host):
        self.AUTH_HOST = auth_host

    @property
    def auth_port(self):
        return self.AUTH_PORT

    @auth_port.setter
    def auth_port(self, auth_port):
        self.AUTH_PORT = auth_port

    def do_GET(self):
        if 'token' not in self.path:
            status_code = hl.UNAUTHORIZED
            auth_uri = u'{"auth_uri":["http://%s:%d/token"]}' %\
                       (self.AUTH_HOST, self.AUTH_PORT)
            self.send_response(status_code)
            self.send_header(u"Content-type", u"application/json")
            self.end_headers()
            self.wfile.write(auth_uri.encode('utf-8'))

        else:
            AuthenticationHandler.request_counter += 1

            auth_header_val = self.headers[u'Authorization']
            if auth_header_val:
                auth_header_val = auth_header_val.replace('Basic ', '')
                credentials_str = base64.b64decode(auth_header_val)\
                    .decode('utf-8')
                credentials = credentials_str.split(':', 1)
                username = credentials[0]
                password = credentials[1]
                if TestConstants.USERNAME == username\
                        and TestConstants.PASSWORD == password:
                    status_code = hl.OK
                    self.send_response(status_code)
                    self.send_header(u"Content-type", u"application/json")
                    self.end_headers()
                    self.wfile.write(self.create_resp_body
                                     (TestConstants.TOKEN,
                                      TestConstants.TOKEN_TYPE,
                                      TestConstants.TOKEN_LIFE_TIME)
                                     .encode('utf-8'))
                elif TestConstants.EMPTY_TOKEN_USERNAME == username:
                    status_code = hl.OK
                    self.send_response(status_code)
                    self.send_header(u"Content-type", u"application/json")
                    self.end_headers()
                    self.wfile.write(
                        self.create_resp_body('',
                                              TestConstants.TOKEN_TYPE,
                                              TestConstants.TOKEN_LIFE_TIME)
                        .encode('utf-8'))

                elif TestConstants.EXPIRED_TOKEN_USERNAME == username:
                    if self.request_counter == 1:
                        resp = self.create_resp_body(
                            TestConstants.TOKEN, TestConstants.TOKEN_TYPE, 5)
                    else:
                        resp = self.create_resp_body(
                            TestConstants.NEW_TOKEN,
                            TestConstants.TOKEN_TYPE,
                            TestConstants.TOKEN_LIFE_TIME)

                    status_code = hl.OK
                    self.send_response(status_code)
                    self.send_header(u"Content-type", u"application/json")
                    self.end_headers()
                    self.wfile.write(resp.encode('utf-8'))

                else:
                    status_code = hl.UNAUTHORIZED
                    self.send_response(status_code)
                    self.send_header(u"Content-type", u"application/json")
                    self.end_headers()
            else:
                status_code = hl.BAD_REQUEST
                self.send_response(status_code)
                self.send_header(u"Content-type", u"application/json")
                self.end_headers()

    @staticmethod
    def create_resp_body(value, type, expires_in):
        return json.dumps({u'access_token': value, u'token_type': type,
                           u'expires_in': expires_in})
