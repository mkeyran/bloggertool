# commands/ls.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import itertools

from textwrap import dedent

from .basecommand import BaseCommand


class LsCommand(BaseCommand):
    NAME = 'ls'
    HELP = 'Display list of registered posts.'
    DESCR = dedent("""\
    Without arguments shows all posts starting from current folder.
    Positional argument if present can be relative or absolute folder path
    to use as start folder.

    Values / and ~ has special meaning - both points to root of local
    project.
    """)

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('root', nargs='?', default='.',
                            help="folder to display")
        parser.add_argument('-l', '--long', default=False,
                            action='store_true',
                            help="long output format")

    def __init__(self, args):
        self.root = args.root
        self.long = args.long

    def run(self):
        config = self.config
        root = config.fs.expand_path(self.root)
        rel_root = config.fs.rel_path(root)

        def good(post):
            return post.file.startswith(rel_root)

        out = []
        filtered = itertools.ifilter(good, config)
        for post in sorted(filtered, key=lambda p: p.name):
            out.append(post.info_list(self.long))

        if not out:
            self.log.info("No posts")
        else:
            self.log.info("Posts:\n%s", '\n'.join(out))
