# commands/__init__.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .basecommand import BaseCommand

from .ls import LsCommand
from .add import AddCommand
from .html import HtmlCommand
from .link import LinkCommand
from .info import InfoCommand
from .rinfo import RInfoCommand
from .rls import RLsCommand
from .diff import DiffCommand
from .browse import OpenCommand, ROpenCommand
from .push import PushCommand
from .init import InitCommand
from .rm import RmCommand
from .label import LabelCommand
from .publish import PublishCommand
from .show import ShowCommand

commands = [LsCommand, AddCommand, HtmlCommand, LinkCommand,
            InfoCommand, RInfoCommand, RLsCommand,
            DiffCommand, OpenCommand, ROpenCommand,
            PushCommand,
            InitCommand, RmCommand,
            LabelCommand, PublishCommand, ShowCommand]

__all__ = [cls.__name__ for cls in commands + [BaseCommand]]
