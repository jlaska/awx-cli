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
import inspect
import logging
import ConfigParser
import re

try:
    import argparse
except ImportError, e:
    print "Unable to import argparse.  Is python-argparse installed?"
    sys.exit(1)

try:
    import importlib
except ImportError, e:
    print "Unable to import importlib.  Is python-importlib installed?"
    sys.exit(1)

__version__ = "1.3.0"
__author__ = "Michael DeHaan"

# set up logging
logging.basicConfig(level=logging.WARN)
log = logging.getLogger()

# Enable loglevels before we've fully processed cli args
matches = re.findall(r'(-v{1,}|--verbose)\b', ' '.join(sys.argv))
num_verbose = sum([s.count('v') for s in matches])
log.setLevel(max(logging.ERROR - (num_verbose * logging.DEBUG),
                 logging.DEBUG))

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
        self.print_usage(sys.stderr)
        choose_from = ' (choose from'
        progparts = self.prog.partition(' ')
        self.exit(2, "error: %(errmsg)s\nTry '%(mainp)s help %(subp)s'"
                     " for more information.\n" %
                     {'errmsg': message.split(choose_from)[0],
                      'mainp': progparts[0],
                      'subp': progparts[2]})

class AwxHelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(AwxHelpFormatter, self).start_section(heading)

class AwxCli:
    '''
    Command-line interface to the AWX API.
    '''

    def __init__(self, args):
        self.cfg_file = None
        self.config = self.load_config()

        self.commands = self.load_commands()
        args = self.parse_args(sys.argv[1:])

        if args:
            if hasattr(args, 'function'):
                args.function(args)

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
                log.debug("load_commands() - skipping module '%s'" % module)
                continue

            log.debug("load_commands() - Looking for BaseCommand objects in '%s'" % module)

            # Attempt to import
            try:
                obj = importlib.import_module('awx_cli.commands.' + module, 'awx_cli.commands')
            except ImportError as e:
                log.error('module could not be imported: %s', e)
                continue

            # Find subclasses of BaseCommand
            for (name, cls) in inspect.getmembers(obj, inspect.isclass):
                if issubclass(cls, BaseCommand.BaseCommand):
                    log.debug("load_commands() - found '%s'" % name)
                    commands.append(cls)
                else:
                    log.debug("load_commands() - skipping class '%s'" % name)
        return commands

    def parse_args(self, argv):
        '''
        Parse command-line arguments

        Args:
        args    positional arguments (optional)
        kwargs  keyword arguments (optional)

        Returns:
        instance of argparse
        '''

        parser = AwxArgumentParser(
                    description=self.__doc__,
                    epilog='See "awx-cli help <command>" '
                           'for help on a specific command.',
                    add_help=False,
                    formatter_class=AwxHelpFormatter,)

        if hasattr(parser, '_optionals'):
            parser._optionals.title = "Options"

        # Global arguments
        parser.add_argument("--server", "-s",
                dest="server",
                default=self.config.getval('general', 'server', 'http://127.0.0.1'),
                metavar="<awx-server-url>", required=False,
                help="AWX host in the form of https://localhost/api")
        parser.add_argument("--username", "-u", dest="username",
                default=self.config.getval('general', 'username', 'admin'),
                metavar="<awx-username>", required=False,
                help="AWX username")
        parser.add_argument("--password", "-p", dest="password",
                default=self.config.getval('general', 'password', 'password'),
                metavar="<awx-password>", required=False,
                help="AWX password")
        parser.add_argument("--config", dest="config",
                default=self.cfg_file, required=False,
                metavar="<awx-config-file>",
                help="Specify alternate configuration file (default: %(default)s)")
        format_choices = ['json','text', 'yaml']
        parser.add_argument("--format", dest="format", choices=format_choices,
                default=format_choices[0], required=False,
                metavar="<format>",
                help="Specify output format")
        parser.add_argument("--verbose", "-v", dest="verbose", action="count",
                default=0, required=False,
                help="Increase verbosity")
        parser.add_argument("--help", "-h", action='store_true', help=argparse.SUPPRESS)

        options, args = parser.parse_known_args(argv)

        # Track parser_help via command name.  This allows HelpCommand to find the
        # appropriate parser print_help()
        help_by_prog = {parser.prog: parser}

        # Command-specific options
        subparsers = parser.add_subparsers(title='List of Commands',
            dest='command', metavar='<command>')
        for command in self.commands:
            obj = command()
            command_parser = obj.parse_args(subparsers)
            command_parser.set_defaults(function=obj.__call__)

            # Record base, and and sub, command parsers
            help_by_prog[command_parser.prog] = command_parser
            help_by_prog.update(obj.help_by_prog)

        # Parse those args
        if options.help or not args:
            parser.print_help()
        else:
            args = parser.parse_args(argv)

            # pass along subcommand parsers so HelpCommand is able to
            # display_help()
            remove_prefix = re.compile(r'^%s\s*' % parser.prog)
            args.help_by_prog = {remove_prefix.sub('', k):v for k,v in help_by_prog.items()}

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
