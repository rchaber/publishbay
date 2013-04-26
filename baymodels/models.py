from boilerplate import models
from google.appengine.ext import ndb
from config import utils
from google.appengine.api import users


from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import google.appengine.api.images as images

import urllib

joblist = utils.joblist
genres_fiction = utils.genres_fiction
genres_nonfiction = utils.genres_nonfiction


class ProDetails(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    username = ndb.ComputedProperty(lambda self: self.user.get().username)
    display_full_name = ndb.BooleanProperty(default=True)
    title = ndb.StringProperty()
    overview = ndb.TextProperty()
    english_level = ndb.IntegerProperty(choices=[0, 1, 2, 3, 4, 5])
    jobs = ndb.StringProperty(choices=joblist, repeated=True)
    profile_visibility = ndb.StringProperty(choices=['everyone', 'pb_users_only', 'hidden'])
    address1 = ndb.StringProperty()
    address2 = ndb.StringProperty()
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    zipcode = ndb.StringProperty()
    phone = ndb.StringProperty()
    picture_key = ndb.BlobKeyProperty()
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    updated_on = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get_by_userkey(cls, k):
        return cls.query(cls.user == k).get()

    @classmethod
    def list_all(cls):
        object_list = cls.query().fetch()
        return [[x.user.get().username, x.jobs] for x in object_list]

    @classmethod
    def user_jobs(cls, username):
        return cls.query(cls.username == username).get().jobs

    @classmethod
    def job_users(cls, job):
        obj_list = cls.query(cls.jobs == job).fetch()
        return [x.username for x in obj_list]


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, file_key):
        file_view = str(urllib.unquote(file_key))
        blob_info = blobstore.BlobInfo.get(file_view)
        self.send_blob(blob_info)


class PublishingHouse(ndb.Model):
    owner = ndb.KeyProperty(kind=models.User)
    name = ndb.StringProperty()
    tagline = ndb.StringProperty()
    description = ndb.TextProperty()
    logo_key = ndb.BlobKeyProperty()
    genres = ndb.StringProperty(choices=genres_fiction + genres_nonfiction, repeated=True)
    show_in_job_posts = ndb.BooleanProperty(default=False)
    partners = ndb.KeyProperty(kind=models.User, repeated=True)

    @classmethod
    def get_by_ownerkey(cls, k):
        return cls.query(cls.owner == k).get()


class BookProject(ndb.Model):
    author = ndb.KeyProperty(kind=models.User)
    title = ndb.StringProperty()
    publishingHouse = ndb.KeyProperty(kind=PublishingHouse)


class WorkingForProject(ndb.Model):
    worker = ndb.KeyProperty(kind=models.User)
    book_project = ndb.KeyProperty(kind=BookProject)
    working_as = ndb.StringProperty(choices=joblist, repeated=True)
    hired_on = ndb.DateTimeProperty(auto_now_add=True)
    total_value = ndb.IntegerProperty()
    already_paid = ndb.IntegerProperty()
    to_be_paid = ndb.ComputedProperty(lambda self: self.total_value - self.already_paid)


class PublishingHouseStaff(ndb.Model):
    house = ndb.KeyProperty(kind=PublishingHouse)
    employee = ndb.KeyProperty(kind=models.User)
    job = ndb.StringProperty(choices=joblist, repeated=True)
    exclusivity = ndb.BooleanProperty(default=False)
    currently_active = ndb.BooleanProperty(default=False)
    working_on_projects = ndb.KeyProperty(kind=BookProject, repeated=True)
    joined_on = ndb.DateTimeProperty(auto_now_add=True)
    terminated_on = ndb.DateTimeProperty()
