# commands/diff.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import difflib

from bloggertool.str_util import T, a
from .basecommand import BaseCommand


class DiffCommand(BaseCommand):
    NAME = 'diff'
    HELP = T("Show difference between local and remote post versions.")
    DESCR = T("""
        Show difference between local and remote blog post versions.
        """)
    require_interactive = True

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('file', help=T("md file to link with"))

    def __init__(self, args):
        self.file = args.file

    def run(self):
        config = self.config
        post = config.post_by_path(self.file)
        if not post:
            self.log.error(T("MD file {0!q} is not registered").format(
                self.file))
            return

        if not post.postid:
            self.log.error(a("MD file {self.file!q} has "
                             "not pushed on server yet"))
            return

        this = post.inner_html().splitlines()

        srv = config.info.remote()
        rpost = srv.get_post(post.postid)
        other = rpost.content.splitlines()

        diff = []

        for line in difflib.unified_diff(other,
                                         this,
                                         rpost.link,
                                         post.inner_html_path,
                                         ):
            diff.append(line)

        if not diff:
            self.log.info(T("No differences"))
        else:
            self.log.info(T("Difference:\n{0}").format('\n'.join(diff)))
