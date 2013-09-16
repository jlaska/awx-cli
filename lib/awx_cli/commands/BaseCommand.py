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

import exceptions
import awx_cli.common as common

class BaseCommand(object):

    def __init__(self, *args, **kwargs):
        self.api = None

    def connect(self, args):
        self.api = common.connect(dict(server=args.server, username=args.username, password=args.password))

    def __call__(self, args):
        self.connect(args)
        self.run(args)

    def parse_args(self, subparsers):
        raise exceptions.NotImplementedError()

    def run(self, args):
        raise exceptions.NotImplementedError()
