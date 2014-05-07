# remote.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
from __future__ import print_function

import getpass
from copy import deepcopy

from dateutil.parser import parse as dtparse
from dateutil.tz import tzutc

from googleapiclient import discovery
from oauth2client import client
from oauth2client import keyring_storage
from oauth2client import tools
import httplib2
import transliterate

from bloggertool.exceptions import RemoteError


class Remote(object):

    def __init__(self, reset_credentials, blogid, secret_filename):
        self._blogid = blogid
        flow = client.flow_from_clientsecrets(
            secret_filename,
            scope="https://www.googleapis.com/auth/blogger",
            message=tools.message_if_missing(secret_filename))

        user = getpass.getuser()
        storage = keyring_storage.Storage('blogspot-tool-storage', user)
        if not reset_credentials:
            credentials = storage.get()
        else:
            credentials = None

        http = httplib2.Http()
        if credentials is None or credentials.invalid:
            flow.redirect_uri = client.OOB_CALLBACK_URN
            authorize_url = flow.step1_get_authorize_url()
            print('Please open', authorize_url)
            code = raw_input('Enter verification code: ').strip()

            try:
                credentials = flow.step2_exchange(code, http=http)
            except client.FlowExchangeError as e:
                raise RemoteError('Authentication has failed: %s' % e)

            storage.put(credentials)
            credentials.set_store(storage)


        http = credentials.authorize(http=http)

        # Construct a service object via the discovery service.
        service = discovery.build('blogger', 'v3', http=http)
        self._client = service

    def get_blogs(self):
        feed = self._client.blogs().listByUser(userId="self").execute()
        return Blogs(feed)

    def get_blog(self, blogid):
        feed = self._client.blogs().get(blogId=self._blogid).execute()
        return Blog(feed)

    def check_blogid(self):
        if not self._blogid:
            raise RemoteError("Set info blogid first")

    def get_posts(self):
        self.check_blogid()
        req = self._client.posts().list(blogId=self._blogid,
                                        status=['live', 'draft', 'scheduled'])
        ret = []
        while req is not None:
            rep = req.execute()
            ret.extend(rep.get('items', []))
            req = self._client.posts().list_next(req, rep)
        return Posts(ret)

    def get_post(self, postid):
        self.check_blogid()
        req = self._client.posts().get(blogId=self._blogid, postId=postid)
        rep = req.execute()
        return Post(rep)

    def update_post(self, post):
        self.check_blogid()
        req = self._client.posts().update(blogId=self._blogid,
                                          postId=post.postid,
                                          body=post._item)
        rep = req.execute()
        return Post(rep)

    def add_post(self, title, content, slug=None, labels=None):
        self.check_blogid()
        if slug is None:
            slug = transliterate.slugify(title)
        req = self._client.posts().insert(
            blogId=self._blogid,
            body={
                "title": slug,
                "content": content,
                "labels": labels if labels else []}
            )
        rep = req.execute()
        if slug != title:
            req = self._client.posts().patch(blogId=self._blogid,
                                             postId=rep['id'],
                                             body={"title": title})
            rep = req.execute()
        return Post(rep)


class Blogs(object):
    def __init__(self, items):
        self._items = items

    @property
    def title(self):
        return "Blogs"

    def __len__(self):
        return len(self._items['items'])

    def __iter__(self):
        return (Blog(item) for item in self._items['items'])

    def __getitem__(self, index):
        assert isinstance(index, int)
        return Blog(self._items['items'][index])


class Blog(object):
    def __init__(self, item):
        self._item = item

    @property
    def blogid(self):
        return self._item['id']

    @property
    def title(self):
        return self._item['name']

    @property
    def url(self):
        return self._item['url']


class Posts(object):
    def __init__(self, items):
        self._items = items

    @property
    def title(self):
        return "Posts"

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return (Post(item) for item in self._items)

    def __getitem__(self, index):
        assert isinstance(index, int)
        return Post(self._items[index])


class Post(object):
    def __init__(self, item):
        self._item = item

    @property
    def title(self):
        return self._item['title']

    def set_title(self, title):
        new_item = deepcopy(self._item)
        new_item['title'] = title
        return Post(new_item)

    @property
    def postid(self):
        return self._item['id']

    @property
    def blogid(self):
        return self._item['blog']['id']

    @property
    def draft(self):
        return self._item.get('status', 'live').lower() != 'live'

    @property
    def published(self):
        return dtparse(self._item['published']).astimezone(tzutc())

    @property
    def updated(self):
        return dtparse(self._item['updated']).astimezone(tzutc())

    @property
    def content(self):
        return self._item['content']

    def set_content(self, html):
        new_item = deepcopy(self._item)
        new_item['content'] = html
        return Post(new_item)

    @property
    def link(self):
        return self._item['url']

    @property
    def labels(self):
        return set(self._item['labels'])

    def set_labels(self, labels):
        new_item = deepcopy(self._item)
        new_item['labels'] = list(labels)
        return Post(new_item)


__all__ = ['Remote']
