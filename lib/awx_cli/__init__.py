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

import sys
import argparse

# TODO: add a plugin loader sometime
from commands.VersionCommand import VersionCommand
from commands.JobLaunchCommand import JobLaunchCommand

__version__ = "1.3.0"
__author__ = "Michael DeHaan"

class AwxCli:

    def __init__(self, args):
        """ constructs the top level control system for the AWX CLI """

        self.commands = [
            VersionCommand,
            JobLaunchCommand,
        ]

        args = self.parse_args(args)

        if not hasattr(args, 'function'):
            raise common.CommandNotFound("unknown command: %s" % first)
        args.function()(args)

    def parse_args(self, args, **kwargs):

        parser = argparse.ArgumentParser(usage='%(prog)s <options> [command] '
                '<command-options>')

        if hasattr(parser, '_optionals'):
            parser._optionals.title = "Options"

        # Global arguments
        parser.add_argument("-s", "--server", dest="server",
                default=None, metavar="SERVER", required=True,
                help="AWX host in the form of https://localhost/api")
        parser.add_argument("-u", "--username", dest="username",
                default=None, metavar="USERNAME", required=True,
                help="AWX username")
        parser.add_argument("-p", "--password", dest="password",
                default=None, metavar="PASSWORD", required=True,
                help="AWX password")

        # Command-specific options
        subparsers = parser.add_subparsers(title='List of Commands',
            dest='command', description='', metavar='')
        for cmd in self.commands:
            sb = cmd().parse_args(subparsers)
            sb.set_defaults(function=cmd)

        # Parse those args
        args = parser.parse_args()

        if args.command is None or args.command == '':
            parser.error("No command provided")

        # TODO: Validate command arguments

        return args
