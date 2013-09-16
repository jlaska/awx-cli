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

import os
import os.path
import sys
import argparse
import importlib
import inspect
import logging
import ConfigParser
import re

__version__ = "1.3.0"
__author__ = "Michael DeHaan"

# set up logging
logging.basicConfig(level=logging.WARN)
log = logging.getLogger()

# Sub-class ConfigParser to add local tweaks
class AwxCliConfigParser(ConfigParser.SafeConfigParser):
    # Add support for list-style options
    def getlist(self, section, option):
        return re.split(r'[,\s]+', self.get(section, option))

    def getval(self, section, option, default):
        try:
            return self.get(section, option)
        except:
            return default

class AwxArgumentParser(argparse.ArgumentParser):
    '''
    Subclass ArgumentParser so we can emit print_help() when no positional
    arguments are supplied.
    '''
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

class AwxCli:

    def __init__(self, args):
        """ constructs theself. top level control system for the AWX CLI """

        self.cfg_file = None
        self.config = self.load_config()

        self.commands = self.load_commands()
        args = self.parse_args(args)

        if not hasattr(args, 'function'):
            raise common.CommandNotFound("unknown command: %s" % first)
        args.function()(args)

    def load_config(self):

        # Determine if an alternate .cfg file was requested via --config.
        # Configuration is loaded prior to inspection of command-line options.
        # NOTE: Despite being coded properly, this won't work when calling:
        #  $ awx-cli --config <foo>.
        # But will work using ...
        #  $ awx-cli --config=<foo>.
        # There appears to be some pre-parsing in the former case.
        for i,arg in enumerate(sys.argv):
            if re.search(r'^--config\b', arg):
                try:
                    self.cfg_file = [sys.argv[i].split('=',1)[1]]
                except IndexError:
                    if len(sys.argv) > i+1:
                        self.cfg_file = [sys.argv[i+1]]
                break

        # Determine if an alternate .cfg file was requested via AWX_CLI_CONFIG
        # environment variable
        if self.cfg_file is None:
            local_cfg_file = os.path.expanduser(os.environ.get('AWX_CLI_CONFIG',
                '~/.awx-cli.cfg'))
            if os.path.isfile(local_cfg_file):
                self.cfg_file = local_cfg_file

        # Default to system-wide config file
        if self.cfg_file is None:
            self.cfg_file = '/etc/awx/awx-cli.cfg'

        # Read configuration, fail if missing
        awx_config = AwxCliConfigParser()
        if len(awx_config.read(self.cfg_file)) == 0:
            logging.debug("No configuration file loaded")

        return awx_config

    def load_commands(self):
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

        parser = AwxArgumentParser(usage='%(prog)s <options> [command] '
                    '<command-options>')

        if hasattr(parser, '_optionals'):
            parser._optionals.title = "Options"

        # Global arguments
        parser.add_argument("-s", "--server", dest="server",
                default=self.config.getval('general', 'server', 'http://127.0.0.1'),
                metavar="SERVER", required=False,
                help="AWX host in the form of https://localhost/api")
        parser.add_argument("-u", "--username", dest="username",
                default=self.config.getval('general', 'username', 'admin'),
                metavar="USERNAME", required=False,
                help="AWX username")
        parser.add_argument("-p", "--password", dest="password",
                default=self.config.getval('general', 'password', 'password'),
                metavar="PASSWORD", required=False,
                help="AWX password")
        parser.add_argument("--config", dest="config",
                default=self.cfg_file, required=False,
                help="Specify alternate configuration file (default: %(default)s)")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count",
                default=0, required=False,
                help="Increase verbosity")

        # Command-specific options
        subparsers = parser.add_subparsers(title='List of Commands',
            dest='command', description='', metavar='')
        for cmd in self.commands:
            sb = cmd().parse_args(subparsers)
            sb.set_defaults(function=cmd)

        # TODO - sort subparsers alphabetically

        # Parse those args
        args = parser.parse_args()

        # Validate global arguments
        for field in ['username', 'password', 'server']:
            if getattr(args, field) is None:
                parser.error("Missing required --%s parameter" % field)

        if args.command is None or args.command == '':
            parser.error("No command provided")

        # Adjust loglevel
        log.setLevel(max(logging.ERROR - (args.verbose * logging.DEBUG),
                         logging.DEBUG))

        # TODO: Validate command arguments

        return args
