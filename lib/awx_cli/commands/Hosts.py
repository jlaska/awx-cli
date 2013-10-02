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

import sys
import argparse
import BaseCommand

api_base = '/hosts'

class Host_Command(BaseCommand.BaseCommand):
    '''
        Manage hosts
    '''

    class Host_List_SubCommand(BaseCommand.List_SubCommand):
        resource = 'hosts'

    class Host_Create_SubCommand(BaseCommand.Create_SubCommand):
        resource = 'hosts'

    class Host_Update_SubCommand(BaseCommand.Update_SubCommand):
        resource = 'hosts'

    class Host_Delete_SubCommand(BaseCommand.Delete_SubCommand):
        resource = 'hosts'

    def parse_args(self, subparser):

        parser = subparser.add_parser('host',
            add_help=False,
            help=self.__doc__)
        parser.add_argument('-h',
            '--help',
            action='store_true',
            help=argparse.SUPPRESS,)
        subparser_org = parser.add_subparsers(dest='subcommand',
            title='Host commands', metavar='<subcommand>')

        # Load any subcommands
        for cls in self.load_subcommands():
            obj = cls()
            obj.parse_args(subparser_org)
            obj.parser.__parent__ = obj
            self.help_by_prog[obj.parser.prog] = obj.parser

        return parser
