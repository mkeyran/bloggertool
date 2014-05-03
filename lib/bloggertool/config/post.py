# config/post.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import datetime
import os

import markdown

from dateutil.tz import tzutc

from bloggertool.engine import get_engine, find_type
from bloggertool.exceptions import ConfigError, UserCancel
from bloggertool.str_util import T, a

from .attrs import Record, str_attr, set_of_str_attr, timestamp_attr


class Post(Record):
    name = str_attr()
    file = str_attr()
    link = str_attr()
    postid = str_attr()
    title = str_attr()
    slug = str_attr()
    labels = set_of_str_attr()
    published = timestamp_attr()
    updated = timestamp_attr()
    local_stamp = timestamp_attr()
    file_encoding = str_attr()
    doctype = str_attr('Markdown') # ReST or Markdown


    TEMPLATE_VARS = {
        'slug': 'article slug',
        'title': 'article title',
        'inner': 'content of article',
        'labels': 'list of article labels, sorted alphabetically',
        }

    NICE_HTML_SUFFIX = '.html'
    INNER_HTML_SUFFIX = '.inner.html'

    def __init__(self, config, name, file):
        super(Post, self).__init__(config)
        self.name = name
        self.file = file
        self.slug = os.path.basename(name)
        fs = self.config.fs
        with fs.open(file, 'r', self.effective_encoding) as f:
            self.doctype = find_type(f)

    @property
    def effective_encoding(self):
        encoding = self.file_encoding
        if not encoding:
            encoding = self.config.info.effective_source_encoding
        return encoding

    @property
    def inner_html_path(self):
        return self.config.fs.replace_ext(self.file,
                                          self.INNER_HTML_SUFFIX)

    @property
    def nice_html_path(self):
        return self.config.fs.replace_ext(self.file,
                                          self.NICE_HTML_SUFFIX)

    @property
    def labels_str(self):
        return ', '.join(sorted(self.labels))

    @property
    def is_html_fresh(self):
        fs = self.config.fs
        if not fs.exists(self.inner_html_path):
            return False
        if not fs.exists(self.nice_html_path):
            return False
        md_time = fs.getmtime(self.file)
        inner_html_time = fs.getmtime(self.inner_html_path)
        nice_html_time = fs.getmtime(self.nice_html_path)
        if md_time > inner_html_time:
            return False
        if md_time > nice_html_time:
            return False
        return True

    def refresh_html(self, force=False):
        fs = self.config.fs
        if not force:
            if self.is_html_fresh:
                return False

        self.log.info(a("Generate html for {self.name!q}"))
        self.local_stamp = datetime.datetime.now(tzutc())

        engine = get_engine(self.doctype)

        with fs.open(self.file, 'r', self.effective_encoding) as md:
            source = md.read()
            if not source:
                self.log.warning("Empty source file: '%s'", self.file)
                return False

            inner_html, meta = engine.do(source)
            # update post title

            if meta.title is not None:
                self.overwrite_attr('title', meta.title)
            if meta.slug is not None:
                slug = meta.slug
                if slug != self.slug and self.postid:
                    raise ConfigError(
                        T("Post {0.name!q} has already published, "
                          "cannot change slug").format(self))
                self.overwrite_attr('slug', slug)

            if meta.labels is not None:
                self.overwrite_attr('labels', meta.labels)

            with fs.open(self.inner_html_path, 'w') as f:
                f.write(inner_html)

            with fs.open(self.nice_html_path, 'w') as f:
                info = self.config.info
                if not info.has_template:
                    self.log.warning(T("""
                        User settings has no template specified.
                        Use markdown output as html.
                        """))
                    f.write(inner_html)
                else:
                    template = info.template
                    labels = list(sorted(self.labels))
                    args = dict(
                        title=self.title,
                        slug=self.slug,
                        labels=labels,
                        inner=inner_html)

                    TEMPLATE_VARS = self.TEMPLATE_VARS
                    if sorted(args.keys()) != sorted(TEMPLATE_VARS.keys()):
                        missing = set(TEMPLATE_VARS) - set(args)
                        extra = set(args) - set(TEMPLATE_VARS)
                        missing = ', '.join(sorted(missing))
                        extra = ', '.join(sorted(extra))
                        msg = T("""
                            Bad template vars list:
                              missing: {missing}
                              extra: {extra}
                            """)(missing=missing, extra=extra)
                        raise RuntimeError(msg)
                    for line in template.generate(args):
                        f.write(line)
        return True

    def inner_html(self, force=False):
        self.refresh_html(force)
        with self.config.fs.open(self.inner_html_path, 'r') as f:
            return f.read()

    def nice_html(self, force=False):
        self.refresh_html(force)
        with self.config.fs.open(self.nice_html_path, 'r') as f:
            return f.read()

    def info_list(self, long, indent=4):
        changed = '*' if self.changed else ''
        ret = T("{changed}{self.name!q}")(changed=changed, self=self)
        if long:
            ret += '\n' + T("""
                title: {self.title}
                link: {self.link}
                slug: {self.slug}
                labels: {self.labels_str}
                postid: {self.postid}
                published: {self.published!t}
                updated: {self.updated!t}
                localstamp: {self.local_stamp!t}
                """, indent=indent)(self=self)
        return ret

    def overwrite_attr(self, attr_name, new_val, suppress_empty=True):
        config = self.config
        interactive = config.interactive
        cur_val = getattr(self, attr_name)
        if new_val != cur_val:
            if suppress_empty and not cur_val:
                ret = 'y'
            elif interactive is None:
                ret = config.ask(a("""
                        New {attr_name}: {new_val!Q}
                        is different from existing {attr_name}: {cur_val!q}
                        for post {self.name!q}
                        Do you like to override?"""),
                    'y/N/q')
            elif interactive:
                ret = 'y'
            else:
                ret = 'n'

            if ret == 'q':
                raise UserCancel("Cancel operation")
            elif ret == 'n':
                self.log.warning(
                    a("Skip {attr_name} modification for {self.name!q}"))
            else:
                setattr(self, attr_name, new_val)
