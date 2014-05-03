# commands/rinfo.py
# Copyright (C) 2011-2012 Andrew Svetlov
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
        pass

    def __init__(self, args):
        #self.email = args.email
        pass

    def run(self):
        config = self.config

        info = config.info

        if not info.email:
            raise ConfigError("Set user email first")

        srv = info.remote()

        blogs = srv.get_blogs()
        out = []
        for blog in blogs:
            out.append("    [%s] %s" % (blog.blogid, blog.title))
        self.log.info("Blogs of user '%s'\n%s", blogs.title,
                      '\n'.join(out))
