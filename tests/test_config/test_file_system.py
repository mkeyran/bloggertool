# -*- encoding: utf-8 -*-

import os
import shutil
import unittest

from bloggertool.config.file_system import FileSystem
from bloggertool.exceptions import FileNotFoundError, FileOutOfProject


class TestFileSystem(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        here = os.path.dirname(__file__)
        assert here
        self.tmpdir = os.path.join(here, 'tmp_dir')
        if not os.path.exists(self.tmpdir):
            os.makedirs(self.tmpdir)
        self.fs = FileSystem(self.tmpdir)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmpdir)

    def test_ctor(self):
        self.assertEqual(self.tmpdir, self.fs._root)

    def test_root(self):
        self.assertEqual(self.tmpdir, self.fs.root)

    def test_exists(self):
        rel_name = 'filename'
        fname = os.path.join(self.tmpdir, rel_name)
        self.assertFalse(self.fs.exists(rel_name))
        self.assertFalse(self.fs.exists(fname))

        with open(fname, 'w'):
            pass

        self.assertTrue(self.fs.exists(rel_name))
        self.assertTrue(self.fs.exists(fname))

    def test_getmtime(self):
        rel_name = 'filename'
        fname = os.path.join(self.tmpdir, rel_name)

        with open(fname, 'w'):
            pass
        mtime = os.path.getmtime(fname)
        self.assertEqual(mtime, self.fs.getmtime(rel_name))
        self.assertEqual(mtime, self.fs.getmtime(fname))

    def test_open_read(self):
        rel_name = 'filename'
        fname = os.path.join(self.tmpdir, rel_name)

        with open(fname, 'w') as f:
            f.write('Русский текст')

        with self.fs.open(rel_name, 'r') as f:
            content = f.read()
            self.assertEqual(unicode, type(content))
            self.assertEqual(u'Русский текст', content)

        with self.fs.open(fname, 'r') as f:
            content = f.read()
            self.assertEqual(unicode, type(content))
            self.assertEqual(u'Русский текст', content)

    def test_open_write(self):
        rel_name = 'filename'
        fname = os.path.join(self.tmpdir, rel_name)

        with self.fs.open(fname, 'w') as f:
            f.write(u'Русский текст')

        with open(fname, 'r') as f:
            content = f.read()
            self.assertEqual('Русский текст', content)

        with self.fs.open(rel_name, 'w') as f:
            f.write(u'Русский текст 2')

        with open(fname, 'r') as f:
            content = f.read()
            self.assertEqual('Русский текст 2', content)

    def test_replace_text(self):
        self.assertEqual('file.html', self.fs.replace_ext('file.md', '.html'))

    def test_check_existance(self):
        fname = os.path.join(self.tmpdir, 'filename')
        try:
            self.fs.check_existance(fname, role='TestFile')
            self.assertFalse(True, "Exception not caught")
        except FileNotFoundError, ex:
            self.assertEqual('TestFile', ex.role)
            self.assertEqual(fname, ex.file)

        with self.fs.open(fname, 'w') as f:
            f.write(u'123')

        self.fs.check_existance(fname, 'TestFile')
        self.assertTrue(True, "Exception not caught")

    def test_abs_path(self):
        rel_name = 'filename'
        fname = os.path.join(self.tmpdir, rel_name)

        self.assertRaises(FileNotFoundError, self.fs.abs_path, rel_name)
        self.assertEqual(fname, self.fs.abs_path(rel_name, True))

        with open(fname, 'w'):
            pass

        self.assertEqual(fname, self.fs.abs_path(rel_name))

    def test_rel_path_out_of_project(self):
        self.assertRaises(FileOutOfProject, self.fs.rel_path, '../file')

    def test_rel_path_does_not_exists(self):
        abs_path = os.path.join(self.tmpdir, 'filename')
        self.assertRaises(FileNotFoundError, self.fs.rel_path, abs_path)

    def test_rel_path(self):
        rel_name = 'dir/file'
        dir_name = os.path.join(self.tmpdir, 'dir')
        abs_path = os.path.join(self.tmpdir, rel_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(abs_path, 'w') as f:
            f.write('1')

        self.assertEqual(rel_name, self.fs.rel_path(abs_path))

    def test_rel_path_from_subdir(self):
        rel_name = 'dir/file'
        dir_name = os.path.join(self.tmpdir, 'dir')
        abs_path = os.path.join(self.tmpdir, rel_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(abs_path, 'w') as f:
            f.write('1')

        os.chdir(dir_name)
        #import pdb;pdb.set_trace()
        self.assertEqual(rel_name, self.fs.rel_path(abs_path))
