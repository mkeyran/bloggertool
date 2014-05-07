# commands/label.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from textwrap import dedent

from bloggertool.str_util import T, a
from .basecommand import BaseCommand


class LabelCommand(BaseCommand):
    NAME = 'label'
    HELP = "Edit post labels."
    DESCR = dedent("""\
    Without arguments shows post labels.
    --add adds labels to post.
    --set overrides all post labels.
    --remove drops specified labels, if present.
    Labels should be single comma separated values, so use brackets:
    blog label --add "python, bloggertool"
    """)

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('files', nargs='*',
                            help="md file to operate with labels")
        labels = parser.add_mutually_exclusive_group()
        labels.add_argument('-a', '--add', help="add labels")
        labels.add_argument('-s', '--set', help="set labels")
        labels.add_argument('-r', '--rm', help="remove labels")

    def __init__(self, args):
        self.files = args.files
        self.set = args.set
        self.add = args.add
        self.rm = args.rm

    def run(self):
        config = self.config
        for fname in self.files:
            post = config.post_by_path(fname)
            if not post:
                self.log.error(a("MD file {fname!q) is not registered"))
                continue
            if self.add:
                self.do_add(post)
            elif self.set:
                self.do_set(post)
            elif self.rm:
                self.do_rm(post)

            labels = ', '.join(sorted(post.labels)) if post.labels else None
            if post.need_save:
                self.log.info(
                    a("Updated labels for post {post.name}: {labels}"))
            else:
                self.log.info(a("Labels for post {post.name!q}: {labels}"))

    def do_add(self, post):
        labels = self.labels_to_list(self.add)
        val = set(post.labels)
        for l in labels:
            val.add(l)
        post.labels = val

    def do_set(self, post):
        labels = self.labels_to_list(self.set)
        post.labels = set(labels)

    def do_rm(self, post):
        labels = self.labels_to_list(self.rm)
        val = set(post.labels)
        for l in labels:
            val.discard(l)
        post.labels = val

    def labels_to_list(self, arg):
        return [i.strip() for i in arg.split(',')]
