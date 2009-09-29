#!/usr/bin/env python
import wsgiref.handlers
from google.appengine.ext import webapp


class MainHandler(webapp.RequestHandler):

  def get(self):
    self.response.out.write("""
<html>
  <head><title>Adieu</title></head>
  <body>
    <form action="/item/create" method="post">
      Title: <input type="text" name="title"/>
      Description: <input type="text" name="description"/>
      <input type="hidden" name="uid" value="1"/>
      <input type="submit" value="Add"/>
    </form>
    <form action="/vote/create" method="post">
      <input type="hidden" name="key" value="1"/>
      <input type="hidden" name="owner" value="1"/>
      <input type="hidden" name="cur_votes" value="1"/>
      <input type="submit" value="Vote"/>
    </form>
  </body>
</html>
""")


def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
