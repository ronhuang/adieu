#!/usr/bin/env python
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template


class HomeHandler(webapp.RequestHandler):
    def get(self):
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', 'home.html')
        self.response.out.write(template.render(path, {}))


class ProfileHandler(webapp.RequestHandler):
    def get(self, profile_id):
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', 'profile.html')
        self.response.out.write(template.render(path, {'profile_id': profile_id}))


class ObjectHandler(webapp.RequestHandler):
    def get(self, object_id):
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', 'object.html')
        self.response.out.write(template.render(path, {'object_id': object_id}))


def main():
    actions = [
        ('/', HomeHandler),
        ('/profile/([0-9]+)$', ProfileHandler),
        ('/object/([0-9]+)$', ObjectHandler),
        ]
    application = webapp.WSGIApplication(actions, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
