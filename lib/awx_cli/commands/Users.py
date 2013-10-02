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
import logging
import argparse
import BaseCommand

class User_Command(BaseCommand.BaseCommand):
    '''
        Manage users
    '''

    api_base = '/users'

    class User_List_SubCommand(BaseCommand.List_SubCommand):
        resource = 'users'

    class User_Create_SubCommand(BaseCommand.Create_SubCommand):
        resource = 'users'

    class User_Update_SubCommand(BaseCommand.Update_SubCommand):
        resource = 'users'

    class User_Delete_SubCommand(BaseCommand.Delete_SubCommand):
        resource = 'users'

    def parse_args(self, subparser):

        parser = subparser.add_parser('user',
            add_help=False,
            help=self.__doc__)
        parser.add_argument('-h',
            '--help',
            action='store_true',
            help=argparse.SUPPRESS,)
        subparser_org = parser.add_subparsers(dest='subcommand',
            title='User commands', metavar='<subcommand>')

        # Load any subcommands
        for cls in self.load_subcommands():
            logging.debug("BEFORE: cls.__bases__ = %s" % cls.__bases__)
            #cls.__bases__ = (cls.__bases__, self.__class__
            #logging.debug("AFTER: cls.__bases__ = %s" % cls.__bases__)
            obj = cls()
            obj.parse_args(subparser_org)
            # obj.__class__ = cls.__class__(cls.__name__ + "WithExtraBase", (cls, ExtraBase), {})
            obj.parser.__parent__ = obj
            self.help_by_prog[obj.parser.prog] = obj.parser

        return parser
