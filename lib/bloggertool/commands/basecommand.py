# commands/basecommand.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from bloggertool.config import Config
from bloggertool.log_util import class_logger


class BaseCommand(object):
    log = class_logger()
    config = None

    NAME = None
    DESCR = None
    HELP = None

    require_load_config = True
    require_interactive = False

    def load_config(self, args):
        self.config = Config.load()
        if self.require_interactive:
            self.config.interactive = args.interactive
