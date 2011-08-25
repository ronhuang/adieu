#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


from google.appengine.dist import use_library
use_library('django', '1.2')

import os
from datetime import datetime, timedelta, tzinfo
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from midautumn.models import MidautumnObject
from midautumn.handlers import BaseHandler
import midautumn.utils


TPE = midautumn.utils.TPE()


class HomeHandler(BaseHandler):
    def get(self):
        pagename = None
        args = None

        if self.current_user:
            # load initial set of data
            query = MidautumnObject.all()
            query.order('-pubtime')

            objects = []
            results = query.fetch(20)
            for obj in results:
                localtime = obj.pubtime + timedelta(hours=8)
                fmt = None
                if localtime.hour < 12:
                    fmt = "%Y年%m月%d號 上午%I:%M:%S"
                else:
                    fmt = "%Y年%m月%d號 下午%I:%M:%S"

                objects.append({'owner_picture': 'http://graph.facebook.com/%s/picture?type=square' % obj.owner,
                                'title': obj.title,
                                'pubtime_iso8601': obj.pubtime.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                'pubtime_local': localtime.strftime(fmt),
                                'relative_url': '/object/%s' % obj.key().id(),
                                'absolute_url': 'http://midautumn.ronhuang.org/object/%s' % obj.key().id(),
                                })

            pagename = 'home.html'
            args = {'profile_url': '/profile/%s' % self.current_user.id,
                    'profile_picture': 'http://graph.facebook.com/%s/picture?type=square' % self.current_user.id,
                    'profile_name': self.current_user.name,
                    'profile_id': self.current_user.id,
                    'objects': objects,
                    }
        else:
            pagename = 'register.html'
            args = None

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', pagename)
        self.response.out.write(template.render(path, args))


class ProfileHandler(BaseHandler):
    def get(self, profile_id):
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', 'profile.html')
        self.response.out.write(template.render(path, {'profile_id': profile_id}))


class ObjectHandler(BaseHandler):
    def get(self, object_id):
        pagename = None
        pagedata = None

        mo = MidautumnObject.get_by_id(int(object_id))
        if mo == None:
            pagename = "object_not_found.html"
            pagedata = {}
        else:
            pagename = "object.html"
            pagedata = {'title': mo.title, 'owner': mo.owner, 'pubtime': mo.pubtime, 'key': mo.key().id()}

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', pagename)
        self.response.out.write(template.render(path, pagedata))


class ChannelHandler(BaseHandler):
    def get(self):
        cache_expire = 60 * 60 * 24 * 365
        self.response.headers['Cache-Control'] = 'public, maxage=%d' % cache_expire
        self.response.headers['Expires'] = datetime.utcnow() + timedelta(days=365)

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', 'channel.html')
        self.response.out.write(template.render(path, {}))


def main():
    actions = [
        ('/', HomeHandler),
        ('/profile/([0-9]+)$', ProfileHandler),
        ('/object/([0-9]+)$', ObjectHandler),
        ('/channel', ChannelHandler),
        ]
    application = webapp.WSGIApplication(actions, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
