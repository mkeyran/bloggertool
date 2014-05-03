# -*- encoding: utf-8 -*-

import datetime
import os
import unittest

from io import StringIO
from textwrap import dedent

import jinja2
import mocker

from bloggertool.exceptions import FileNotFoundError, UserCancel, ConfigError
from bloggertool.str_util import Template as _
from bloggertool.config import Config
from bloggertool.config.post import Post


class SampleIO(StringIO):
    def __init__(self):
        super(SampleIO, self).__init__()
        self.val = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.val = self.getvalue()
        return super(SampleIO, self).__exit__(exc_type, exc_val, exc_tb)


class TestPost(unittest.TestCase):
    def setUp(self):
        self.config = Config(os.path.abspath('project-root'))
        self.post = Post(self.config, 'name', 'dir/file.md')
        self.mocker = mocker.Mocker()
        self.log = self.mocker.mock()
        self.post.log = self.log
        self.fs = self.config.fs
        self.fs._impl = self.mocker.mock()
        self.ask = self.mocker.mock()
        self.config._ask = self.ask

    def test_ctor(self):
        self.assertEqual('name', self.post.name)
        self.assertEqual('dir/file.md', self.post.file)
        self.assertEqual('name', self.post.slug)

    def test_inner_html_path(self):
        with self.mocker:
            self.assertEqual('dir/file.inner.html', self.post.inner_html_path)

    def test_nice_html_path(self):
        with self.mocker:
            self.assertEqual('dir/file.html', self.post.nice_html_path)

    def test_is_html_fresh_inner_not_found(self):
        full_mdpath = os.path.join(self.fs.root, 'dir/file.md')
        full_inner_html_path = os.path.join(self.fs.root,
                                            'dir/file.inner.html')
        full_nice_html_path = os.path.join(self.fs.root, 'dir/file.html')

        self.post.config.fs._impl.exists(full_inner_html_path)
        self.mocker.result(False)

        with self.mocker:
            self.assertFalse(self.post.is_html_fresh)

    def test_is_html_fresh_nice_not_found(self):
        full_mdpath = os.path.join(self.fs.root, 'dir/file.md')
        full_inner_html_path = os.path.join(self.fs.root,
                                            'dir/file.inner.html')
        full_nice_html_path = os.path.join(self.fs.root, 'dir/file.html')

        self.post.config.fs._impl.exists(full_inner_html_path)
        self.mocker.result(True)
        self.post.config.fs._impl.exists(full_nice_html_path)
        self.mocker.result(False)

        with self.mocker:
            self.assertFalse(self.post.is_html_fresh)

    def test_is_html_fresh_is_ok(self):
        full_mdpath = os.path.join(self.fs.root, 'dir/file.md')
        full_inner_html_path = os.path.join(self.fs.root,
                                            'dir/file.inner.html')
        full_nice_html_path = os.path.join(self.fs.root, 'dir/file.html')

        self.post.config.fs._impl.exists(full_mdpath)
        self.mocker.result(True)
        self.post.config.fs._impl.exists(full_inner_html_path)
        self.mocker.result(True)
        self.mocker.count(2)
        self.post.config.fs._impl.exists(full_nice_html_path)
        self.mocker.result(True)
        self.mocker.count(2)
        self.post.config.fs._impl.getmtime(full_mdpath)
        self.mocker.result(5)
        self.post.config.fs._impl.getmtime(full_inner_html_path)
        self.mocker.result(10)
        self.post.config.fs._impl.getmtime(full_nice_html_path)
        self.mocker.result(15)

        with self.mocker:
            self.assertTrue(self.post.is_html_fresh)

    def test_is_html_fresh_is_inner_expired(self):
        full_mdpath = os.path.join(self.fs.root, 'dir/file.md')
        full_inner_html_path = os.path.join(self.fs.root,
                                            'dir/file.inner.html')
        full_nice_html_path = os.path.join(self.fs.root, 'dir/file.html')

        self.post.config.fs._impl.exists(full_mdpath)
        self.mocker.result(True)
        self.post.config.fs._impl.exists(full_inner_html_path)
        self.mocker.result(True)
        self.mocker.count(2)
        self.post.config.fs._impl.exists(full_nice_html_path)
        self.mocker.result(True)
        self.mocker.count(2)
        self.post.config.fs._impl.getmtime(full_mdpath)
        self.mocker.result(5)
        self.post.config.fs._impl.getmtime(full_inner_html_path)
        self.mocker.result(1)
        self.post.config.fs._impl.getmtime(full_nice_html_path)
        self.mocker.result(15)

        with self.mocker:
            self.assertFalse(self.post.is_html_fresh)

    def test_is_html_fresh_is_nice_expired(self):
        full_mdpath = os.path.join(self.fs.root, 'dir/file.md')
        full_inner_html_path = os.path.join(self.fs.root,
                                            'dir/file.inner.html')
        full_nice_html_path = os.path.join(self.fs.root, 'dir/file.html')

        self.post.config.fs._impl.exists(full_mdpath)
        self.mocker.result(True)
        self.post.config.fs._impl.exists(full_inner_html_path)
        self.mocker.result(True)
        self.mocker.count(2)
        self.post.config.fs._impl.exists(full_nice_html_path)
        self.mocker.result(True)
        self.mocker.count(2)
        self.post.config.fs._impl.getmtime(full_mdpath)
        self.mocker.result(5)
        self.post.config.fs._impl.getmtime(full_inner_html_path)
        self.mocker.result(6)
        self.post.config.fs._impl.getmtime(full_nice_html_path)
        self.mocker.result(1)

        with self.mocker:
            self.assertFalse(self.post.is_html_fresh)

    def test_refresh_html_fresh(self):
        mock = self.mocker.patch(self.post)
        mock.is_html_fresh
        self.mocker.result(True)
        with self.mocker:
            self.assertFalse(self.post.refresh_html())

    def test_refresh_html_cannot_change_published_slug(self):
        self.config.interactive = False
        full_mdpath = os.path.join(self.fs.root, 'dir/file.md')
        full_inner_html_path = os.path.join(self.fs.root,
                                            'dir/file.inner.html')
        full_nice_html_path = os.path.join(self.fs.root, 'dir/file.html')

        self.post.postid = 'some postid'

        self.post.config.fs._impl.exists(full_mdpath)
        self.mocker.result(True)
        self.mocker.count(1, None)

        self.config.fs._impl.open(full_mdpath, 'r', 'utf-8')
        self.mocker.result(StringIO(dedent(u"""\
            Title: Заголовок
            slug: article-slug
            labels: one, two
                    three
            Текст статьи
            """)))

        self.log.info('Generate html for name')

        with self.mocker:
            self.assertRaises(ConfigError, self.post.refresh_html, True)

    def test_refresh_html_with_template(self):
        self.config.interactive = None
        full_mdpath = os.path.join(self.fs.root, 'dir/file.md')
        full_inner_html_path = os.path.join(self.fs.root,
                                            'dir/file.inner.html')
        full_nice_html_path = os.path.join(self.fs.root, 'dir/file.html')

        self.post.title = self.post.slug = 'garbage'
        self.post.labels = ['garbage']

        self.ask(mocker.ANY, 'y/N/q')
        self.mocker.result('y')
        self.mocker.count(3)

        self.post.config.fs._impl.exists(full_mdpath)
        self.mocker.result(True)
        self.mocker.count(1, None)

        self.config.fs._impl.open(full_mdpath, 'r', 'utf-8')
        self.mocker.result(StringIO(dedent(u"""\
            Title: Заголовок
            slug: article-slug
            labels: one, two
                    three
            Текст статьи
            """)))

        inner_body = SampleIO()
        self.config.fs._impl.open(full_inner_html_path, 'w', 'utf-8')
        self.mocker.result(inner_body)

        nice_body = SampleIO()
        self.config.fs._impl.open(full_nice_html_path, 'w', 'utf-8')
        self.mocker.result(nice_body)

        self.config.info.template_dir = 'dir'
        self.config.info.template_file = 'tmpl'
        TEMPLATE = dedent("""\
            <html>
              <head>
                <title>{{title}}</title>
              </head>
              <body>
                <h1>{{title}}</h1>
                <p>Slug: {{slug}}</p>
                <p>Labels: {{labels}}</p>
                <hr>
                {{inner}}
              </body>
            </html>""")
        env = jinja2.Environment(loader=jinja2.DictLoader({'tmpl': TEMPLATE}))
        self.config.info._template_env = env

        self.log.info('Generate html for name')

        with self.mocker:
            self.assertTrue(self.post.refresh_html(True))
            self.assertEqual(u'Заголовок', self.post.title)
            self.assertEqual(u'article-slug', self.post.slug)
            self.assertEqual(', '.join(sorted(['one', 'two', 'three'])),
                             self.post.labels_str)
            self.assertEqual(u'<p>Текст статьи</p>', inner_body.val)
            expected = dedent(u"""\
                <html>
                  <head>
                    <title>Заголовок</title>
                  </head>
                  <body>
                    <h1>Заголовок</h1>
                    <p>Slug: article-slug</p>
                    <p>Labels: [u'one', u'three', u'two']</p>
                    <hr>
                    <p>Текст статьи</p>
                  </body>
                </html>""")
            self.assertEqual(expected, nice_body.val)

    def test_refresh_html_without_template(self):
        self.config.interactive = None
        full_mdpath = os.path.join(self.fs.root, 'dir/file.md')
        full_inner_html_path = os.path.join(self.fs.root,
                                            'dir/file.inner.html')
        full_nice_html_path = os.path.join(self.fs.root, 'dir/file.html')

        self.post.title = self.post.slug = 'garbage'
        self.post.labels = ['garbage']

        self.ask(mocker.ANY, 'y/N/q')
        self.mocker.result('y')
        self.mocker.count(3)

        self.post.config.fs._impl.exists(full_mdpath)
        self.mocker.result(True)
        self.mocker.count(1, None)

        self.config.fs._impl.open(full_mdpath, 'r', 'utf-8')
        self.mocker.result(StringIO(dedent(u"""\
            Title: Заголовок
            slug: article-slug
            labels: one, two
                    three
            Текст статьи
            """)))

        inner_body = SampleIO()
        self.config.fs._impl.open(full_inner_html_path, 'w', 'utf-8')
        self.mocker.result(inner_body)

        nice_body = SampleIO()
        self.config.fs._impl.open(full_nice_html_path, 'w', 'utf-8')
        self.mocker.result(nice_body)

        self.log.info('Generate html for name')
        self.log.warning("User settings has no template specified.\n"
                         "Use markdown output as html.")

        with self.mocker:
            self.assertTrue(self.post.refresh_html(True))
            self.assertEqual(u'Заголовок', self.post.title)
            self.assertEqual(u'article-slug', self.post.slug)
            self.assertEqual(', '.join(sorted(['one', 'two', 'three'])),
                             self.post.labels_str)
            self.assertEqual(u'<p>Текст статьи</p>', inner_body.val)
            self.assertEqual(u'<p>Текст статьи</p>', nice_body.val)

    def test_inner_html(self):
        full_mdpath = os.path.join(self.fs.root, 'dir/file.md')
        full_inner_html_path = os.path.join(self.fs.root,
                                            'dir/file.inner.html')
        full_nice_html_path = os.path.join(self.fs.root, 'dir/file.html')

        mock = self.mocker.patch(self.post)
        mock.refresh_html(False)
        self.mocker.result(False)

        self.post.config.fs._impl.exists(full_inner_html_path)
        self.mocker.result(True)
        self.mocker.count(1, None)

        self.config.fs._impl.open(full_inner_html_path, 'r', 'utf-8')
        self.mocker.result(StringIO(u'<p>Текст статьи</p>'))

        with self.mocker:
            self.assertEqual(u'<p>Текст статьи</p>',
                             self.post.inner_html())

    def test_nice_html(self):
        full_mdpath = os.path.join(self.fs.root, 'dir/file.md')
        full_inner_html_path = os.path.join(self.fs.root,
                                            'dir/file.inner.html')
        full_nice_html_path = os.path.join(self.fs.root, 'dir/file.html')

        mock = self.mocker.patch(self.post)
        mock.refresh_html(True)
        self.mocker.result(True)

        self.post.config.fs._impl.exists(full_nice_html_path)
        self.mocker.result(True)
        self.mocker.count(1, None)

        self.config.fs._impl.open(full_nice_html_path, 'r', 'utf-8')
        self.mocker.result(StringIO(u'<p>Текст статьи</p>'))

        with self.mocker:
            self.assertEqual(u'<p>Текст статьи</p>',
                             self.post.nice_html(True))

    def test_overwrite_attr_not_changed(self):
        self.post.slug = 'slug'

        with self.mocker:
            self.post.overwrite_attr('slug', 'slug')
            self.assertEqual('slug', self.post.slug)

    def test_overwrite_attr_empty(self):
        self.config.interactive = True
        self.post.slug = ''

        with self.mocker:
            self.post.overwrite_attr('slug', 'slug2')
            self.assertEqual('slug2', self.post.slug)

    def test_overwrite_attr_no(self):
        self.config.interactive = False
        self.post.slug = 'slug'
        self.log.warning(u'Skip slug modification for name')

        with self.mocker:
            self.post.overwrite_attr('slug', 'slug2')
            self.assertEqual('slug', self.post.slug)

    def test_overwrite_attr_yes(self):
        self.config.interactive = True
        self.post.slug = 'slug'

        with self.mocker:
            self.post.overwrite_attr('slug', 'slug2')
            self.assertEqual('slug2', self.post.slug)

    def test_overwrite_attr_interactive_yes(self):
        self.config.interactive = None
        self.post.slug = 'slug'

        self.ask(_("""
            New slug: slug2
            is different from existing slug: slug
            for post name
            Do you like to override?"""), 'y/N/q')
        self.mocker.result('y')

        with self.mocker:
            self.post.overwrite_attr('slug', 'slug2')
            self.assertEqual('slug2', self.post.slug)

    def test_overwrite_attr_interactive_no(self):
        self.config.interactive = None
        self.post.slug = 'slug'

        self.ask(_("""
            New slug: slug2
            is different from existing slug: slug
            for post name
            Do you like to override?"""), 'y/N/q')
        self.mocker.result('n')

        self.log.warning('Skip slug modification for name')

        with self.mocker:
            self.post.overwrite_attr('slug', 'slug2')
            self.assertEqual('slug', self.post.slug)

    def test_overwrite_attr_interactive_quit(self):
        self.config.interactive = None
        self.post.slug = 'slug'

        self.ask(_("""
            New slug: slug2
            is different from existing slug: slug
            for post name
            Do you like to override?"""), 'y/N/q')
        self.mocker.result('q')

        with self.mocker:
            self.assertRaises(UserCancel, self.post.overwrite_attr,
                              'slug', 'slug2')

    def fill_post(self):
        self.post.title = 'Post Title'
        self.post.link = 'link'
        self.post.labels = ['a', 'b']
        self.post.postid = 'postid'
        #self.localstamp = datetime.datetime(2011, 2, 21, 22, 32, 05)

    def test_info_list_not_changed_short(self):
        self.fill_post()
        self.post.changed = False

        with self.mocker:
            self.assertEqual('name', self.post.info_list(False))

    def test_info_list_changed_short(self):
        self.fill_post()
        self.post.changed = True

        with self.mocker:
            self.assertEqual('*name', self.post.info_list(False))

    def test_info_list_not_changed_long(self):
        self.fill_post()
        self.post.changed = False

        with self.mocker:
            self.assertEqual(dedent("""\
                name
                    title: Post Title
                    link: link
                    slug: name
                    labels: a, b
                    postid: postid
                    published: None
                    updated: None
                    localstamp: None"""), self.post.info_list(True))

    def test_info_list_changed_long(self):
        self.fill_post()
        self.post.changed = True

        with self.mocker:
            self.assertEqual(dedent("""\
                *name
                    title: Post Title
                    link: link
                    slug: name
                    labels: a, b
                    postid: postid
                    published: None
                    updated: None
                    localstamp: None"""), self.post.info_list(True))
