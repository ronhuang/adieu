#!/usr/bin/env python
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import logging
from datetime import datetime, timedelta
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
        timestamp = self.request.get('timestamp')

        user = self.current_user
        query = db.GqlQuery("SELECT * FROM MidautumnObject WHERE title = :1", title)

        args = None

        if not user:
            args = {'result': 'not_authorized'}
        elif query.count(1) > 0:
            args = {'result': 'duplicated', 'title': title}
        else:
            mo = MidautumnObject(title=title, owner=user)
            mo.put()

            # fetch all objects after the timestamp
            # should include the one just posted
            query = MidautumnObject.all()
            query.filter('pubtime >', datetime.utcfromtimestamp(float(timestamp)))
            query.order('-pubtime')

            objects = []
            for obj in query:
                objects.append(obj.to_dict(current_user=user))

            # check achievements
            achievements = []
            achievements.extend(achievement.check_post(mo))

            args = {'result': 'success',
                    'objects': objects,
                    'achievements': achievements}

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(args))

    def get(self, key):
        mo = MidautumnObject.get_by_id(int(key))

        args = None

        if not mo:
            args = {'result': 'not_exist', 'key': key}
        else:
            args = {'result': 'success',
                    'objects': [mo.to_dict(current_user=self.current_user),]}

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(args))


class DeleteObjectHandler(BaseHandler):

    def post(self, key):
        user = self.current_user

        mo = MidautumnObject.get_by_id(int(key))

        args = None

        if not user:
            args = {'result': 'not_authorized'}
        elif not mo:
            args = {'result': 'not_exist', 'key': key}
        elif mo.owner.id != user.id:
            args = {'result': 'not_authorized'}
        else:
            mo.delete()
            args = {'result': 'success', 'key': key}

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(args))


class ObjectsHandler(BaseHandler):

    def get(self):
        cursor = self.request.get('cursor', None)

        args = None

        # load initial set of data
        query = MidautumnObject.all()
        query.order('-pubtime')
        if cursor:
            query.with_cursor(cursor)

        objects = []
        results = query.fetch(10)
        for obj in results:
            objects.append(obj.to_dict(current_user=self.current_user))

        args = {'result': 'success',
                'objects': objects,
                'cursor': query.cursor(),
                'more': len(objects) >= 10,
                }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(args))


class EdgeHandler(BaseHandler):

    def post(self):
        action = self.request.get('action', None)
        url = self.request.get('url', None)

        user = self.current_user
        mo = MidautumnObject.get_by_url(url)

        args = None

        if not user:
            args = {'result': 'not_authorized'}
        elif action not in ('create', 'remove'):
            args = {'result': 'unknown_action'}
        elif not url:
            args = {'result': 'missing_parameter'}
        elif not mo:
            args = {'result': 'invalid_parameter'}
        else:
            query = user.edge_set
            query.filter('url =', url)
            edge = query.get()
            if not edge:
                edge = FacebookEdge(owner=user, url=url, object=mo)
            if action == 'create':
                edge.connected = True
                edge.created = True
            else:
                edge.connected = False
                edge.removed = True
            edge.put()

            achievements = []
            achievements.extend(achievement.check_like(edge))

            args = {'result': 'success',
                    'achievements': achievements,
                    }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(args))


class CommentHandler(BaseHandler):

    def post(self):
        action = self.request.get('action', None)
        href = self.request.get('href', None)
        commentID = self.request.get('commentID', None)

        user = self.current_user
        mo = MidautumnObject.get_by_url(href)

        args = None

        if not user:
            args = {'result': 'not_authorized'}
        elif action not in ('create', 'remove'):
            args = {'result': 'unknown_action'}
        elif not href or not commentID:
            args = {'result': 'missing_parameter'}
        elif not mo:
            args = {'result': 'invalid_parameter'}
        else:
            query = user.comment_set
            query.filter('href =', href)
            query.filter('comment_id =', commentID)
            comment = query.get()

            if (action == 'create' and comment) or (action == 'remove' and not comment):
                args = {'result': 'invalid_state'}
            elif action == 'create':
                comment = FacebookComment(owner=user, href=href, comment_id=commentID, object=mo)
                comment.put()

                achievements = []
                achievements.extend(achievement.check_comment(comment))

                args = {'result': 'success',
                        'achievements': achievements,
                        }
            else:
                comment.delete()

                achievements = []
                achievements.extend(achievement.check_comment(owner=user))

                args = {'result': 'success',
                        'achievements': achievements,
                        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(args))


class VisitHandler(BaseHandler):

    def _handle_visit(self, user):
        # maintain continuous visit
        now = datetime.now()
        count = user.continuous_visit_count
        delta = now - user.continuous_visit_start
        df = timedelta(count)
        dt = timedelta(count + 1)
        if delta >= df and delta < dt:
            # advance count
            user.continuous_visit_count = count + 1
            user.put()
        elif delta >= dt:
            # continuous visit reset
            user.continuous_visit_start = now
            user.continuous_visit_count = 1
            user.put()
        else:
            # still on the same day
            pass

    def post(self):
        user = self.current_user

        args = None

        if not user:
            args = {'result': 'not_authorized'}
        else:
            self._handle_visit(user)

            achievements = achievement.check_continuous_visit(user)
            args = {'result': 'success',
                    'achievements': achievements
                    }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(args))


def main():
    actions = [
        ('/api/object', ObjectHandler),
        ('/api/object/([0-9]+)$', ObjectHandler),
        ('/api/object/([0-9]+)/delete', DeleteObjectHandler),
        ('/api/objects', ObjectsHandler),
        ('/api/edge', EdgeHandler),
        ('/api/comment', CommentHandler),
        ('/api/visit', VisitHandler),
        ]
    application = webapp.WSGIApplication(actions, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
