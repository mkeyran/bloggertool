# commands/post.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import datetime

from dateutil.tz import tzutc

from bloggertool.str_util import T, a
from .basecommand import BaseCommand


class ShowCommand(BaseCommand):
    NAME = 'show'
    HELP = "Display or change meta information for post."
    DESCR = T("""
        Display or change meta information for post.
    """)
    require_interactive = True

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('file', help="md file")
        parser.add_argument('--slug',
                            help="set slug (used for generated post link "
                            "in post publishing")
        parser.add_argument('--title',
                            help="set post title")

    def __init__(self, args):
        self.file = args.file
        self.slug = args.slug
        self.title = args.title

    def run(self):
        config = self.config
        post = config.post_by_path(self.file)
        if not post:
            self.log.error(a("MD file {self.file!q} is not registered"))
            return

        if not self.slug and not self.title:
            self.log.info("Post %s", post.info_list(True))
            return

        if self.slug:
            if post.postid:
                self.log.error(a("""
                    Post {post.name!q} has already published,
                    cannot change slug
                    """))
            else:
                post.overwrite_attr('slug', self.slug.strip())

        if self.title:
            post.overwrite_attr('title', self.title.strip())

        if post.need_save:
            self.log.info(a("Post {post.name!q} updated."))
            post.local_stamp = datetime.datetime.now(tzutc())
