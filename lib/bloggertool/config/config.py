# config/config.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import os

from .info import Info
from .post import Post

import yaml

from bloggertool.exceptions import RootNotFoundError
from .file_system import FileSystem
from bloggertool.log_util import class_logger
from bloggertool.ui import ask as _do_ask


class Config(object):
    CONFIG_FILENAME = '.blogspot.yaml'
    SECRET_FILENAME = '.client_secret.json'
    log = class_logger()
    _ask = staticmethod(_do_ask)

    def __init__(self, root):
        self._fs = FileSystem(root)
        self._posts = {}
        self._info = Info(self)
        self._info._config = self
        self.need_save = False
        self.interactive = False

    @property
    def fs(self):
        return self._fs

    @property
    def config_filename(self):
        return os.path.join(self.root, self.CONFIG_FILENAME)

    @property
    def secret_filename(self):
        return os.path.join(self.root, self.SECRET_FILENAME)

    @property
    def root(self):
        return self.fs.root

    @classmethod
    def find_root(cls, cwd=None):
        root = os.getcwd() if cwd is None else os.path.abspath(cwd)
        config_path = os.path.join(root, cls.CONFIG_FILENAME)
        while not os.path.exists(config_path):
            root = os.path.dirname(root)
            config_path = os.path.join(root, cls.CONFIG_FILENAME)
            if root == '/':
                if not os.path.exists(config_path):
                    raise RootNotFoundError("Cannot find project for '%s'" %
                                            os.getcwd())
        secret_path = os.path.join(root, cls.SECRET_FILENAME)
        if not os.path.exists(secret_path):
            raise RootNotFoundError(
                "Cannot find secret file '%s' beside to config file '%s'"
                % (secret_path, config_path))
        return root

    @classmethod
    def load(cls):
        root = cls.find_root()
        ret = cls(root)
        with open(ret.config_filename) as f:
            cfg = yaml.load(f)

            if cfg is not None:
                if 'posts' in cfg:
                    for name, data in cfg['posts'].iteritems():
                        data['name'] = Post.name.from_yaml(name)
                        post = Post.from_dict(data)
                        post._config = ret
                        ret._posts[name] = post

                info = Info.from_dict(cfg.get('info', {}))
                info._config = ret
                ret._info = info

            return ret

    def save(self):
        self.log.debug("Save config to '%s'", self.config_filename)
        posts = {}
        for post in self:
            posts[Post.name.to_yaml(post.name)] = post.to_dict()
        cfg = {'posts': posts,
               'info': self.info.to_dict()}

        # NB: save data only after building full yaml dict
        # Otherwise you can corrupt config file if case of errors
        with open(self.config_filename, 'w') as f:
            yaml.dump(cfg, f)

    # container interface

    def __len__(self):
        return len(self._posts)

    def __nonzero__(self):
        return bool(self._posts)

    def __getitem__(self, name):
        return self._posts[name]

    def __iter__(self):
        return self._posts.itervalues()

    def __contains__(self, name_or_post):
        if isinstance(name_or_post, Post):
            name = name_or_post.name
        else:
            name = name_or_post
        return name in self._posts

    def add(self, name, rel_path):
        assert name not in self
        post = Post(self, name, rel_path)
        self._posts[post.name] = post
        self.need_save = True
        return post

    def drop(self, name_or_post):
        if isinstance(name_or_post, Post):
            name = name_or_post.name
        else:
            name = name_or_post
        assert name in self
        del self._posts[name]
        self.need_save = True

    def post_by_path(self, mdpath, no_existance_check=False):
        if mdpath.endswith('.'):
            mdpath = mdpath[:-1]

        if not mdpath.endswith('.md'):
            mdpath += '.md'

        mdpath = self.fs.expand_path(mdpath)

        relpath = self.fs.rel_path(mdpath,
                                   no_existance_check=no_existance_check)
        name = self.fs.replace_ext(relpath, '')  # drop .md ending

        if name in self:
            return self[name]
        else:
            return None

    @property
    def info(self):
        return self._info

    def ask(self, prompt, answers):
        return self._ask(prompt, answers)
