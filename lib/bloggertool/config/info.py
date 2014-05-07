# config/info.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import jinja2

from bloggertool.remote import Remote
from bloggertool.exceptions import ConfigError, RemoteError

from .attrs import Record, str_attr
from .file_system import FileSystem


class Info(Record):
    """Project info"""
    _template_env = None

    blogid = str_attr()
    template_dir = str_attr()
    template_file = str_attr()
    source_encoding = str_attr()

    @property
    def effective_source_encoding(self):
        encoding = self.source_encoding
        if encoding:
            return encoding
        else:
            return "utf-8"

    @property
    def has_template(self):
        return self.template_dir and self.template_file

    @property
    def template_fs(self):
        return FileSystem(self.config.fs.abs_path(self.template_dir))

    @jinja2.contextfilter
    def abspath_filter(self, ctx, rel_path):
        """return abspath for argument, assuming what
        arg is relative to current template path"""
        template_name = ctx.name
        assert template_name
        environment = ctx.environment
        template = environment.get_template(template_name)
        fname = template.filename
        assert fname
        return self.template_fs.abs_path(rel_path)

    @property
    def template(self):
        if self._template_env is None:
            if not self.has_template:
                raise ConfigError("Set user properies `template_dir` and "
                                  "`template_file`")

            fs = self.template_fs
            fs.check_existance(fs.abs_path(self.template_file),
                               role='Template file')
            self._template_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(fs.root))

            self._template_env.filters['abspath'] = self.abspath_filter
        return self._template_env.get_template(self.template_file)

    def remote(self, reset_credentials=False):
        try:
            srv = Remote(reset_credentials,
                         self.blogid,
                         secret_filename=self.config.secret_filename)
            return srv
        except RemoteError as ex:
            self.log.warning('Cannot login: %s', ex)

        raise ConfigError('Cannot authenticate')
