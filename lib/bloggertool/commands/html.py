# commands/html.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from bloggertool.exceptions import ConfigError
from bloggertool.notify import Notifier
from bloggertool.str_util import T, a
from .basecommand import BaseCommand


class HtmlCommand(BaseCommand):
    NAME = 'html'
    HELP = T("Generate html output for md files.")
    DESCR = T("""
    Without arguments updates only htmls older then source md
    for all registered posts.
    """)

    require_interactive = True

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('file', nargs='?',
                            help="md file to generate html")
        parser.add_argument('--always', default=False, action='store_true',
                            help=T("Always regenerate html files"))
        parser.add_argument('--serve', default=False, action='store_true',
                            help=T("""
                                Loop forever waiting for source file change,
                                updating html as reaction
                            """))

    def __init__(self, args):
        self.file = args.file
        self.always = args.always
        self.serve = args.serve

    def run(self):
        config = self.config
        if not config:
            raise ConfigError(T("Config has no any registered posts"))

        if config.interactive is None and self.serve:
            raise ConfigError(a("""
                Cannot process --serve in interactive mode.
                Specify either --force or --no-clobber
                """))

        post = self.config.post_by_path(self.file)

        if post is None:
            raise ConfigError(a("Not registered file {self.file!q}"))

        posts = [post]
        # XXX add support for multiple posts. Should follow 'ls' schema

        for post in posts:
            if not post.refresh_html(self.always):
                self.log.info(a("Skip fresh {post.name!q}"))

        if self.serve:
            notifier = Notifier(config.fs.root)
            for post in posts:
                notifier.add(config.fs.abs_path(post.file),
                             post.refresh_html, force=False)
            self.log.info(T("Run serve loop"))
            notifier.loop()
