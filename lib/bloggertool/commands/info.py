# commands/info.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import os
from textwrap import dedent

from bloggertool.exceptions import ConfigError
from bloggertool.str_util import T, a
from .basecommand import BaseCommand


class InfoCommand(BaseCommand):
    NAME = 'info'
    HELP = "Display or change project info."
    DESCR = T("""
        Show project info without parameters.
        Change project settings if params specified.

        For more information about template setup see:
        $ blog help template
    """)

    FLAGS = ('email', 'blogid',
             'template', 'drop_template',
             'source_encoding')

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('--email', help="set user email")
        parser.add_argument('--blogid', help="set blog id")
        # templates
        exclusive = parser.add_mutually_exclusive_group()
        exclusive.add_argument('--template',
                               help="""
                                template path, folder part is
                                'template dir'
                                and filename part is
                                'template file'.
                                Please note: you CANNOT set dir and file
                                separetely
                                """)

        exclusive.add_argument('--drop-template', help=dedent("""\
                                drop template settings.
                                Be CAREFUL with that option"""),
                               action='store_true')

        parser.add_argument('--source-encoding',
                            help=T("""
                                set default encoding for source files"""))

    def __init__(self, args):
        self.email = args.email
        self.blogid = args.blogid
        self.template = args.template
        self.drop_template = args.drop_template
        self.source_encoding = args.source_encoding
        self.has_updates = any(
            (getattr(args, name) for name in self.FLAGS))

    def run(self):
        config = self.config

        info = config.info

        if not self.has_updates:
            out = T("""
                User info:
                    email: {info.email}
                    blogid: {info.blogid!N}
                    template:
                        dir: {info.template_dir!N}
                        file: {info.template_file!N}
                    source-encoding: {info.effective_source_encoding}
                """)(info=info)
            self.log.info(out)
        else:
            if self.email is not None:
                info.email = self.email
            if self.blogid is not None:
                info.blogid = self.blogid
            if self.drop_template:
                info.template_dir = None
                info.template_file = None
                self.log.warning("Drop template settings")
            if self.template:
                template_path = config.fs.expand_path(self.template)
                config.fs.check_existance(template_path, role="Template")
                abs_folder, fname = os.path.split(template_path)
                folder = config.fs.rel_path(abs_folder)
                if not folder or not fname:
                    raise ConfigError(a("""
                        Put template in subfolder of project dir {config.root}
                        """))
                info.template_dir = folder
                info.template_file = fname
            if self.source_encoding:
                info.source_encoding = self.source_encoding

            self.log.info("User updated")
