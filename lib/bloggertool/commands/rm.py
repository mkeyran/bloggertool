# commands/rm.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from textwrap import dedent

from bloggertool.exceptions import FileNotFoundError
from bloggertool.str_util import qname
from .basecommand import BaseCommand


class RmCommand(BaseCommand):
    NAME = 'rm'
    HELP = "Remove md file from blogspot project database."
    DESCR = dedent("""\
    Doesn't remove file itself.
    Doesn't remove post from blogspot site.
    """)
    require_interactive = True

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('file', help="filename to remove")
        #parser.add_argument('--force',
        #                    default=False,
        #                    action='store_true',
        #                    help="don't check for existance of filename")

    def __init__(self, args):
        self.file = args.file

    def run(self):
        config = self.config

        try:
            post = config.post_by_path(self.file)
            need_ask = False
            do_delete = True
        except FileNotFoundError:
            post = config.post_by_path(self.file, no_existance_check=True)
            need_ask = True

        if post is None:
            self.log.warning("Nothing to remove, file %s wasn't added",
                             self.file)
            return

        if need_ask and config.interactive is True:
            do_delete = True
        if need_ask and config.interactive is False:
            do_delete = False

        if need_ask and config.interactive is None:
            # TODO: implement or drop `ask`
            ret = ask("Post %s is registered but post file does not exist\n"
                      "Do you want to remove it?" % qname(post.name),
                      'y/N')
            do_delete = ret == 'y'

        if need_ask and not do_delete:
            self.log.info("Skip removing of %s by user choice" %
                          qname(post.name))
        else:
            self.log.info("Remove %s", post.name)
            config.drop(post)
