# help/__init__.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from collections import namedtuple

Topic = namedtuple('Topic', 'title text')

TOPICS = {}


def add_topic(name, title, text):
    TOPICS[name] = Topic(title, text)


import bloggertool.help.template  # add topics

from bloggertool.help.help import make_help


__all__ = ['make_help']
