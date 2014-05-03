import datetime
import unittest

from dateutil.tz import tzutc

from bloggertool.config.attrs import (attr, str_attr, bool_attr,
                                      set_of_str_attr,
                                      timestamp_attr,
                                      Record)


class sample_attr(attr):
    from_yaml = to_yaml = lambda self, v: v


class SampleConfig(object):
    need_save = False


class SampleRecord(Record):
    a = sample_attr()
    b = bool_attr()
    c = str_attr()
    t = timestamp_attr()
    d = set_of_str_attr()


class SampleRecord2(SampleRecord):
    e = str_attr()


class SampleRecord3(Record):
    a = sample_attr()


class TestAttr(unittest.TestCase):
    def test_ctor(self):
        a = sample_attr()
        self.assertEqual(None, a._default)
        self.assertEqual(None, a._name)
        self.assertEqual(None, a._attr_name)

        b = sample_attr('default')
        self.assertEqual('default', b._default)

    def test_set_name(self):
        a = sample_attr()

        a.set_name('attr')
        self.assertEqual('attr', a.name)
        self.assertEqual('_attr', a._attr_name)

    def test_class__get__(self):
        self.assertEqual(SampleRecord.__dict__['a'], SampleRecord.a)

    def test_get_val(self):
        r = SampleRecord(SampleConfig())
        self.assertEqual(None, SampleRecord.a.get_val(r))

    def test_setup(self):
        r = SampleRecord(SampleConfig())
        self.assertEqual(True, r.changed)
        SampleRecord.a.setup(r, 'value')
        self.assertEqual('value', r.a)
        self.assertEqual(True, r.changed)
        self.assertEqual(False, r.need_save)

    def test_set_val(self):
        r = SampleRecord(SampleConfig())
        r._changed = False
        self.assertEqual(False, r.need_save)
        r.a = 'value'
        self.assertEqual('value', r.a)
        self.assertEqual(True, r.changed)
        self.assertEqual(True, r.need_save)


class TestBoolAttr(unittest.TestCase):
    def test_from_yaml(self):
        a = bool_attr()
        self.assertEqual(False, a.from_yaml(None))
        self.assertEqual(False, a.from_yaml(False))
        self.assertEqual(True, a.from_yaml(True))
        self.assertEqual(False, a.from_yaml(''))
        self.assertEqual(True, a.from_yaml('yes'))

    def test_to_yaml(self):
        a = bool_attr()
        self.assertEqual(False, a.to_yaml(False))
        self.assertEqual(True, a.to_yaml(True))

    def test_set_val(self):
        r = SampleRecord(SampleConfig())
        r.b = None
        self.assertEqual(False, r.b)


class TestStrAttr(unittest.TestCase):
    def test_from_yaml(self):
        a = str_attr()
        self.assertEqual(u'', a.from_yaml(None))
        self.assertEqual(u'a', a.from_yaml('a'))

    def test_to_yaml(self):
        a = str_attr()
        self.assertEqual('', a.to_yaml(None))
        self.assertEqual('a', a.to_yaml(u'a'))

    def test_set_val(self):
        r = SampleRecord(SampleConfig())
        r.c = 'abc'
        self.assertEqual(u'abc', r.c)
        r.c = None
        self.assertEqual(u'', r.c)


class TestTimestampAttr(unittest.TestCase):
    t = 1298032285
    dt = datetime.datetime(2011, 2, 18, 12, 31, 25, tzinfo=tzutc())

    def test_from_yaml(self):
        a = timestamp_attr()
        self.assertEqual(self.dt, a.from_yaml(self.t))

    def test_to_yaml(self):
        a = timestamp_attr()
        self.assertEqual(self.t, a.to_yaml(self.dt))

    def test_set_val(self):
        r = SampleRecord(SampleConfig())
        self.assertRaises(TypeError, setattr, r, 't', 'abc')
        r.t = self.dt
        self.assertEqual(self.dt, r.t)


class TestSetOfStrAttr(unittest.TestCase):
    def test_from_yaml(self):
        a = set_of_str_attr()
        self.assertEqual(frozenset(), a.from_yaml(None))
        self.assertEqual(frozenset([u'a']), a.from_yaml(['a']))
        self.assertEqual(frozenset([u'a', u'b']), a.from_yaml(['a', 'b']))

    def test_to_yaml(self):
        a = set_of_str_attr()
        self.assertEqual([], a.to_yaml(None))
        self.assertEqual([], a.to_yaml(frozenset()))
        self.assertEqual(['a'], a.to_yaml(frozenset([u'a'])))
        self.assertEqual(['a', 'b'], a.to_yaml(frozenset([u'a', u'b'])))

    def test_set_val(self):
        r = SampleRecord(SampleConfig())
        r.d = set(['abc'])
        self.assertEqual(frozenset([u'abc']), r.d)
        r.d = 'abc'
        self.assertEqual(frozenset([u'a', u'b', u'c']), r.d)
        r.d = None
        self.assertEqual(frozenset(), r.d)


class TestRecordMeta(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(True, 'a' in SampleRecord.__attrs__)
        self.assertEqual(True, 'b' in SampleRecord.__attrs__)
        self.assertEqual(True, 'c' in SampleRecord.__attrs__)
        self.assertEqual(True, 'd' in SampleRecord.__attrs__)
        self.assertEqual(False, 'e' in SampleRecord.__attrs__)

    def test_inherited(self):
        self.assertEqual(True, 'a' in SampleRecord2.__attrs__)
        self.assertEqual(True, 'b' in SampleRecord2.__attrs__)
        self.assertEqual(True, 'c' in SampleRecord2.__attrs__)
        self.assertEqual(True, 'd' in SampleRecord2.__attrs__)
        self.assertEqual(True, 'e' in SampleRecord2.__attrs__)


class TestRecord(unittest.TestCase):
    def test_ctor(self):
        r = SampleRecord(SampleConfig())
        self.assertEqual(True, r.changed)
        self.assertEqual(False, r.need_save)
        self.assertEqual(False, r.config.need_save)

    def test_changed(self):
        r = SampleRecord(SampleConfig())

        r._changed = False
        self.assertEqual(False, r.changed)

        r.a = 123
        self.assertEqual(True, r.changed)
        self.assertEqual(True, r.need_save)
        self.assertEqual(True, r.config.need_save)

    def test_changed2(self):
        r = SampleRecord(SampleConfig())
        r.changed = False

        self.assertEqual(False, r.changed)
        self.assertEqual(True, r.need_save)

    def test_changed3(self):
        r = SampleRecord(SampleConfig())
        r.a = 123
        r.changed = False
        r.need_save = False

        self.assertEqual(False, r.changed)
        self.assertEqual(False, r.need_save)

        r.a = 123  # the same value, don't change attr

        self.assertEqual(False, r.changed)
        self.assertEqual(False, r.need_save)

    def test_from_dict_empty(self):
        r = SampleRecord3.from_dict({})
        self.assertEqual(None, r.a)
        self.assertEqual(True, r.changed)
        self.assertEqual(False, r.need_save)

    def test_from_dict_partial(self):
        r = SampleRecord3.from_dict({'a': 123})
        self.assertEqual(123, r.a)
        self.assertEqual(True, r.changed)
        self.assertEqual(False, r.need_save)

    def test_from_dict1(self):
        r = SampleRecord3.from_dict({'a': 234, 'changed': True})
        self.assertEqual(234, r.a)
        self.assertEqual(True, r.changed)
        self.assertEqual(False, r.need_save)

    def test_from_dict2(self):
        r = SampleRecord3.from_dict({'a': 234, 'changed': False})
        self.assertEqual(234, r.a)
        self.assertEqual(False, r.changed)
        self.assertEqual(False, r.need_save)

    def test_to_dict1(self):
        r = SampleRecord3(SampleConfig())
        r.a = 123
        self.assertEquals({'changed': True, 'a': 123}, r.to_dict())

    def test_to_dict2(self):
        r = SampleRecord3(SampleConfig())
        r.a = 234
        r.changed = False
        self.assertEquals({'changed': False, 'a': 234}, r.to_dict())
