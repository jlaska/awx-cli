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

import inspect
import logging
import argparse
import BaseCommand
import awx_cli.common as common

class Organization_Command(BaseCommand.BaseCommand):
    '''
        Manage organizations
    '''

    def parse_args(self, subparser):
        parser = subparser.add_parser('organization',
            add_help=False,
            help=self.__doc__)
        parser.add_argument('-h',
            '--help',
            action='store_true',
            help=argparse.SUPPRESS,)
        subparser_org = parser.add_subparsers(dest='subcommand',
            title='Organization commands', metavar='<subcommand>')

        # setup any subcommand parsers
        # FIXME - define a SubCommand class instead?
        # clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        for attr in (a for a in dir(self) if a.startswith('subparse_')):
            command = attr[9:].replace('_', '-')
            sub_parser = getattr(self, attr)(subparser_org)
            # Record the print_help for the subparser
            self.help_by_prog[sub_parser.prog] = sub_parser.print_help

        return parser

    def _create_subparser(self, subparser, **kwargs):
        command = inspect.stack()[1][3].replace('subparse_','')
        logging.debug("Creating subparser for '%s'" % command)
        return subparser.add_parser(command, **kwargs)

    def subparse_list(self, subparser):
        parser = self._create_subparser(subparser,
            help='List available organizations',
            parents=[self.common_args.get('list'),])
        parser.set_defaults(func=self.run)
        return parser

    def subparse_create(self, subparser):
        parser = self._create_subparser(subparser,
            help='Create a new organization',
            parents=[self.common_args.get('create'),])
        parser.set_defaults(func=self.run)
        return parser

    def subparse_update(self, subparser):
        parser = self._create_subparser(subparser,
            help='Update an existing organization',
            parents=[self.common_args.get('update'),])
        parser.set_defaults(func=self.run)
        return parser

    def subparse_delete(self, subparser):
        parser = self._create_subparser(subparser,
            help='Delete an existing organization',
            parents=[self.common_args.get('delete'),])
        parser.set_defaults(func=self.run)
        return parser

    def run(self, args, **kwargs):
        if hasattr(self, 'run_%s' % args.subcommand):
            getattr(self, 'run_%s' % args.subcommand)(args)

    def run_list(self, args):
        data = self.api.get('/api/v1/organizations/')
        output = dict(
           results = data.pop('results')
        )
        print common.dump(output)

    def run_create(self, args):
        jdata = dict(name=args.name, description=args.desc)
        data = self.api.post('/api/v1/organizations/', jdata)
        print common.dump(data)

    def run_update(self, args):
        url = "/api/v1/organizations/%d/" % int(args.id)

        data = self.api.get(url)
        data.update(dict(name=args.name, description=args.desc))
        response = self.api.put(url, data)
        print common.dump(response)

    def run_delete(self, args):
        url = "/api/v1/organizations/%d/" % int(args.id)

        response = self.api.delete(url)
        print common.dump(response)

