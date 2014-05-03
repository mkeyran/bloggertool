# remote.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from copy import deepcopy

from dateutil.parser import parse as dtparse
from dateutil.tz import tzutc, tzlocal

from gdata.blogger.client import BloggerClient as _BloggerClient
#from gdata.blogger.data import LABEL_SCHEME
from gdata.client import CaptchaChallenge, BadAuthentication
from gdata.blogger.data import BlogPost as _BlogPost

#from atom.data import Content

from bloggertool.__version__ import __version__
from bloggertool.exceptions import RemoteError


class Remote(object):
    POST_URL = 'http://www.blogger.com/feeds/%s/posts/default/%s'
    SOURCE = 'AndrewSvetlov-BloggerTool-%s' % __version__

    def __init__(self, email, passwd, blogid,
              captcha_token=None, captcha_response=None):
        self._blogid = blogid
        self._client = _BloggerClient()
        self._client.client_login(email,
                                  passwd,
                                  source=self.SOURCE,
                                  service='blogger',
                                  captcha_token=captcha_token,
                                  captcha_response=captcha_response)

    def get_blogs(self):
        return Blogs(self._client.get_blogs())

    def check_blogid(self):
        if not self._blogid:
            raise RemoteError("Set info blogid first")

    def get_posts(self):
        self.check_blogid()
        return Posts(self._client.get_posts(self._blogid))

    def get_post(self, postid):
        self.check_blogid()
        url = self.POST_URL % (self._blogid, postid)
        entry = self._client.get_feed(url, desired_class=_BlogPost)
        return Post(entry)

    def update_post(self, post):
        self._client.update(post._entry)
        return self.get_post(post.postid)

    def add_post(self, title, content, labels=None):
        self.check_blogid()
        post = Post(self._client.add_post(self._blogid,
                                          title, content, labels))
        return self.get_post(post.postid)


class Blogs(object):
    def __init__(self, feed):
        self._feed = feed

    @property
    def title(self):
        return self._feed.title.text

    def __len__(self):
        return len(self._feed.entry)

    def __iter__(self):
        return (Blog(entry) for entry in self._feed.entry)

    def __getitem__(self, index):
        return Blog(self._feed.entry[index])


class Blog(object):
    def __init__(self, entry):
        self._entry = entry

    @property
    def blogid(self):
        return self._entry.get_blog_id()

    @property
    def title(self):
        return self._entry.title.text


class Posts(object):
    def __init__(self, feed):
        self._feed = feed

    @property
    def title(self):
        return self._feed.title.text

    def __len__(self):
        return len(self._feed.entry)

    def __iter__(self):
        return (Post(entry) for entry in self._feed.entry)

    def __getitem__(self, index):
        return Post(self._feed.entry[index])


class Post(object):
    def __init__(self, entry):
        self._entry = entry

    @property
    def title(self):
        return self._entry.title.text

    def set_title(self, title):
        new_entry = deepcopy(self._entry)
        new_entry.title.text = title
        return Post(new_entry)

    @property
    def postid(self):
        return self._entry.get_post_id()

    @property
    def blogid(self):
        return self._entry.get_blog_id()

    @property
    def entryid(self):
        return self._entry.id.text

    @property
    def draft(self):
        ret = False
        if self._entry.control:
            draft = getattr(self._entry.control, 'draft', None)
            if draft is not None:
                ret = draft.text == 'yes'
        return ret

    @property
    def published(self):
        return dtparse(self._entry.published.text).astimezone(tzutc())

    @property
    def updated(self):
        return dtparse(self._entry.updated.text).astimezone(tzutc())

    @property
    def content(self):
        return self._entry.content.text

    def set_content(self, html):
        new_entry = deepcopy(self._entry)
        new_entry.content.text = html
        return Post(new_entry)

    @property
    def link(self):
        for link in self._entry.link:
            if link.rel == 'alternate':
                return link.href
        return None

    #def set_link(self, link):
    #    new_entry = deepcopy(self._entry)
    #    for link in new_entry.link:
    #        if link.rel == 'alternate':
    #            link.href = link
    #    return Post(new_entry)

    @property
    def labels(self):
        return set(c.term for c in self._entry.category)

    def set_labels(self, labels):
        new_entry = deepcopy(self._entry)
        del new_entry.category[:]
        for label in labels:
            new_entry.add_label(label)
        return Post(new_entry)


__all__ = ['CaptchaChallenge', 'BadAuthentication', 'Remote']
