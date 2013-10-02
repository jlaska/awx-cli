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

class Job_Command(BaseCommand.BaseCommand):
    '''
        Manage jobs
    '''

    api_base = '/jobs'

    class Job_List_SubCommand(BaseCommand.List_SubCommand):
        resource = 'jobs'

    class Job_Launch_SubCommand(BaseCommand.SubCommand):
        resource = 'jobs'
        def parse_args(self, subparser, **kwargs):
            p = BaseCommand.SubCommand.parse_args(self, subparser, 'launch',
                help='Launch a job template')
            p.add_argument('--template', default=None, required=True,
                type=str, help="Specify job template id")
            p.add_argument('--sync', default=False,
                type=bool, help="Indicate whether to wait for job completion (default: %(default)s)")
            return p

        def run(self, args):
            # Lookup template by name
            if not args.template.isdigit():
                jt_url = "/api/v1/job_templates/?%s" % \
                    urllib.urlencode(dict(name__icontains=args.template))
                data = self.api.get(jt_url)
                if data.get('count', 0) == 0:
                    raise common.BaseException("No templates found matching: %s" % args.template)
                elif data.get('count', 0) > 1:
                    raise common.BaseException("Multiple templates match provided string: %s" % args.template)
                args.template = data['results'][0].get('id')

            # get the job template
            jt_url = "/api/v1/job_templates/%d/" % int(args.template)
            data = self.api.get(jt_url)
            id = data.pop('id')

            # add some more info needed to start the job
            # NOTE: a URL to launch job templates directly
            # may be added later, but this is basically a copy of the job template
            # data to the jobs resource, which is also fine.

            now = str(datetime.datetime.now())
            data.update(dict(
                name = 'cli job invocation started at %s' % now,
                verbosity = 0,
            ))

            # post a new job

            jt_jobs_url = "%sjobs/" % jt_url
            job_result = self.api.post(jt_jobs_url, data)

            # get the parameters needed to start the job (if any)
            # prompt for values unless given on command line (FIXME)

            print "URL=%s" % jt_jobs_url

            job_id = job_result['id']
            job_start_url = "/api/v1/jobs/%d/start/" % job_id
            job_start_info = self.api.get(job_start_url)
            start_data = {}
            for password in job_start_info.get('passwords_needed_to_start', []):
                value = getpass.getpass('%s: ' % password)
                start_data[password] = value

            # start the job 
            job_start_result = self.api.post(job_start_url, start_data)
            print common.dump(job_start_result) 

            # TODO: optional status polling (FIXME)
            if args.sync:
                raise NotImplementedError("Status polling is not yet implemented")

    def parse_args(self, subparser):

        parser = subparser.add_parser('job',
            add_help=False,
            help=self.__doc__)
        parser.add_argument('-h',
            '--help',
            action='store_true',
            help=argparse.SUPPRESS,)
        subparser_org = parser.add_subparsers(dest='subcommand',
            title='Job commands', metavar='<subcommand>')

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
