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

import logging
import argparse
import re
import awx_cli.common as common

class BaseCommand(object):

    def __init__(self, *args, **kwargs):
        self.api = None
        self.help_by_prog = dict()
        self.common_args = self.setup_common_args()

    @property
    def name(self):
        '''
        Convert class name to something meaningful. For example:
            Organization_Command => organization
            HelpCommand => help
        '''
        return re.sub(r'(?i)[_-]?Command$', '', self.__class__.__name__.lower())

    # FIXME - this doesn't need to exist in each object ... just module-level
    def setup_common_args(self):
        '''create a dictionary of common arguments for use with subcommands'''

        args = dict()

        args['list'] = argparse.ArgumentParser(add_help=False)
        args['list'].add_argument('--filter',
            dest='filter',
            metavar='FILTER',
            action='append',
            default=[],
            required=False,
            help="Specify a key=value resource search filter (may be used multiple times)")

        args['create'] = argparse.ArgumentParser(add_help=False)
        args['create'].add_argument('--name',
            dest='name',
            metavar='NAME',
            default=None,
            required=True,
            help="Specify resource name")
        args['create'].add_argument('--desc',
            dest='desc',
            metavar='DESC',
            default=None,
            required=False,
            help="Specify resource description")

        args['update'] = argparse.ArgumentParser(add_help=False)
        edit_group = args['update'].add_mutually_exclusive_group(required=True)
        edit_group.add_argument('--id',
            dest='id',
            metavar='ID',
            default=None,
            help="Specify resource id")
        edit_group.add_argument('--name',
            dest='name',
            metavar='NAME',
            default=None,
            help="Specify resource name")

        args['update'].add_argument('--new-name',
            dest='newname',
            metavar='NEWNAME',
            default=None,
            required=False,
            help="Specify a new resource name")
        args['update'].add_argument('--desc',
            dest='desc',
            metavar='DESC',
            default=None,
            required=False,
            help="Specify resource description")

        args['delete'] = argparse.ArgumentParser(add_help=False)
        delete_group = args['delete'].add_mutually_exclusive_group(required=True)
        delete_group.add_argument('--id',
            dest='id',
            metavar='ID',
            default=None,
            help="Specify resource id")
        delete_group.add_argument('--name',
            dest='name',
            metavar='NAME',
            default=None,
            help="Specify resource name")

        return args

    def connect(self, args):
        logging.debug("Establishing connection ('%s', '%s', '****')" % (args.server, args.username))
        self.api = common.connect(args.server, args.username, args.password)

    def __call__(self, args):
        self.connect(args)
        self.run(args)

    def parse_args(self, subparsers):
        raise NotImplementedError()

    def run(self, args):
        raise NotImplementedError()
