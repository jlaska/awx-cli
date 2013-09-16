
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

import datetime
import exceptions
import os
import getpass
import json
import urllib2
import ConfigParser

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

def get_config_parser():
    parser = ConfigParser.ConfigParser()
    path1 = os.path.expanduser(os.environ.get('AWX_CLI_CONFIG', "~/.awx_cli.cfg"))
    path2 = "/etc/awx/awx_cli.cfg"

    if os.path.exists(path1):
        parser.read(path1)
    elif os.path.exists(path2):
        parser.read(path2)
    else:
        return None
    return parser

def get_config_value(p, section, key, default):
    try:
        return p.get(section, key)
    except:
        return default

def get_config_default(p, key, defaults, section='general'):
    return get_config_value(p, section, key, defaults[key])

def connect(options):
    
    config_file = get_config_parser()

    if type(options) != dict:
        options = dict(
            username = options.username,
            password = options.password,
            server   = options.server
        )

    defaults = dict(
        username = "admin",
        password = "password",
        server   = "http://127.0.0.1"
    )


    if config_file:
        defaults['username'] = get_config_default(
            config_file, 'username', defaults
        )
        defaults['password'] = get_config_default(
            config_file, 'password', defaults
        )
        defaults['server'] = get_config_default(
            config_file, 'server', defaults
        )

    username = options.get("username", defaults["username"])
    password = options.get("password", defaults["password"])
    server   = options.get("server",   defaults["server"])
    if username is None:
        username = defaults['username']
    if password is None:
        password = defaults['password']
    if server is None:
        server = defaults['server']

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
