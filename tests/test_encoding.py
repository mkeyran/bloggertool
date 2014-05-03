# -*- encoding: utf-8 -*-

import locale
import os
import sys
import unittest

from StringIO import StringIO

from bloggertool.encoding import Output, setup_encoding


class TestSetupEncoding(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.environ = os.environ
        self.getpreferredencoding = locale.getpreferredencoding

    def tearDown(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        os.environ = self.environ
        locale.getpreferredencoding = self.getpreferredencoding

    def test_direct(self):
        setup_encoding('cp866')
        self.assertEqual('cp866', sys.stdout.encoding)
        self.assertEqual('cp866', sys.stderr.encoding)

    def test_locale(self):
        sys.stdout = StringIO()
        sys.stdout.encoding = None

        setup_encoding(None)
        enc = locale.getpreferredencoding()
        self.assertEqual(enc, sys.stdout.encoding)
        self.assertEqual(enc, sys.stderr.encoding)

    def test_locale_overriden(self):
        sys.stdout = StringIO()
        sys.stdout.encoding = None
        locale.getpreferredencoding = lambda: 'cp866'
        setup_encoding(None)
        self.assertEqual('cp866', sys.stdout.encoding)
        self.assertEqual('cp866', sys.stderr.encoding)

    def test_default_ascii(self):
        sys.stdout = StringIO()
        sys.stdout.encoding = None
        locale.getpreferredencoding = lambda: None

        setup_encoding(None)
        self.assertEqual('ascii', sys.stdout.encoding)
        self.assertEqual('ascii', sys.stderr.encoding)

    def test_stdout_encoding(self):
        sys.stdout = StringIO()
        sys.stdout.encoding = 'cp1251'
        setup_encoding(None)
        self.assertEqual('cp1251', sys.stdout.encoding)
        self.assertEqual('cp1251', sys.stderr.encoding)

    def test_environ(self):
        os.environ = {'BLOGGERTOOL_ENCODING': 'cp866'}
        setup_encoding(None)
        self.assertEqual('cp866', sys.stdout.encoding)
        self.assertEqual('cp866', sys.stderr.encoding)


class TestOutput(unittest.TestCase):
    def setUp(self):
        self.s = StringIO()
        self.out = Output(self.s, 'utf-8')

    def test_ctor(self):
        self.assertEqual(self.out.file, self.s)
        self.assertEqual(self.out.name, '<string>')
        self.assertEqual(self.out.encoding, 'utf-8')

    def test_close(self):
        self.assertFalse(self.out.closed)
        self.out.close()
        self.assertTrue(self.out.closed)

    def test_fileno(self):
        # don't test self.out because StringIO has no fileno member
        # don't use stdout because can be overriden by nosetests
        out = Output(sys.stderr, 'utf-8')
        self.assertEqual(2, out.fileno())

    def test_isatty(self):
        self.assertFalse(self.out.isatty())
        out = Output(sys.stderr, 'utf-8')
        self.assertTrue(out.isatty())

    def test_write_str(self):
        self.out.write('string')
        val = self.s.getvalue()
        self.assertEqual('string', val)

    def test_write_russian_str(self):
        self.out.write('строка')
        val = self.s.getvalue()
        self.assertEqual('строка', val)

    def test_write_unicode(self):
        self.out.write(u'string')
        val = self.s.getvalue()
        self.assertEqual('string', val)

    def test_write_russian_unicode(self):
        self.out.write(u'строка')
        val = self.s.getvalue()
        self.assertEqual('строка', val)

    def test_writelines(self):
        self.out.writelines(['a', 'b', 'c'])
        val = self.s.getvalue()
        self.assertEqual('abc', val)
