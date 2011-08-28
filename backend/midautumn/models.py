#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


import time
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

    # for serialization
    def to_dict(self):
        localtime = self.pubtime + timedelta(hours=8)
        fmt = None
        if localtime.hour < 12:
            fmt = "%Y年%m月%d號 上午%I:%M:%S"
        else:
            fmt = "%Y年%m月%d號 下午%I:%M:%S"

        uid = self.owner.id
        relative_url = '/object/%s' % self.key().id()

        return {'owner_picture': 'http://graph.facebook.com/%s/picture?type=square' % uid,
                'title': self.title,
                'pubtime_iso8601': self.pubtime.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'pubtime_local': localtime.strftime(fmt),
                'timestamp': int(time.mktime(self.pubtime.timetuple())),
                'relative_url': relative_url,
                'absolute_url': 'http://midautumn.ronhuang.org/%s' % relative_url,
                }


class FacebookEdge(db.Model):
    owner = db.ReferenceProperty(FacebookUser, collection_name='edge_set', required=True)
    url = db.StringProperty(required=True)
    connected = db.BooleanProperty()
    created = db.BooleanProperty()
    removed = db.BooleanProperty()


class FacebookComment(db.Model):
    owner = db.ReferenceProperty(FacebookUser, collection_name='comment_set', required=True)
    href = db.StringProperty(required=True)
    comment_id = db.StringProperty(required=True)
