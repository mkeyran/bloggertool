# log_util.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
import sys


class class_logger(object):
    """descriptor, used to make logger for attribute in first usage"""
    def __init__(self):
        pass

    def __get__(self, instance, owner):
        log = getattr(owner, '__log__', None)
        if log is None:
            name = owner.__module__ + '.' + owner.__name__
            log = logging.getLogger(name)
            owner.__log__ = log
            return log
        return log


def setup_log(args):
    root = logging.getLogger()
    if args.verbose:
        fs = "%(levelname)s:%(name)s:%(message)s"
        root.setLevel(logging.DEBUG)
    else:
        fs = "%(levelname)s %(message)s"
        root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(fs)
    handler.setFormatter(fmt)
    root.addHandler(handler)
    #logging.basicConfig(level=logging.DEBUG)
