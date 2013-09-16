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

class Organization_List(BaseCommand.BaseCommand):

    def parse_args(self, subparsers):
        p = subparsers.add_parser('list_organizations',
            help='List available organizations')
        return p

    def run(self, args):

        data = self.api.get('/api/v1/organizations/')
        output = dict(
           results = data.pop('results')
        )
        print common.dump(output)

class Organization_Create(BaseCommand.BaseCommand):

    def parse_args(self, subparsers):
        p = subparsers.add_parser('create_organization',
            parents=[BaseCommand.arg_name, BaseCommand.arg_desc],
            help='Create an organization')
        return p

    def run(self, args):

        jdata = dict(name=args.name, description=args.desc)
        data = self.api.post('/api/v1/organizations/', jdata)
        print common.dump(data)

class Organization_Update(BaseCommand.BaseCommand):

    def parse_args(self, subparsers):
        p = subparsers.add_parser('update_organization',
            parents=[BaseCommand.arg_id,
                BaseCommand.arg_name,
                BaseCommand.arg_desc],
            help='Update an organization')
        return p

    def run(self, args):
        url = "/api/v1/organizations/%d/" % int(args.id)

        data = self.api.get(url)
        data.update(dict(name=args.name, description=args.desc))
        response = self.api.put(url, data)
        print common.dump(response)

class Organization_Delete(BaseCommand.BaseCommand):

    def parse_args(self, subparsers):
        p = subparsers.add_parser('delete_organization',
            parents=[BaseCommand.arg_id,],
            help='Delete an existing organization')
        return p

    def run(self, args):
        url = "/api/v1/organizations/%d/" % int(args.id)

        response = self.api.delete(url)
        print common.dump(response)

