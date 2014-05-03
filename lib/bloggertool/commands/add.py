# commands/add.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from textwrap import dedent

from .basecommand import BaseCommand
from bloggertool.str_util import qname


class AddCommand(BaseCommand):
    NAME = 'add'
    HELP = "Add md file"
    DESCR = dedent("""\
    Add md file to project
    """)

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('files', nargs='+', help="filename to add")

    def __init__(self, args):
        self.files = args.files

    def run(self):
        config = self.config

        for fname in self.files:
            #fname = os.path.abspath(fname)
            post = config.post_by_path(fname, no_existance_check=True)
            if post is not None:
                self.log.warning("Skip already registered file %s",
                                 qname(fname))
                continue

            abs_path = config.fs.expand_path(fname)
            rel_path = config.fs.rel_path(abs_path)

            if not rel_path.endswith('.md'):
                self.log.error("Cannot operate with non-md files")
                continue

            name = config.fs.replace_ext(rel_path, '')

            self.log.info("Add %s -> %s", qname(name), qname(rel_path))

            config.add(name, rel_path)
