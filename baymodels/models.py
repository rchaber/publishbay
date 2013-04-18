from boilerplate import models
from google.appengine.ext import ndb


class ContactInfo(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    address1 = ndb.StringProperty()
    address2 = ndb.StringProperty()
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    zipcode = ndb.StringProperty()
    phone1 = ndb.StringProperty()
    phone2 = ndb.StringProperty()
    picture = ndb.BlobProperty()
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    updated_on = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get_by_userkey(cls, k):
        return cls.query(cls.user == k).get()


class ProfessionalDetails(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    resume = ndb.TextProperty()
    bio = ndb.TextProperty()
    shortstatement = ndb.StringProperty()
    longstatement = ndb.TextProperty()


class OccupationType(ndb.Model):
    name = ndb.StringProperty()

    @classmethod
    def list_all(cls):
        object_list = cls.query().fetch()
        list = [x.key.id() for x in object_list]
        return list

    @classmethod
    def key_by_name(cls, name):
        obj = cls.query(cls.name == name).fetch()
        return obj[0].key if len(obj) > 0 else None

    @classmethod
    def id_by_name(cls, name):
        obj = cls.query(cls.name == name).fetch()
        return obj[0].key.id() if len(obj) > 0 else None


class OccupationUsers(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    occupation = ndb.KeyProperty(kind=OccupationType)
    username = ndb.ComputedProperty(lambda self: self.user.get().username)
    occup_name = ndb.ComputedProperty(lambda self: self.occupation.get().name)

    @classmethod
    def list_all(cls):
        object_list = cls.query().fetch()
        list = [[x.username, x.occup_name] for x in object_list]
        return list

    @classmethod
    def user_occupations(cls, username):
        object_list = cls.query(cls.username == username).fetch()
        list = [x.occup_name for x in object_list]
        return list

    @classmethod
    def occupation_users(cls, occup_name):
        object_list = cls.query(cls.occup_name == occup_name).fetch()
        list = [x.username for x in object_list]
        return list
