# commands/browse.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from textwrap import dedent
import webbrowser

from bloggertool.notify import Notifier
from bloggertool.str_util import T, a
from bloggertool.exceptions import ConfigError

from .basecommand import BaseCommand


class OpenCommand(BaseCommand):
    NAME = 'open'
    HELP = "Open browser with local html output for post."
    DESCR = dedent("""\
    Open browser with local html output for post
    """)
    require_interactive = True

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('file', help="md file to link with")
        parser.add_argument('--always', default=False, action='store_true',
                            help="Always regenerate html files")
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
        post = config.post_by_path(self.file)
        if not post:
            self.log.error("MD file '%s' is not registered", self.file)
            return

        if config.interactive is None and self.serve:
            raise ConfigError(a("""
                Cannot process --serve in interactive mode.
                Specify either --force or --no-clobber
                """))

        post.refresh_html(self.always)
        abs_path = config.fs.abs_path(post.nice_html_path)
        self.log.info("Opening '%s'", abs_path)
        webbrowser.open('file:///' + abs_path)

        if self.serve:
            notifier = Notifier(config.fs.root)
            notifier.add(config.fs.abs_path(post.file),
                         post.refresh_html, force=False)
            self.log.info(T("Run serve loop"))
            notifier.loop()


class ROpenCommand(BaseCommand):
    NAME = 'ropen'
    HELP = "Open browser with remote html output for post."
    DESCR = dedent("""\
    Open browser with remote html output for post
    """)

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('file', help="md file to link with")

    def __init__(self, args):
        self.file = args.file

    def run(self):
        config = self.config
        post = config.post_by_path(self.file)
        if not post:
            self.log.error("MD file '%s' is not registered", self.file)
            return

        self.log.info("Opening '%s'", post.link)
        webbrowser.open(post.link)
