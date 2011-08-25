#!/usr/bin/env python
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


import os
from datetime import datetime, timedelta
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from midautumn.models import MidautumnObject
from midautumn.handlers import BaseHandler


class HomeHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.pagename = 'home.html'
            self.args = {}
        else:
            self.pagename = 'register.html'
            self.args = None

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', self.pagename)
        self.response.out.write(template.render(path, self.args))


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
