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
import os
import argparse
import importlib
import inspect
import logging

# set up logging
logging.basicConfig(level=logging.WARN)
log = logging.getLogger()

__version__ = "1.3.0"
__author__ = "Michael DeHaan"

class AwxCli:

    def __init__(self, args):
        """ constructs the top level control system for the AWX CLI """

        self.commands = self.loadCommands()

        args = self.parse_args(args)

        if not hasattr(args, 'function'):
            raise common.CommandNotFound("unknown command: %s" % first)
        args.function()(args)

    def loadCommands(self):
        '''
        Find and return a list of subclasses of commands.BaseCommand

        Args:

        Returns:
        list of classes

        Raises:
        ImportError
        '''

        commands = list()

        # Import BaseCommand so we know where to look
        BaseCommand = importlib.import_module('awx_cli.commands.BaseCommand')
        module_dir = os.path.dirname(BaseCommand.__file__)

        # Gather other .py modules in the same directory as BaseCommand.py
        modules = [os.path.splitext(f)[0] for f in os.listdir(module_dir)
            if f.endswith('.py')]

        for module in modules:

            if module in ['BaseCommand', '__init__']:
                continue

            # Attempt to import
            try:
                obj = importlib.import_module('awx_cli.commands.' + module, 'awx_cli.commands')
            except ImportError as e:
                log.error('module could not be imported: %s', e)
                continue

            # Find subclasses of BaseCommand
            for (name, cls) in inspect.getmembers(obj, inspect.isclass):
                if issubclass(cls, BaseCommand.BaseCommand):
                    commands.append(cls)
        return commands

    def parse_args(self, *args, **kwargs):
        '''
        Parse command-line arguments

        Args:
        args    positional arguments (optional)
        kwargs  keyword arguments (optional)

        Returns:
        instance of argparse
        '''

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
