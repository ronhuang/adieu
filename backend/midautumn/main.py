#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import time
from datetime import datetime, timedelta, tzinfo
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from midautumn.models import MidautumnObject
from midautumn.handlers import BaseHandler


class HomeHandler(BaseHandler):
    def get(self):
        pagename = None
        args = None

        if self.current_user:
            # load initial set of data
            query = MidautumnObject.all()
            query.order('-pubtime')

            objects = []
            results = query.fetch(10)
            for obj in results:
                objects.append(obj.to_dict())

            pagename = 'home.html'
            args = {'profile_url': '/profile/%s' % self.current_user.id,
                    'profile_picture': 'http://graph.facebook.com/%s/picture?type=square' % self.current_user.id,
                    'profile_name': self.current_user.name,
                    'profile_id': self.current_user.id,
                    'objects': objects,
                    'cursor': query.cursor(),
                    'more': len(objects) >= 10,
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
        args = None

        mo = MidautumnObject.get_by_id(int(object_id))
        if mo == None:
            pagename = "object_not_found.html"
            args = {}
        else:
            pagename = "object.html"
            args = mo.to_dict()

            if self.current_user:
                args.update({'profile_url': '/profile/%s' % self.current_user.id,
                             'profile_picture': 'http://graph.facebook.com/%s/picture?type=square' % self.current_user.id,
                             'profile_name': self.current_user.name,
                             'profile_id': self.current_user.id,
                             })
            else:
                args.update({'profile_url': '#',
                             'profile_picture': '/img/blank.jpg',
                             'profile_name': '',
                             'profile_id': '',
                             })

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', pagename)
        self.response.out.write(template.render(path, args))


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
