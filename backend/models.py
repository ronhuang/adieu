from google.appengine.ext import db


class Item(db.Model):
    title = db.StringProperty(required=True)
    description = db.StringProperty(multiline=True)
    owner = db.IntegerProperty(required=True)
    date = db.DateTimeProperty(required=True, auto_now_add=True)
    image = db.BlobProperty()


class Comment(db.Model):
    item = db.ReferenceProperty(Item, required=True)
    content = db.StringProperty(required=True, multiline=True)
    owner = db.IntegerProperty(required=True)
    date = db.DateTimeProperty(required=True, auto_now_add=True)


class Vote(db.Model):
    item = db.ReferenceProperty(Item, required=True)
    owner = db.IntegerProperty(required=True)
    date = db.DateTimeProperty(required=True, auto_now_add=True)
