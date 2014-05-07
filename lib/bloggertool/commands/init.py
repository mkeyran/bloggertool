# commands/init.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import os
from textwrap import dedent

from bloggertool.config import Config
from bloggertool.exceptions import RootNotFoundError, ConfigError
from bloggertool.str_util import qname

from .basecommand import BaseCommand


class InitCommand(BaseCommand):

    NAME = 'init'
    HELP = "Initialize blogspot progect."
    DESCR = dedent("""\
    Initialize blogspot progect.
    """)
    require_load_config = False

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('root',
                            help="project root")

    def __init__(self, args):
        self.root = args.root

    def gen_exc(self, root):
        return ConfigError("Already a project: %s" % qname(root))

    def run(self):
        try:
            root = Config.find_root(self.root)
        except RootNotFoundError:
            root = os.path.abspath(self.root)
            if not os.path.exists(root):
                os.makedirs(root)
            config_filename = os.path.join(root, Config.CONFIG_FILENAME)
            if os.path.exists(config_filename):
                raise self.gen_exc(root)
            with open(config_filename, 'w'):
                self.log.info("Create project %s", qname(root))
        else:
            raise self.gen_exc(root)
