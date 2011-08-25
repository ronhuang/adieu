from google.appengine.ext import db
import datetime


SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)


class MidautumnObject(db.Model):
    title = db.StringProperty(required=True)
    owner = db.StringProperty(required=True)
    pubtime = db.DateTimeProperty(required=True, auto_now_add=True)

    # for serialization
    def to_dict(self):
        output = {}

        # key property is not in properties()
        output['key'] = self.key().id()

        for key, prop in self.properties().iteritems():
            value = getattr(self, key)

            if value is None or isinstance(value, SIMPLE_TYPES):
                output[key] = value
            elif isinstance(value, datetime.date):
                # Convert date/datetime to ISO 8601
                output[key] = value.strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                raise ValueError('Cannot encode ' + repr(prop))

        return output
