# exceptions.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .str_util import qname


class BaseError(RuntimeError):
    """Base error class for bloggertool"""


class FileError(BaseError):
    """Base file error"""
    MSG = "%(role)s %(file)s error"

    def __init__(self, file, root=None, role='File'):
        args = {'file': qname(file),
                'root': qname(root) if root is not None else None,
                'role': role}
        super(FileError, self).__init__(file,
                                        root,
                                        role)
        self._str = self.MSG % args
        self.file = file
        self.root = root
        self.role = role

    def __str__(self):
        return self._str

    def __repr__(self):
        return self._str


class FileNotFoundError(FileError):
    """File not found"""
    MSG = "%(role)s %(file)s does not exists"


class FileOutOfProject(FileError):
    """File out of project root folder"""
    MSG = "%(role)s %(file)s is out of project root dir %(root)s"


class ConfigError(BaseError):
    pass


class RootNotFoundError(ConfigError):
    pass


class RemoteError(BaseError):
    """Exception from remote logic"""


class UserCancel(BaseError):
    """User aborted current operation by expicit input"""

class UnknownDocType(BaseError):
    """Unknown document type"""
