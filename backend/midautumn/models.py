from google.appengine.ext import db


class MidautumnObject(db.Model):
    title = db.StringProperty(required=True)
    owner = db.StringProperty(required=True)
    date = db.DateTimeProperty(required=True, auto_now_add=True)
