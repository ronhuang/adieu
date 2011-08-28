#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


import time
import re
from google.appengine.ext import db
from datetime import timedelta


class FacebookUser(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    continuous_visit_start = db.DateTimeProperty(auto_now_add=True)
    continuous_visit_count = db.IntegerProperty(required=True, default=1)


# UserAchievement is moved to achievement.py


class MidautumnObject(db.Model):
    title = db.StringProperty(required=True)
    owner = db.ReferenceProperty(FacebookUser, collection_name='object_set', required=True)
    pubtime = db.DateTimeProperty(required=True, auto_now_add=True)

    @staticmethod
    def get_by_url(url):
        if not url:
            return
        # url is expect to be http://example.com/object/<key>
        matches = re.search(r'/object/(?P<key>[0-9]+)', url)
        if not matches:
            return
        key = matches.group('key')
        return MidautumnObject.get_by_id(int(key))

    # for serialization
    def to_dict(self, details=False, current_user=None):
        localtime = self.pubtime + timedelta(hours=8)
        fmt = None
        if localtime.hour < 12:
            fmt = "%Y年%m月%d號 上午%I:%M:%S"
        else:
            fmt = "%Y年%m月%d號 下午%I:%M:%S"

        uid = self.owner.id
        relative_url = '/object/%s' % self.key().id()

        result = {'owner_picture': 'http://graph.facebook.com/%s/picture?type=square' % uid,
                  'title': self.title,
                  'pubtime_iso8601': self.pubtime.strftime('%Y-%m-%dT%H:%M:%SZ'),
                  'pubtime_local': localtime.strftime(fmt),
                  'timestamp': int(time.mktime(self.pubtime.timetuple())),
                  'relative_url': relative_url,
                  'absolute_url': 'http://midautumn.ronhuang.org' + relative_url,
                  }

        if details:
            query = self.edge_set
            query.filter('connected =', True)
            result['like_count'] = query.count()

            query = self.comment_set
            result['comment_count'] = query.count()

        if current_user:
            if current_user.id == self.owner.id:
                result['modifiable'] = True

        return result


class FacebookEdge(db.Model):
    owner = db.ReferenceProperty(FacebookUser, collection_name='edge_set', required=True)
    object = db.ReferenceProperty(MidautumnObject, collection_name='edge_set', required=True)
    url = db.StringProperty(required=True)
    connected = db.BooleanProperty()
    created = db.BooleanProperty()
    removed = db.BooleanProperty()


class FacebookComment(db.Model):
    owner = db.ReferenceProperty(FacebookUser, collection_name='comment_set', required=True)
    object = db.ReferenceProperty(MidautumnObject, collection_name='comment_set', required=True)
    href = db.StringProperty(required=True)
    comment_id = db.StringProperty(required=True)
