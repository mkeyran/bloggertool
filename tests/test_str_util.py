# -*- encoding: utf-8 -*-
import datetime

import unittest

from bloggertool.str_util import (qname,
                                  Formatter, Template, NamespaceFormatter,
                                  auto_format)
#                                  parse_timestamp,
#                                  tzutc)


class TestQName(unittest.TestCase):
    def test_simple(self):
        self.assertEqual('name', qname('name'))
        self.assertEqual('name.txt', qname('name.txt'))
        self.assertEqual("name'a", qname("name'a"))

    def test_simple_space(self):
        self.assertEqual('"name a"', qname('name a'))
        self.assertEqual('"name\' a"', qname("name' a"))

    def test_space_with_quot(self):
        self.assertEqual('<name "a">', qname('name "a"'))

    def test_prevent_doubling(self):
        self.assertEqual('"name a"', qname(qname('name a')))
        self.assertEqual('<name "a">', qname(qname('name "a"')))

#class TestParseBloggerstamp(unittest.TestCase):
#    def test_simple(self):
#        self.assertEqual(datetime.datetime(2009, 3, 12, 3, 42, 0, 5000,
#                                           tzinfo=tzutc()),
#                         parse_timestamp("2009-03-12T05:42:00.005+02:00"))#
#
#
#    def test_negativetz(self):
#        self.assertEqual(datetime.datetime(2009, 3, 12, 7, 42, 0, 5000,
#                                           tzutc()),
#                         parse_timestamp("2009-03-12T05:42:00.005-02:00"))


class TestFormatter(unittest.TestCase):
    def setUp(self):
        self.fmt = Formatter()

    def test_default(self):
        self.assertEqual('a', self.fmt.format('{0}', 'a'))

    def test_q(self):
        self.assertEqual('"a b"', self.fmt.format('{0!q}', 'a b'))

    def test_Q(self):
        self.assertEqual('None', self.fmt.format('{0!Q}', None))
        self.assertEqual('"a b"', self.fmt.format('{0!Q}', 'a b'))


class TestTemplate(unittest.TestCase):
    def test_simple(self):
        self.assertEqual('a', Template('a'))

    def test_str(self):
        self.assertEqual('a', str(Template('a')))

    def test_unicode(self):
        self.assertEqual(u'a', unicode(Template('a')))

    def test_russian(self):
        self.assertEqual(u'русский', Template(u'русский'))

    def test_format(self):
        self.assertEqual('"a b"', Template('{0!q}').format('a b'))
        self.assertEqual('"a b"', format(Template('{0!q}'), 'a b'))

    def test_format_clash(self):
        self.assertEqual('a b c', Template('{self} {args} {kwargs}').format(
            self='a',
            args='b',
            kwargs='c'))

    def test_strip(self):
        self.assertEqual('a', Template(' a '))

    def test_no_strip(self):
        self.assertEqual(' a ', Template(' a ', strip=False))

    def test_dedent_with_strip(self):
        self.assertEqual('a\nb\nc', Template("""
            a
            b
            c
            """))

    def test_dedent_without_strip(self):
        self.assertEqual('\na\nb\nc\n', Template("""
            a
            b
            c
            """, strip=False, dedent=True))

    def test_add(self):
        self.assertEqual('a\nb  c', Template("""
            a
            b
            """) + '  c')

    def test_add(self):
        a = Template("""
            a
            b
            """)
        a += '  c'
        self.assertEqual('a\nb  c', a)

    def test_indent(self):
        self.assertEqual('  a\n  b', Template("""
            a
            b
            """, indent=2))


global_name = 'global'


class TestNamespaceFormatter(unittest.TestCase):
    def test_simple(self):
        ns = {'b': 2}
        ret = NamespaceFormatter(ns).format("{a} {b}", a=1)
        self.assertEqual('1 2', ret)

    def test_nested(self):
        ns1 = {'b': 2}
        ns2 = {'c': 3}
        fmt = NamespaceFormatter(ns1, ns2)
        ret = fmt.format("{a} {b} {c}", a=1)
        self.assertEqual('1 2 3', ret)

    def test_class_attr(self):
        class A(object):
            def __init__(self, val):
                self.val = val

        ns1 = {'b': A(2)}
        ns2 = {'c': A(3)}
        fmt = NamespaceFormatter(ns1, ns2)
        ret = fmt.format("{a.val} {b.val} {c.val}", a=A(1))
        self.assertEqual('1 2 3', ret)

    def test_not_found(self):
        ns = {'b': 2}
        fmt = NamespaceFormatter(ns)
        self.assertRaises(KeyError, fmt.format, "{a} {b} {c}", a=1)

    def test_ns(self):
        local_name = 'local'
        fmt = NamespaceFormatter(locals(), globals())
        ret = fmt.format("{local_name} {global_name}")
        self.assertEqual('local global', ret)

    def test_auto_format(self):
        local_name = 'local'
        self.assertEqual('local global',
                         auto_format("{local_name} {global_name}"))
