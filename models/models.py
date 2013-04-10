from webapp2_extras.appengine.auth.models import User
from google.appengine.ext import ndb


class Profile(ndb.Model):
    user = ndb.KeyProperty(kind=User)
    is_publisher = ndb.BooleanProperty(default=False)
    is_editor = ndb.BooleanProperty(default=False)
    is_designer = ndb.BooleanProperty(default=False)
    is_translator = ndb.BooleanProperty(default=False)
    is_author = ndb.BooleanProperty(default=False)
    is_proofreader = ndb.BooleanProperty(default=False)

