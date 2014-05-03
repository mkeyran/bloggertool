# commands/link.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import datetime
import os
from textwrap import dedent

from dateutil.tz import tzutc

from bloggertool.str_util import qname
from .basecommand import BaseCommand


class LinkCommand(BaseCommand):
    NAME = 'link'
    HELP = "Link md with (already existing) blogspot post."
    DESCR = dedent("""\
    Link md with (already existing) blogspot post.
    """)

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('file', help="md file to link with")
        parser.add_argument('url', help="blogspot url")

    def __init__(self, args):
        self.file = args.file
        self.url = args.url

    def run(self):
        config = self.config
        post = config.post_by_path(self.file)
        if not post:
            self.log.error("MD file %s is not registered", qname(self.file))
            return

        if post.postid:
            self.log.error("Post %s already linked to published one "
                           "at remote side", qname(post.name))
            return

        srv = config.info.remote()

        rposts = srv.get_posts()
        for rpost in rposts:
            if rpost.link == self.url:
                post.link = self.url
                post.title = rpost.title
                post.postid = rpost.postid
                post.labels = rpost.labels
                post.slug = os.path.splitext(os.path.basename(self.url))[0]
                post.published = rpost.published
                post.updated = rpost.updated
                post.local_stamp = datetime.datetime.now(tzutc())
                post.changed = False
                self.log.info("Post %s connected to %s",
                              qname(post.name), post.link)
                return

        self.log.error('Has no remote blog post with link %s', self.url)
