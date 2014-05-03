import collections
import contextlib
import os
import re
import shlex
import shutil
import string
import subprocess
import textwrap

from bloggertool.str_util import Template, NamespaceFormatter


class Executor(object):
    def __init__(self, blog_cmd, regr_folder):
        self.blog_cmd = blog_cmd
        self.regr_folder = os.path.abspath(regr_folder)
        self.cwd = [regr_folder]
        self.out = None
        self.retcode = None

    @contextlib.contextmanager
    def cd(self, arg):
        self.cwd.append(os.path.abspath(os.path.join(self.cwd[-1], arg)))
        yield
        self.cwd.pop()

    def get_cwd(self):
        return self.cwd[-1]

    def mkdir(self, arg):
        os.makedirs(os.path.join(self.cwd[-1], arg))

    def rmtree(self):
        folder = self.cwd[-1]
        if os.path.exists(folder):
            shutil.rmtree(folder)

    def write(self, fname, text):
        with open(self.full_name(fname), 'wb') as f:
            f.write(text)

    def read(self, fname):
        with open(self.full_name(fname), 'rb') as f:
            return f.read()

    def full_name(self, fname):
        return os.path.join(self.cwd[-1], fname)

    def go(self, args, retcode=0):
        """run blog with args, return (retcode, stdout)"""
        args_list = shlex.split(args)
        proc = subprocess.Popen([self.blog_cmd] + args_list,
                                cwd=self.get_cwd(),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.out, err = proc.communicate()
        self.retcode = proc.returncode
        if retcode is not None:
            if retcode != self.retcode:
                raise RuntimeError("RETCODE %s, EXPECTED %s\n%s" %
                                   (self.retcode,
                                    retcode,
                                    self.out))
        return self.out


class Q(Template):
    """Query, used for result check"""
    NS = NamespaceFormatter(collections.defaultdict(lambda: None))

    def format(__self, *__args, **__kwargs):
        return Q(__self.NS.vformat(__self, __args, __kwargs))

    def eq(self, other, strip=True):
        if strip:
            other = other.strip()
        if str(self) != str(other):
            raise RuntimeError(
                'Not Equals\n%s\n----------- != ------------\n%s'
                % (self, other))

    def __eq__(self, other):
        return self.eq(other)

    def __ne__(self, other):
        return not self.eq(other)

    def match(self, test, strip=True):
        if strip:
            test = test.strip()
        match = re.match(self, test, re.M)
        if match is None:
            raise RuntimeError("%s\n doesn't match pattern\n%s" % (test, self))
        return Match(match)

    def ifind(self, test, strip=True):
        if strip:
            test = test.strip()
        return (Match(m) for m in re.finditer(self, test, re.M))


class Match(object):
    def __init__(self, match):
        self.match = match

    def check(self, **kwargs):
        groups = self.match.groupdict()
        for name, val in kwargs:
            group = groups(name)
            Q(val) == group

    def __getitem__(self, key):
        return self.match.groupdict()[key]
