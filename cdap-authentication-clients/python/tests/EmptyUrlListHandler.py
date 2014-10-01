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


class EmptyUrlListHandler(brh):

    def do_GET(self):
        status_code = hl.UNAUTHORIZED
        auth_uri = u'{"auth_uri":[]}'
        self.send_response(status_code)
        self.send_header(u"Content-type", u"application/json")
        self.end_headers()
        self.wfile.write(auth_uri.encode('utf-8'))
