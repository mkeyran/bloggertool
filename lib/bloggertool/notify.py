# notify.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import asyncore

import pyinotify

from bloggertool.log_util import class_logger


class EventProcessor(pyinotify.ProcessEvent):
    log = class_logger()

    def my_init(self, main):
        self.main = main

    def process_default(self, event):
        try:
            for path, cb, args, kwargs in self.main.handlers:
                if event.pathname == path:
                    cb(*args, **kwargs)
        except Exception:
            self.log.exception("In notifier event handling")


class Notifier(object):
    def __init__(self, root):
        self.watch_manager = pyinotify.WatchManager()
        self.notifier = pyinotify.AsyncNotifier(
            self.watch_manager,
            default_proc_fun=EventProcessor(main=self))
        self.handlers = []
        events = pyinotify.IN_ATTRIB | pyinotify.IN_MODIFY
        self.watch_manager.add_watch(root, events, rec=True)

    def add(self, path, cb, *args, **kwargs):
        params = (path, cb, args, kwargs)
        self.handlers.append(params)

    def loop(self):
        asyncore.loop()
