# commands/publish.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import os

from textwrap import dedent

from bloggertool.str_util import qname
from .basecommand import BaseCommand


class PublishCommand(BaseCommand):
    NAME = 'publish'
    HELP = "Publish post to remote."
    DESCR = dedent("""\
    Publish post to remote.
    """)
    require_interactive = True

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('file', help="md file to publish")
        parser.add_argument('--always', default=False, action='store_true',
                            help="Always regenerate html files")

    def __init__(self, args):
        self.file = args.file
        self.always = args.always

    def run(self):
        config = self.config
        post = config.post_by_path(self.file)
        if not post:
            self.log.error("MD file %s is not registered", qname(self.file))
            return

        if post.postid:
            self.log.error("%s has already published as %s [%s]",
                           qname(post.name), post.link, post.postid)
            return

        self.check_post(post)

        srv = config.info.remote()

        content = post.inner_html()
        if not post.slug:
            rpost = srv.add_post(post.title, content,
                                 labels=post.labels)
        else:
            rpost = srv.add_post(post.slug, content,
                                 labels=post.labels)
            updated_rpost = rpost.set_title(post.title)
            updated_rpost = srv.update_post(updated_rpost)

        post.postid = rpost.postid
        post.link = rpost.link
        post.slug = os.path.splitext(os.path.basename(post.link))[0]
        post.published = rpost.published
        post.updated = rpost.updated
        post.changed = False

        self.log.info("Post %s published as %s [%s]",
                      qname(post.name), post.link, post.postid)

    def check_post(self, post):
        post.refresh_html(self.always)
        # add check for non-empty title, labels, etc...
