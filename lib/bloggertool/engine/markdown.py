# encoding.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from __future__ import absolute_import

import markdown

from bloggertool.engine import Meta

class Engine(object):
    MARKDOWN_EXTS = ['abbr',
#                     'codehilite', # see http://pygments.org/docs/
                     'def_list',
                     'fenced_code',
                     # default at end of html or ///Footnotes Go Here ///
                     'footnotes',
                     # configure via header_level and header_forceid: Off
                     # in md metadata
                     'headerid',
                     'meta',
                     'tables',
                     'toc',  # use [TOC] in md file
                     ]


    def do(self, source):
        md = markdown.Markdown(extensions=self.MARKDOWN_EXTS)
        inner_html = md.convert(source)

        meta = Meta

        if 'title' in md.Meta:
            meta.title = ' '.join(md.Meta['title'])

        if 'slug' in md.Meta:
            assert len(md.Meta['slug']) == 1
            slug = md.Meta['slug'][0]
            meta.slug = slug

        if 'labels' in md.Meta:
            labels_str = ', '.join(md.Meta['labels'])
            labels = [l.strip() for l in labels_str.split(',')]
            meta.labels = frozenset(labels)

        return inner_html, meta
