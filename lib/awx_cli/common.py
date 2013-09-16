
# Copyright 2013, AnsibleWorks Inc.
# Michael DeHaan <michael@ansibleworks.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import exceptions
import json
import urllib2

class BaseException(exceptions.Exception):
    def __init__(self, msg):
        super(BaseException, self).__init__()
        self.msg = msg

    def __str__(self):
        return "ERROR: %s" % self.msg

class CommandNotFound(BaseException):
    pass

class Connection(object):

    def __init__(self, server):
        self.server = server

    def _request(self, endpoint, data=None, method='GET'):
        url = "%s%s" % (self.server, endpoint)
        request = urllib2.Request(url)

        if method in ['PUT', 'PATCH', 'POST', 'DELETE']:
            request.add_header('Content-type', 'application/json')
            request.get_method = lambda: method

        if data is not None:
            request.add_data(json.dumps(data))

        data = None
        try:
            response = urllib2.urlopen(request)
            data = response.read()
        except Exception, e:
            raise BaseException("%s, url: %s, data: %s, response: %s" % (str(e), url, data, e.read()))
        try:
            result = json.loads(data)
            return result
        except:
            return data

    def get(self, endpoint):
        return self._request(endpoint)

    def post(self, endpoint, data):
        return self._request(endpoint, data, method='POST')

    def put(self, endpoint, data):
        return self._request(endpoint, data, method='PUT')

    def patch(self, endpoint, data):
        return self._request(endpoint, data, method='PATCH')

    def delete(self, endpoint):
        return self._request(endpoint, method='DELETE')

def connect(server, username, password):

    # Setup urllib2 for basic password authentication.
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, server, username, password)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)

    conn = Connection(server)
    try:
        conn.get('/api/v1/')
    except Exception, e:
        raise BaseException(str(e))
    return conn

def dump(data):
    return json.dumps(data, indent=4, sort_keys=True)
