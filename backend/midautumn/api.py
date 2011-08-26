#!/usr/bin/env python
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import logging
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.runtime import DeadlineExceededError
from google.appengine.ext import db
from django.utils import simplejson as json
from midautumn.models import MidautumnObject
import midautumn.achievement as achievement
from midautumn.handlers import BaseHandler


class ObjectHandler(BaseHandler):

    def post(self):
        title = self.request.get('title')
        owner = self.request.get('owner')
        timestamp = self.request.get('timestamp')

        # Check duplicate
        q = db.GqlQuery("SELECT * FROM MidautumnObject WHERE title = :1", title)
        if q.count(1) > 0:
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps({'result': 'duplicated', 'title': title}))
            return

        # Not duplicated
        mo = MidautumnObject(title=title, owner=owner)
        mo.put()

        # fetch all objects after the timestamp
        # should include the one just posted
        q = MidautumnObject.all()
        q.filter('pubtime >', datetime.utcfromtimestamp(float(timestamp)))
        q.order('-pubtime')

        objects = []
        for obj in q:
            objects.append(obj.to_dict())

        # check achievements
        achievements = []
        achievements.extend(achievement.check_post(mo))

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({'result': 'success',
                                            'objects': objects,
                                            'achievements': achievements}))

    def get(self, key):
        mo = MidautumnObject.get_by_id(int(key))

        self.response.headers['Content-Type'] = 'application/json'

        if mo == None:
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps({'result': 'not_exist', 'key': key}))
        else:
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps({'result': 'success', 'objs': [mo.to_dict(),]}))


class ObjectsHandler(BaseHandler):

    def get(self):
        cursor = self.request.get('cursor', None)

        args = None

        if self.current_user:
            # load initial set of data
            query = MidautumnObject.all()
            query.order('-pubtime')
            if cursor:
                query.with_cursor(cursor)

            objects = []
            results = query.fetch(10)
            for obj in results:
                objects.append(obj.to_dict())

            args = {'result': 'success',
                    'profile_url': '/profile/%s' % self.current_user.id,
                    'profile_picture': 'http://graph.facebook.com/%s/picture?type=square' % self.current_user.id,
                    'profile_name': self.current_user.name,
                    'profile_id': self.current_user.id,
                    'objects': objects,
                    'cursor': query.cursor(),
                    'more': len(objects) >= 10,
                    }
        else:
            args = {'result': 'not_authorized'}

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(args))


def main():
    actions = [
        ('/api/object', ObjectHandler),
        ('/api/object/([0-9]+)$', ObjectHandler),
        ('/api/objects', ObjectsHandler),
        ]
    application = webapp.WSGIApplication(actions, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
