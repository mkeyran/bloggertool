# config/info.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import getpass

import keyring
import jinja2

from bloggertool.remote import Remote, CaptchaChallenge, BadAuthentication
from bloggertool.exceptions import ConfigError
from bloggertool.ui import get_captcha

from .attrs import Record, str_attr
from .file_system import FileSystem


class Info(Record):
    """Project info"""
    _template_env = None

    email = str_attr()
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

    def get_passwd(self, force=False):
        if self.email is None:
            raise ConfigError("User email has not specified")
        user = getpass.getuser()
        if force:
            passwd = None
        else:
            passwd = keyring.get_password('blogspot-tool', user)
        if passwd is None:
            if self.config.interactive is not None:
                raise ConfigError("Cannot ask user in non-interactive mode")
            passwd = getpass.getpass(
                "Enter password for google account %s: " %
                self.email)
            keyring.set_password('blogspot-tool', user, passwd)
        return passwd

    def remote(self):
        if self.email is None:
            raise ConfigError("User email has not specified")

        has_error = False
        captcha_token = None
        captcha_response = None
        for i in range(3):
            try:
                passwd = self.get_passwd(has_error)
                srv = Remote(self.email,
                             passwd,
                             self.blogid,
                             captcha_token=captcha_token,
                             captcha_response=captcha_response)
                return srv
            except BadAuthentication, ex:
                self.log.warning('Cannot login: %s', ex)
                has_error = True
            except CaptchaChallenge, ex:
                self.log.warning("Captcha required %s", ex)
                self.log.debug("Captcha_url %s", ex.captcha_url)
                captcha_token = ex.captcha_token

                captcha_response = get_captcha(ex.captcha_url)
                if captcha_response is None:
                    raise ConfigError('Cannot process CAPTCHA')
                has_error = True

        raise ConfigError('Cannot authenticate')
