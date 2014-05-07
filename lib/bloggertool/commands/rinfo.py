# commands/rinfo.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from textwrap import dedent

from bloggertool.exceptions import ConfigError
from .basecommand import BaseCommand


class RInfoCommand(BaseCommand):
    NAME = 'rinfo'
    HELP = "Display info for remote site."
    DESCR = dedent("""\
    Display info for remote site.
    """)

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('--reset_credentials', default=False,
                            action='store_true',
                            help="reset stored credentials")

    def __init__(self, args):
        self.reset_credentials = args.reset_credentials

    def run(self):
        config = self.config

        info = config.info

        srv = info.remote(self.reset_credentials)

        blogs = srv.get_blogs()
        out = []
        for blog in blogs:
            out.append("    [%s->%s] %s" % (blog.blogid, blog.url, blog.title))
        self.log.info("Blogs of user '%s'\n%s", blogs.title,
                      '\n'.join(out))
