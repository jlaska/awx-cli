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

import argparse
import BaseCommand
import awx_cli.common as common

class Help_Command(BaseCommand.BaseCommand):
    '''
    Display help about this program or one of its commands.
    '''
    def parse_args(self, subparser):
        parser = subparser.add_parser('help',
            add_help=False,)
        parser.add_argument('-h', '--help',
            action='store_true',
            help=argparse.SUPPRESS,)
        parser.add_argument('command',
            metavar='<subcommand>',
            nargs='*',
            help=self.__doc__)

        return parser

    def run(self, args):
        """
        Display help about this program or one of its subcommands.
        """

        if args.command:
            if isinstance(args.command, list):
                args.command = ' '.join(args.command)

            # Display subcommand-specific help
            if args.command in args.help_by_prog:
                args.help_by_prog[args.command]()
            else:
                raise Exception("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            args.help_by_prog['']()
