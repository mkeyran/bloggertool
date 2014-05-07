# str_util.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import datetime

import string
import sys

from textwrap import dedent as _dedent

from dateutil.tz import tzlocal


def to_unicode(arg):
    if arg is None:
        return u''
    elif isinstance(arg, unicode):
        return arg
    elif isinstance(arg, str):
        return unicode(arg, 'utf-8')
    elif isinstance(arg, int):
        return unicode(arg)  # let's implicitly convert numbers
    else:
        raise UnicodeDecodeError("Cannot convert to unicode")


def from_unicode(arg):
    if arg is None:
        return ''
    else:
        return arg.encode('utf-8')


def qname(arg):
    if not arg:
        return ''
    if not ' ' in arg:
        return arg
    elif arg[0] == arg[-1] == '"':
        return arg
    elif arg[0] == '<' and arg[-1] == '>':
        return arg
    elif not '"' in arg:
        return '"' + arg + '"'
    else:
        # arg has both spaces and "
        # as < and > are not allowed as part of path without screeneng
        # let's use angle brackets

        # so good so far. Quote angle brackets???
        # I like to see name "quoted" if one has spaces
        # also I like to see unambigous quotes without exceptions

        # using \" is ugly choice
        # while that form supported by unix very well I not sure about Windows
        # Intend of `qname` function to generate good file name to use it
        # in command line shell

        # enough for start
        return '<' + arg + '>'


def format_dt(dt):
    if dt is None:
        return None
    local_dt = dt.astimezone(tzlocal())
    local_now = datetime.datetime.now(tzlocal())
    delta = local_now - local_dt
    if delta.days < 0:
        # dt in future
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    elif delta.seconds < 60:
        return T("now")
    elif delta.seconds < 600:
        return T("{minutes:d} minutes ago").format(minutes=delta.seconds / 60)
    elif local_dt.date() == local_now.date():
        return local_dt.strftime("%H:%M")
    else:
        return local_dt.strftime("%Y-%m-%d")


class Formatter(string.Formatter):
    def convert_field(self, value, conversion):
        if 'Q' == conversion:
            if value is None:
                return 'None'
            else:
                return qname(value)
        elif 'q' == conversion:
            return qname(value)
        elif 't' == conversion:
            return format_dt(value)
        elif 'N' == conversion:
            if not value:
                return None
            else:
                return value
        else:
            return super(Formatter, self).convert_field(value, conversion)


_formatter = Formatter()


class Template(unicode):
    def __new__(cls, pattern, **kwargs):
        strip = kwargs.get('strip', True)
        dedent = kwargs.get('dedent', strip)
        indent = kwargs.get('indent', 0)
        if dedent:
            pattern = _dedent(pattern)
        if strip:
            pattern = pattern.strip()
        if indent:
            prefix = ' ' * indent
            pattern = '\n'.join(prefix + line for line in pattern.splitlines())
        return unicode.__new__(cls, pattern)

    def format(__self, *__args, **__kwargs):
        # use __self etc to don't clash with __kwargs keys
        return _formatter.vformat(__self, __args, __kwargs)

    def __format__(__self, *__args, **__kwargs):
        return __self.format(*__args, **__kwargs)

    def __call__(__self, *__args, **__kwargs):
        return __self.format(*__args, **__kwargs)

    def __add__(self, other):
        return self.__class__(unicode(self) + other, strip=False)

    __iadd__ = __add__


class NamespaceFormatter(Formatter):
    def __init__(self, *namespaces):
        self.namespaces = namespaces

    def get_value(self, key, args, kwargs):
        if isinstance(key, basestring):
            try:
                return kwargs[key]
            except KeyError:
                for namespace in self.namespaces:
                    try:
                        return namespace[key]
                    except KeyError:
                        pass
        return super(NamespaceFormatter, self).get_value(key, args, kwargs)


def auto_format(spec, **spec_kwargs):
    template = Template(spec, **spec_kwargs)
    frame = sys._getframe(1)
    fmt = NamespaceFormatter(frame.f_locals, frame.f_globals)
    return fmt.format(template)


T = Template
NF = NamespaceFormatter
a = auto_format
