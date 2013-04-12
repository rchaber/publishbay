from boilerplate import models
from google.appengine.ext import ndb


class UserProfile(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)


class OccupationType(ndb.Model):
    name = ndb.StringProperty()


class OccupationUsers(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    occupation = ndb.KeyProperty(kind=OccupationType)
