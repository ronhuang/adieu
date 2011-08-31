#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.dist import use_library
use_library('django', '1.2')

from django.utils import simplejson
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from models import Item, Vote


def increase_vote(item, owner, cur_votes):
    if item == None:
        return cur_votes

    # Check duplicate
    q = db.GqlQuery("SELECT * FROM Vote WHERE item = :1 AND owner = :2", item, owner)
    if q.count() > 0:
        ret = """<span id="vote_result">%d</span> <span id="vote_message" style="color: #666666;">（已推薦過）</span>""" % (cur_votes, )
        return ret

    vote = Vote(owner=owner, item=item)
    vote.put()

    ret = """<span id="vote_result" style="color: #EB7F00; text-weight: bold">%d</span>""" % (item.vote_set.count(), )
    return ret


class CreateHandler(webapp.RequestHandler):

    def post(self):
        key = int(self.request.get('key'))
        owner = int(self.request.get('owner'))
        cur_votes = int(self.request.get('cur_votes'))

        ret = increase_vote(Item.get_by_id(key), owner, cur_votes)

        self.response.out.write(ret)


def main():
    application = webapp.WSGIApplication([('/vote/create', CreateHandler),
                                          ],
                                         debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
