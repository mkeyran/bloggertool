# config/filesystem.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import codecs
import os

from bloggertool.exceptions import FileNotFoundError, FileOutOfProject


class FileSystem(object):
    class Impl(object):
        exists = staticmethod(os.path.exists)
        getmtime = staticmethod(os.path.getmtime)
        open = staticmethod(codecs.open)

    def __init__(self, root):
        self._root = root
        self._impl = self.Impl()

    @property
    def root(self):
        return self._root

    def expand_path(self, path, role='File'):
        """
        Return full path.
            normalized path if path is absolute
            user expanded path if path starts with ~ or ~user
            project expanded path if path starts with @
            current dir expanded path otherwise
        """

        # XXX check expanding for Windows
        # should return arg if arg startswith C:\ etc
        # XXX check expand for local user ~/filename
        #ret = os.path.abspath(ret)
        #if ret.startswith(self.root):
        #ret = os.path.join(self.root, path)
        if not os.path.isabs(path):
            #ret = os.path.join(self.root, path)
            ret = os.path.abspath(path)
        else:
            ret = os.path.normpath(path)
        #ret = os.path.abspath(path)
        #if not os.path.exists(ret):
        #    ret = os.path.join(self.root, path)
        if not ret.startswith(self.root):
            raise FileOutOfProject(ret, self.root, role)
        return ret

    def exists(self, rel_path):
        full_path = self.abs_path(rel_path, no_existance_check=True)
        return self._impl.exists(full_path)

    def getmtime(self, rel_path):
        full_path = self.abs_path(rel_path)
        return self._impl.getmtime(full_path)

    def open(self, rel_path, mode, encoding='utf-8'):
        no_existance_check = mode == 'w'
        full_path = self.abs_path(rel_path,
                                  no_existance_check=no_existance_check)
        return self._impl.open(full_path, mode, encoding)

    def replace_ext(self, path, new_ext):
        root, old_ext = os.path.splitext(path)
        return root + new_ext

    def abs_path(self, rel_path, no_existance_check=False, role='File'):
        """Return absolute path for rel_path,
        assuming rel_path is relative on config.root.

        By default performs check for file existance.
        `role` used for exception message.

        NB. Behavior differs from os.path.abspath!!!
        """
        abs_path = os.path.join(self.root, rel_path)
        if not no_existance_check:
            self.check_existance(abs_path, role)
        return abs_path

    def check_existance(self, abs_path, role):
        if not self._impl.exists(abs_path):
            raise FileNotFoundError(abs_path, role=role)

    def rel_path(self, abs_path, no_existance_check=False, role='File'):
        """Path, relative to project root"""
        root = self.root
        if not abs_path.startswith(root):
            raise FileOutOfProject(abs_path, root, role)

        if not no_existance_check:
            self.check_existance(abs_path, role)

        rel_path = abs_path[len(root):]
        while rel_path.startswith('/'):
            rel_path = rel_path[1:]

        return rel_path
