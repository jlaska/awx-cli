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
import inspect
import logging
import argparse
import re
import awx_cli.common as common

Common_List_Args = argparse.ArgumentParser(add_help=False)
Common_List_Args.add_argument('--filter',
    dest='filter',
    metavar='FILTER',
    action='append',
    default=[],
    required=False,
    help="Specify a key=value resource search filter (may be used multiple times)")

Common_Create_Args = argparse.ArgumentParser(add_help=False)
Common_Create_Args.add_argument('--name',
    dest='name',
    metavar='NAME',
    default=None,
    required=True,
    help="Specify resource name")
Common_Create_Args.add_argument('--desc',
    dest='desc',
    metavar='DESC',
    default=None,
    required=False,
    help="Specify resource description")

Common_Update_Args = argparse.ArgumentParser(add_help=False)
mutex_group = Common_Update_Args.add_mutually_exclusive_group(required=True)
mutex_group.add_argument('--id',
    dest='id',
    metavar='ID',
    default=None,
    help="Specify resource id")
mutex_group.add_argument('--name',
    dest='name',
    metavar='NAME',
    default=None,
    help="Specify resource name")

Common_Update_Args.add_argument('--new-name',
    dest='newname',
    metavar='NEWNAME',
    default=None,
    required=False,
    help="Specify a new resource name")
Common_Update_Args.add_argument('--desc',
    dest='desc',
    metavar='DESC',
    default=None,
    required=False,
    help="Specify resource description")

Common_Delete_Args = argparse.ArgumentParser(add_help=False)
mutex_group = Common_Delete_Args.add_mutually_exclusive_group(required=True)
mutex_group.add_argument('--id',
    dest='id',
    metavar='ID',
    default=None,
    help="Specify resource id")
mutex_group.add_argument('--name',
    dest='name',
    metavar='NAME',
    default=None,
    help="Specify resource name")

class BaseCommand(object):

    def __init__(self, *args, **kwargs):
        self.api = None
        self.help_by_prog = dict()

    def load_subcommands(self):
        '''
        Return a list of classes that are a subclass of BaseCommand.SubCommand
        '''
        #return [cls for (name,cls) in inspect.getmembers(sys.modules[self.__module__], lambda member: inspect.isclass(member) and issubclass(member, SubCommand))]
        return [cls for (name,cls) in inspect.getmembers(self, lambda member: inspect.isclass(member) and issubclass(member, SubCommand))]

    def connect(self, args):
        logging.debug("Establishing connection ('%s', '%s', '****')" % (args.server, args.username))
        self.api = common.connect(args.server, args.username, args.password)

    def __call__(self, args):
        self.connect(args)
        self.run(args)

    def parse_args(self, subparsers):
        raise NotImplementedError()

    def run(self, args, **kwargs):
        full_cmd = '%s %s' % (args.command, args.subcommand)
        if args.help_by_prog.has_key(full_cmd):
            # Reference base object
            obj = args.help_by_prog[full_cmd].__parent__
            # Share the existing connection
            obj.api = self.api
            # Run the handler
            obj.run(args)

class SubCommand(object):
    '''fixme'''
    def __init__(self, *args, **kwargs):
        self.parser = None

    def parse_args(self, subparser, command, **kwargs):
        self.parser = subparser.add_parser(command, **kwargs)
        self.parser.set_defaults(function=self.run)
        return self.parser

    def run(self, args):
        raise NotImplementedError()

class List_SubCommand(SubCommand):
    resource = 'UNDEFINED'

    def parse_args(self, subparser, **kwargs):
        return super(List_SubCommand, self).parse_args(subparser, 'list',
            help='List available %s' % self.resource,
            parents=[Common_List_Args,])

    def run(self, args):
        data = self.api.get('/api/v1/%s/' % self.resource)
        output = dict(
           results = data.pop('results')
        )
        print common.dump(output)

class Create_SubCommand(SubCommand):
    resource = 'UNDEFINED'
    def parse_args(self, subparser, **kwargs):
        return super(Create_SubCommand, self).parse_args(subparser, 'create',
            help='Create a new %s' % self.resource,
            parents=[Common_Create_Args,])

    def run(self, args):
        jdata = dict(name=args.name, description=args.desc)
        data = self.api.post('/api/v1/%s/' % self.resource, jdata)
        print common.dump(data)

class Update_SubCommand(SubCommand):
    resource = 'UNDEFINED'
    def parse_args(self, subparser, **kwargs):
        return super(Update_SubCommand, self).parse_args(subparser, 'update',
            help='Update an existing %s' % self.resource,
            parents=[Common_Update_Args,])

    def run(self, args):
        url = "/api/v1/%s/%d/" % (self.resource, int(args.id))
        data = self.api.get(url)
        data.update(dict(name=args.name, description=args.desc))
        response = self.api.put(url, data)
        print common.dump(response)

class Delete_SubCommand(SubCommand):
    resource = 'UNDEFINED'
    def parse_args(self, subparser, **kwargs):
        return super(Delete_SubCommand, self).parse_args(subparser, 'delete',
            help='Delete an existing %s' % self.resource,
            parents=[Common_Delete_Args,])

    def run(self, args):
        url = "/api/v1/%s/%d/" % (self.resource, int(args.id))
        response = self.api.delete(url)
        print common.dump(response)

