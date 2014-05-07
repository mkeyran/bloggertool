# encoding.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import codecs
import locale
import os
import sys


class Output(object):
    """Write-only file with embedded encoding"""
    def __init__(self, file, encoding):
        self.file = file
        self.name = getattr(file, 'name', '<string>')
        self.encoding = encoding
        self.writer = codecs.getwriter(self.encoding)(self.file,
                                                      'replace')

    def close(self):
        self.file.close()

    @property
    def closed(self):
        return self.file.closed

    def flush(self):
        self.file.flush()

    def fileno(self):
        return self.file.fileno()

    def isatty(self):
        if hasattr(self.file, 'isatty'):
            return self.file.isatty()
        else:
            return False

    def write(self, data):
        if isinstance(data, unicode):
            self.writer.write(data)
        else:
            self.file.write(data)

    def writelines(self, lines):
        for line in lines:
            self.write(line)


def setup_encoding(encoding=None):
    # determine encoding in order:
    # 1. directly set
    # 2. environmant variable
    # 3. encoding of stdout
    # 4. locale settings
    # 5. ascii

    if encoding is None:
        encoding = os.environ.get('BLOGGERTOOL_ENCODING')
        if encoding is None:
            encoding = getattr(sys.stdout, 'encoding', None)
            if encoding is None:
                # nothing found, use locale settings
                # please note, it's not the best choice for Windows
                # because user locale (cp1251) can differ from
                # preferred console locale (cp866)
                encoding = locale.getpreferredencoding()
                if encoding is None:
                    encoding = 'ascii'

    sys.stdout = Output(sys.stdout, encoding)
    sys.stderr = Output(sys.stderr, encoding)
