# commands/push.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from textwrap import dedent

from .basecommand import BaseCommand


class PushCommand(BaseCommand):
    NAME = 'push'
    HELP = "Push html to remote server."
    DESCR = dedent("""\
    Push html to remote server.
    """)
    require_interactive = True

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('file', help="md file to link with")
        parser.add_argument('--always', default=False, action='store_true',
                            help="Always regenerate html files")

    def __init__(self, args):
        self.file = args.file
        self.always = args.always

    def run(self):
        config = self.config
        post = config.post_by_path(self.file)
        if not post:
            self.log.error("MD file '%s' is not registered", self.file)
            return

        if not post.postid:
            self.log.error("MD file '%s' has not pushed on server yet",
                           self.file)
            return

        post.refresh_html(self.always)

        srv = config.info.remote()

        rpost = srv.get_post(post.postid)

        this = post.inner_html()

        updated_rpost = rpost.set_content(this)
        updated_rpost = updated_rpost.set_title(post.title)
        updated_rpost = updated_rpost.set_labels(post.labels)
        #updated_rpost = updated_rpost.set_link(post.link)

        srv.update_post(updated_rpost)
        self.log.info("Post %s updated", post.name)
        post.published = rpost.published
        post.updated = rpost.updated
        post.changed = False
