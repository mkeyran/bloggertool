import unittest

from bloggertool.exceptions import FileError


class TestFileError(unittest.TestCase):
    def test_ctor(self):
        ex = FileError('file', 'root', 'Role')

        self.assertEqual('file', ex.file)
        self.assertEqual('root', ex.root)
        self.assertEqual('Role', ex.role)

    def test___str__(self):
        ex = FileError('file', 'root', 'Role')
        self.assertEqual('Role file error', str(ex))
