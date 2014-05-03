# config/attrs.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import calendar
import datetime

from dateutil.tz import tzutc

from bloggertool.log_util import class_logger
from bloggertool.str_util import to_unicode, from_unicode


class attr(object):
    TYPE = tuple()

    def __init__(self, default=None):
        self._default = default
        self._name = None
        self._attr_name = None

    def set_name(self, name):
        self._name = name
        self._attr_name = '_' + name

    @property
    def name(self):
        return self._name

    def get_val(self, instance):
        if not hasattr(instance, self._attr_name):
            return self._default
        return getattr(instance, self._attr_name)

    def __get__(self, instance, owner):
        if instance is None:
            return self  # return attr if class access
        return self.get_val(instance)

    def setup(self, instance, value):
        # called from __init__, should not set 'changed' flag
        setattr(instance, self._attr_name, value)

    def __set__(self, instance, value):
        self.set_val(instance, value)

    def set_val(self, instance, value):
        old_val = self.get_val(instance)
        if old_val != value:
            setattr(instance, self._attr_name, value)
            instance.changed = True

    def from_yaml(self, val):
        raise NotImplementedError(self._name)

    def to_yaml(self, val):
        raise NotImplementedError(self._name)


class bool_attr(attr):
    def from_yaml(self, val):
        return bool(val)

    to_yaml = from_yaml

    def set_val(self, instance, value):
        super(bool_attr, self).set_val(instance, bool(value))


class str_attr(attr):
    # unicode actually
    def from_yaml(self, val):
        return to_unicode(val)

    def to_yaml(self, val):
        return from_unicode(val)

    def set_val(self, instance, value):
        super(str_attr, self).set_val(instance, to_unicode(value))


class set_of_str_attr(attr):
    def from_yaml(self, iterable):
        if iterable is None:
            return frozenset()
        return frozenset(to_unicode(i) for i in iterable)

    def to_yaml(self, val):
        if not val:
            return []
        return [from_unicode(i) for i in sorted(val)]

    def set_val(self, instance, value):
        if value is None:
            value = frozenset()
        else:
            value = frozenset(value)
        super(set_of_str_attr, self).set_val(instance, value)


class timestamp_attr(attr):
    def from_yaml(self, stamp):
        if stamp is None:
            return None
        dt = datetime.datetime.utcfromtimestamp(stamp)
        return dt.replace(tzinfo=tzutc())

    def to_yaml(self, val):
        if val is None:
            return None
        return calendar.timegm(val.utctimetuple())

    def set_val(self, instance, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError(value)
        super(timestamp_attr, self).set_val(instance, value)


class RecordMeta(type):

    def __init__(cls, name, bases, dct):
        super(RecordMeta, cls).__init__(name, bases, dct)

        attrs = dict(getattr(cls, '__attrs__', {}))  # make a copy
        for name, val in dct.iteritems():
            if isinstance(val, attr):
                val.set_name(name)
                attrs[name] = val
        cls.__attrs__ = attrs


class Record(object):
    """NB: recorded attributes should be immutable"""
    __metaclass__ = RecordMeta

    log = class_logger()

    need_save = False
    _changed = True
    _config = None

    def __init__(self, config):
        self._config = config

    @property
    def config(self):
        assert self._config is not None
        return self._config

    @property
    def changed(self):
        return self._changed

    @changed.setter
    def changed(self, value):
        self.need_save = True
        self.config.need_save = True
        self._changed = value

    @classmethod
    def from_dict(cls, dct):
        instance = cls.__new__(cls)
        for name, val in dct.iteritems():
            if name in cls.__attrs__:
                attr = cls.__attrs__[name]
                value = attr.from_yaml(val)
                attr.setup(instance, value)
        instance._changed = bool(dct.get('changed', True))
        return instance

    def to_dict(self):
        ret = {}
        for name, attr in self.__attrs__.iteritems():
            val = attr.get_val(self)
            ret[name] = attr.to_yaml(val)
        ret['changed'] = self._changed
        return ret
