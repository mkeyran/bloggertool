#!/usr/bin/env python

import os

from setuptools import setup, find_packages

requires = ['python-dateutil', 'trafaret', 'keyring', 'jinja2', 'gdata',
            'markdown', 'PyYAML', 'pyinotify', 'google-api-python-client']


def get_version(fname):
    with open(fname, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('\'"')


def check_licenses():
    CHK = "the MIT License: http://www.opensource.org/licenses/mit-license.php"
    for root, folders, files in os.walk('lib/bloggertool'):
        for f in files:
            if not f.endswith('.py'):
                continue
            if f[0] in '.#~':
                continue
            fname = os.path.join(root, f)
            if not CHK in open(fname).read():
                raise AssertionError("%s doesn't have license" % fname)


check_licenses()


def read_short_descr(fname):
    with open(fname, 'r') as f:
        line = f.readline()
        line = f.readline()
        assert '=====' in line
        line = f.readline().strip()
        while not line:
            line = f.readline().strip()

        ret = []
        while line:
            ret.append(line)
            line = f.readline().strip()
        return ' '.join(ret)


def read_long_descr(fname):
    with open(fname, 'r') as f:
        f.readline()
        assert '=====' in f.readline()
        line = f.readline().strip()
        while not line:
            line = f.readline().strip()

        while line:
            line = f.readline().strip()

        while not line:
            line = f.readline().strip()

        ret = []
        while '------' not in line:
            ret.append(line)
            line = f.readline().strip()

        return '\n'.join(ret)


setup(
    name='bloggertool',
    version=get_version('lib/bloggertool/__version__.py'),
    author='Andrew Svetlov',
    author_email='andrew.svetlov@gmail.com',
    url='https://github.com/asvetlov/bloggertool',
    description=read_short_descr('README.txt'),
    long_description=read_long_descr('README.txt'),
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English', # not translated yet
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        ],
    package_dir={'': 'lib'},
    packages=find_packages('lib'),
    entry_points = {
        'console_scripts':
            ['blog = bloggertool.main:main']
        },
    zip_safe=True,
    install_requires=requires,
    #test_require
    test_suite='nose.collector',
    #require
)
