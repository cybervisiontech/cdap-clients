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

import json
from io import open


class Config(object):

    def __init__(self):
        self.__username = None
        self.__password = None
        self.__security_ssl_cert_check = None

    @property
    def security_auth_client_username(self):
        return self.__username

    @security_auth_client_username.setter
    def security_auth_client_username(self, username):
        self.__username = username

    @property
    def security_auth_client_password(self):
        return self.__password

    @security_auth_client_password.setter
    def security_auth_client_password(self, password):
        self.__password = password

    @property
    def security_ssl_cert_check(self):
        return self.__security_ssl_cert_check

    @security_ssl_cert_check.setter
    def security_ssl_cert_check(self, security_ssl_cert_check):
        self.__security_ssl_cert_check = security_ssl_cert_check

    def read_from_file(self, file):
        new_config = Config()
        json_config = None
        with open(file) as configFile:
            json_config = json.loads(configFile.read())

        new_config.__username = json_config[u'security_auth_client_username']
        new_config.__password = json_config[u'security_auth_client_password']
        if json_config[u'security_ssl_cert_check'] is "true":
            new_config.__security_ssl_cert_check = True
        else:
            new_config.__security_ssl_cert_check = False
        return new_config
