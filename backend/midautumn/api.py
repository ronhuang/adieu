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
from midautumn.models import MidautumnObject, FacebookEdge, FacebookComment
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
                    'objects': objects,
                    'cursor': query.cursor(),
                    'more': len(objects) >= 10,
                    }
            args.update(self.current_user_profile)
        else:
            args = {'result': 'not_authorized'}

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(args))


class EdgeHandler(BaseHandler):

    def post(self):
        action = self.request.get('action', None)
        url = self.request.get('url', None)

        args = None

        if not self.current_user:
            args = {'result': 'not_authorized'}
        elif action not in ('create', 'remove'):
            args = {'result': 'unknown_action'}
        elif not url:
            args = {'result': 'missing_parameter'}
        else:
            q = FacebookEdge.all()
            q.filter('owner =', self.current_user.id)
            q.filter('url =', url)
            edge = q.get()
            if not edge:
                edge = FacebookEdge(owner=self.current_user.id, url=url)
            if action == 'create':
                edge.connected = True
                edge.created = True
            else:
                edge.connected = False
                edge.removed = True
            edge.put()

            args = {'result': 'success'}

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(args))


class CommentHandler(BaseHandler):

    def post(self):
        action = self.request.get('action', None)
        href = self.request.get('href', None)
        commentID = self.request.get('commentID', None)

        args = None

        if not self.current_user:
            args = {'result': 'not_authorized'}
        elif action not in ('create', 'remove'):
            args = {'result': 'unknown_action'}
        elif not href or not commentID:
            args = {'result': 'missing_parameter'}
        else:
            q = FacebookComment.all()
            q.filter('owner =', self.current_user.id)
            q.filter('href =', href)
            q.filter('commentID =', commentID)
            edge = q.get()

            if (action == 'create' and edge) or (action == 'remove' and not edge):
                args = {'result': 'invalid_state'}
            elif action == 'create':
                edge = FacebookComment(owner=self.current_user.id, href=href, comment_id=commentID)
                edge.put()
                args = {'result': 'success'}
            else:
                edge.delete()
                args = {'result': 'success'}

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(args))


def main():
    actions = [
        ('/api/object', ObjectHandler),
        ('/api/object/([0-9]+)$', ObjectHandler),
        ('/api/objects', ObjectsHandler),
        ('/api/edge', EdgeHandler),
        ('/api/comment', CommentHandler),
        ]
    application = webapp.WSGIApplication(actions, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
