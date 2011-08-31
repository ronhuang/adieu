#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.dist import use_library
use_library('django', '1.2')

from django.utils import simplejson
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from models import Item, Vote


class CreateHandler(webapp.RequestHandler):

    def post(self):
        title = self.request.get('title')
        description = self.request.get('description')
        owner = int(self.request.get('uid'))

        # Check duplicate
        q = db.GqlQuery("SELECT * FROM Item WHERE title = :1", title)
        if q.count(1) > 0:
            self.response.out.write(simplejson.dumps({'result': 'duplicated', 'title': title}))
            return

        # Not duplicated
        item = Item(title=title, description=description, owner=owner)
        key = item.put()

        vote = Vote(item=item, owner=owner)
        vote.put()

        self.response.out.write(simplejson.dumps({'result': 'added', 'title': title, 'key': key.id()}))


class UpdateHandler(webapp.RequestHandler):

    def post(self):
        self.response.out.write(simplejson.dumps({'result': 'not_implemented'}))


class DestroyHandler(webapp.RequestHandler):

    def post(self, item_id):
        self.response.out.write(simplejson.dumps({'result': 'not_implemented'}))


class ShowHandler(webapp.RequestHandler):

    def get(self, item_key):
        food_key = int(item_key)
        item = Item.get_by_id(food_key)
        if item == None:
            self.response.out.write(simplejson.dumps({'result': 'not_exist', 'key': food_key}))
        else:
            food = {'key': food_key,
                    'title': item.title,
                    'description': item.description,
                    'owner': item.owner,
                    'date': item.date.strftime('%s'),
                    'votes': item.vote_set.count()}
            self.response.out.write(simplejson.dumps({'result': 'success', 'food': food}))


class ListHandler(webapp.RequestHandler):

    def get(self):
        foods = []

        items = db.GqlQuery("SELECT * FROM Item")

        for item in items:
            food = {'key': item.key().id(),
                    'title': item.title,
                    'description': item.description,
                    'owner': item.owner,
                    'date': item.date.strftime('%s'),
                    'votes': item.vote_set.count()}
            foods.append(food)

        self.response.out.write(simplejson.dumps({'result': 'success', 'foods': foods}))


def main():
    application = webapp.WSGIApplication([('/item/create', CreateHandler),
                                          ('/item/update', UpdateHandler),
                                          (r'/item/destroy/(.*)', DestroyHandler),
                                          (r'/item/show/(.*)', ShowHandler),
                                          ('/item/list', ListHandler),
                                          ],
                                         debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
