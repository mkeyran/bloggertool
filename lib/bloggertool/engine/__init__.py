# encoding.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from bloggertool.exceptions import UnknownDocType

MARKDOWN = 'Markdown'
REST = 'ReST'


def find_type(f):
    doctype = MARKDOWN
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line == '=' * len(line):
            doctype = REST
        return doctype
    raise UnknownDocType()


def get_engine(doctype):
    if doctype == MARKDOWN:
        from .markdown import Engine
        return Engine()
    elif doctype == REST:
        from .rest import Engine
        return Engine()
    else:
        raise UnknownDocType()


class Meta(object):
    labels = frozenset()
    title = None
    slug = None
