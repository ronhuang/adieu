#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import time
from datetime import datetime, timedelta
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from midautumn.models import MidautumnObject, FacebookUser
from midautumn.achievement import UserAchievement
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
            args = {'objects': objects,
                    'cursor': query.cursor(),
                    'more': len(objects) >= 10,
                    }
            args.update(self.current_user_profile)
        else:
            pagename = 'register.html'
            args = None

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', pagename)
        self.response.out.write(template.render(path, args))


class ProfileHandler(BaseHandler):
    def get(self, key):
        args = {}
        pagename = None

        # check if requested profile exist
        profile = FacebookUser.get_by_key_name(key)
        if profile:
            # objects from requested profile
            query = profile.object_set
            query.order('pubtime')
            objects = []
            for obj in query:
                objects.append(obj.to_dict(details=True))
            args['objects'] = objects

            # achievements from requested profile
            query = profile.achievement_set
            query.order('created')
            achievements = []
            for achi in query:
                achievements.append(achi.to_dict())
            args['achievements'] = achievements

            # misc statistics
            query = profile.edge_set
            query.filter('connected =', True)
            args['liked_count'] = query.count()

            query = profile.edge_set
            query.filter('created =', True)
            args['liked_created_count'] = query.count()

            query = profile.edge_set
            query.filter('removed =', True)
            args['liked_removed_count'] = query.count()

            query = profile.comment_set
            args['comment_count'] = query.count()

            pagename = 'profile.html'
        else:
            pagename = 'profile_not_found.html'

        # current user related info
        args.update(self.current_user_profile)

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', pagename)
        self.response.out.write(template.render(path, args))


class ObjectHandler(BaseHandler):
    def get(self, key):
        pagename = None
        args = None

        mo = MidautumnObject.get_by_id(int(key))
        if mo == None:
            pagename = "object_not_found.html"
            args = {}
        else:
            pagename = "object.html"
            args = mo.to_dict()

        args.update(self.current_user_profile)

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', pagename)
        self.response.out.write(template.render(path, args))


class AchievementHandler(BaseHandler):
    def get(self, key):
        pagename = None
        args = None

        ua = UserAchievement.get_by_id(int(key))
        if ua == None:
            pagename = "achievement_not_found.html"
            args = {}
        else:
            pagename = "achievement.html"
            args = ua.to_dict()

        args.update(self.current_user_profile)

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
        ('/achievement/([0-9]+)$', AchievementHandler),
        ('/channel', ChannelHandler),
        ]
    application = webapp.WSGIApplication(actions, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
