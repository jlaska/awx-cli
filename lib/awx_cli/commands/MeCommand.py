# Copyright 2013, AnsibleWorks Inc.
# James Laska <jlaska@ansibleworks.com>
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

import BaseCommand
import awx_cli.common as common

class MeCommand(BaseCommand.BaseCommand):

    def parse_args(self, subparsers):
        p = subparsers.add_parser('me',
            help='Display information about currently logged in user')
        return p

    def run(self, args):

        data = self.api.get('/api/v1/me')
        output = dict(
           results = data.pop('results')
        )
        print common.dump(output)

