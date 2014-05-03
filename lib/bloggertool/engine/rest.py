# encoding.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from __future__ import absolute_import

from docutils import core
from docutils.writers import html4css1


class Meta(object):
    pass


class Engine(object):
    def do(self, source):
        writer = Writer()
        core.publish_string(source, writer=writer)
        meta = Meta()
        meta.title = ''.join(writer.title)
        meta.slug = None
        meta.labels = []
        meta.subtitle = ''.join(writer.subtitle)
        meta.footer = ''.join(writer.footer)
        return ''.join(writer.body), meta


class Writer(html4css1.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = Translator

    def apply_template(self):
        subs = self.interpolation_dict()
        #from pprint import pprint
        #pprint(subs)
        return ''.join(writer.body)


class Translator(html4css1.HTMLTranslator):
    def __init__(self, document):
        html4css1.HTMLTranslator.__init__(self, document)

