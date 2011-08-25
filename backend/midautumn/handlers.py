#!/usr/bin/env python
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


import logging
import midautumn.facebook as facebook
from midautumn.models import FacebookUser
from google.appengine.ext import webapp
from midautumn.configs import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET
from django.utils import simplejson as json


class BaseHandler(webapp.RequestHandler):
    """Provides access to the active Facebook user in self.current_user

    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """
    @property
    def current_user(self):
        if not hasattr(self, "_current_user"):
            self._current_user = None
            cookie = facebook.get_signed_fb_request(
                self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
            if cookie:
                # Store a local instance of the user data so we don't need
                # a round-trip to Facebook on every request
                user = FacebookUser.get_by_key_name(cookie["uid"])
                if not user:
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    user = FacebookUser(key_name=str(profile["id"]),
                                        id=str(profile["id"]),
                                        name=profile["name"],
                                        profile_url=profile["link"],
                                        access_token=cookie["access_token"])
                    user.put()
                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                self._current_user = user
        return self._current_user
