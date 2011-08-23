#!/usr/bin/env python
#
# Copyright (c) 2011 Ron Huang
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.


import os
import logging
import re
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.runtime import DeadlineExceededError
from django.utils import simplejson as json


class MainHandler(webapp.RequestHandler):
    def get(self):
        cookies = Cookies(self)
        token_key = None
        token_secret = None

        if "ulg" in cookies:
            token_key = cookies["ulg"]
        if "auau" in cookies:
            token_secret = cookies["auau"]

        # Check if authorized.
        user = None
        if token_key and token_secret:
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(token_key, token_secret)
            api = tweepy.API(auth)
            user = api.verify_credentials()

        page = None
        data = {}
        if user:
            page = 'timeline.html'
            data["screen_name"] = user.screen_name
            data["name"] = user.name
            data["year"] = user.created_at.year
            data["month"] = user.created_at.month
            data["day"] = user.created_at.day
        else:
            page = 'signin.html'

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'view', page)
        self.response.out.write(template.render(path, data))


class SignInHandler(webapp.RequestHandler):
    def get(self):
        # OAuth dance
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
        try:
            url = auth.get_authorization_url()
        except tweepy.TweepError, e:
            # Failed to get a request token
            msg = {'message': e}
            dirname = os.path.dirname(__file__)
            path = os.path.join(dirname, 'view', 'error.html')
            self.response.out.write(template.render(path, msg))
            return

        # store the request token for later use in the callback page.
        cookies = Cookies(self)
        cookies["jkiu"] = auth.request_token.key
        cookies["jhyu"] = auth.request_token.secret

        self.redirect(url)


class CallbackHandler(webapp.RequestHandler):
    def get(self):
        oauth_token = self.request.get("oauth_token", None)
        oauth_verifier = self.request.get("oauth_verifier", None)

        if oauth_token is None:
            # Invalid request!
            msg = {'message': 'Missing required parameters!'}
            dirname = os.path.dirname(__file__)
            path = os.path.join(dirname, 'view', 'error.html')
            self.response.out.write(template.render(path, msg))
            return

        # lookup the request token
        cookies = Cookies(self)
        token_key = None
        token_secret = None

        if "jkiu" in cookies:
            token_key = cookies["jkiu"]
            del cookies["jkiu"]
        if "jhyu" in cookies:
            token_secret = cookies["jhyu"]
            del cookies["jhyu"]

        if token_key is None or token_secret is None or oauth_token != token_key:
            # We do not seem to have this request token, show an error.
            msg = {'message': 'Invalid token!'}
            dirname = os.path.dirname(__file__)
            path = os.path.join(dirname, 'view', 'error.html')
            self.response.out.write(template.render(path, msg))
            return

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_request_token(token_key, token_secret)

        # fetch the access token
        try:
            auth.get_access_token(oauth_verifier)
        except tweepy.TweepError, e:
            # Failed to get access token
            msg = {'message': e}
            dirname = os.path.dirname(__file__)
            path = os.path.join(dirname, 'view', 'error.html')
            self.response.out.write(template.render(path, msg))
            return

        # remember on the user browser
        cookies["ulg"] = auth.access_token.key
        cookies["auau"] = auth.access_token.secret

        self.redirect("/")


class SignOutHandler(webapp.RequestHandler):
    def get(self):
        cookies = Cookies(self)
        del cookies["ulg"]
        del cookies["auau"]

        self.redirect("/")


class EventsHandler(webapp.RequestHandler):
    def get(self):
        etype = None
        eid = None

        m = re.match("/events/(\w+)/(\d+)", self.request.path)
        if m:
            etype = m.group(1)
            eid = m.group(2)

        if etype is None or eid is None:
            self.error(404)
            return

        if etype != "followers":
            self.error(404)
            return

        # Retrieve authentication
        cookies = Cookies(self)
        token_key = None
        token_secret = None

        if "ulg" in cookies:
            token_key = cookies["ulg"]
        if "auau" in cookies:
            token_secret = cookies["auau"]

        # Check if authorized.
        api = None
        me = None
        if token_key and token_secret:
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(token_key, token_secret)
            api = tweepy.API(auth)
            me = api.verify_credentials()
            if not me:
                api = None

        if not api:
            # Not authentication
            self.error(401)
            return

        events = []
        result = {'date-time-format': 'iso8601', 'events': events}

        # Add self.
        event = {
            'start': me.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'title': me.name,
            'image': me.profile_image_url,
            'link': "http://twitter.com/" + me.screen_name,
            'description': me.description,
            'caption': me.screen_name,
            'classname': 'self',
            }
        events.append(event)

        # Add others.
        try:
            for user in Cursor(api.friends).items():
                event = {
                    'start': user.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'title': user.name,
                    'image': user.profile_image_url,
                    'link': "http://twitter.com/" + user.screen_name,
                    'description': user.description,
                    'caption': user.screen_name,
                    }
                events.append(event)
        except tweepy.TweepError, e:
            self.error(503)
            return
        except DeadlineExceededError, e:
            # Serialize whatever we have.
            logging.warning("%s has %d entries, just retrieved %d" % (me.screen_name, me.friends_count, len(events)))
            pass

        self.response.out.write(json.dumps(result))


def main():
    actions = [
        ('/', IndexHandler),
        ('/home', HomeHandler),
        ('/logout', LogoutHandler),
        ('/.*', ProfileHandler),
        ]
    application = webapp.WSGIApplication(actions, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
