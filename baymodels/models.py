from boilerplate import models

from google.appengine.ext import ndb
from config import utils
from google.appengine.api import users

import urllib

joblist = utils.joblist
genres_fiction = utils.genres_fiction
genres_nonfiction = utils.genres_nonfiction


class BasicSettings(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    display_full_name = ndb.BooleanProperty(default=True)
    picture_key = ndb.BlobKeyProperty()

    @classmethod
    def get_by_userkey(cls, k):
        return cls.query(cls.user == k).get()

    @classmethod
    def get_by_username(cls, u):
        return cls.query(cls.username == u).get()

    @property
    def username(self):
        return self.user.get().username

    @property
    def name(self):
        return self.user.get().name

    @property
    def last_name(self):
        return self.user.get().last_name


class ContactInfo(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    address1 = ndb.StringProperty()
    address2 = ndb.StringProperty()
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    zipcode = ndb.StringProperty()
    phone = ndb.StringProperty()
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    updated_on = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get_by_userkey(cls, k):
        return cls.query(cls.user == k).get()

    @classmethod
    def get_by_username(cls, u):
        return cls.query(cls.username == u).get()

    @property
    def username(self):
        return self.user.get().username

    @property
    def name(self):
        return self.user.get().name

    @property
    def last_name(self):
        return self.user.get().last_name


class PublishingHouse(ndb.Model):
    owner = ndb.KeyProperty(kind=models.User)
    name = ndb.StringProperty()
    tagline = ndb.StringProperty()
    description = ndb.TextProperty()
    logo_key = ndb.BlobKeyProperty()
    genres = ndb.StringProperty(repeated=True)
    show_in_job_posts = ndb.BooleanProperty(default=False)
    partners = ndb.KeyProperty(kind=models.User, repeated=True)
    unsolicited = ndb.BooleanProperty(default=True)

    @classmethod
    def get_by_ownerkey(cls, k):
        return cls.query(cls.owner == k).get()


class ProDetails(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    title = ndb.StringProperty()
    overview = ndb.TextProperty()
    english_level = ndb.IntegerProperty(choices=[0, 1, 2, 3, 4, 5])
    jobs = ndb.StringProperty(choices=joblist, repeated=True)
    profile_visibility = ndb.StringProperty(choices=['everyone', 'pb_users_only', 'hidden'])
    ph_contractor = ndb.KeyProperty(kind=PublishingHouse)
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    updated_on = ndb.DateTimeProperty(auto_now=True)

    @property
    def pid(self):
        return self.key.id()

    @property
    def username(self):
        return self.user.get().username

    @property
    def name(self):
        return self.user.get().name

    @property
    def last_name(self):
        return self.user.get().last_name

    @property
    def display_full_name(self):
        return BasicSettings.get_by_userkey(self.user).display_full_name

    @property
    def picture_key(self):
        return BasicSettings.get_by_userkey(self.user).picture_key

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


class AuthorProfile(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    title = ndb.StringProperty()
    pseudonyms = ndb.StringProperty(repeated=True)
    overview = ndb.TextProperty()
    ghostwrites = ndb.BooleanProperty(default=False)
    freelance = ndb.BooleanProperty(default=False)
    genres = ndb.StringProperty(repeated=True)
    ph_author = ndb.KeyProperty(kind=PublishingHouse)

    @classmethod
    def get_by_userkey(cls, k):
        return cls.query(cls.user == k).get()

    @property
    def name(self):
        return self.user.get().name

    @property
    def last_name(self):
        return self.user.get().last_name

    @property
    def display_full_name(self):
        return BasicSettings.get_by_userkey(self.user).display_full_name


class JobPost(ndb.Model):
    """
    fields:
    - Job (select)
    - Title (text)
    - description (textarea)
    - estimated duration (select: more than 6 months, 3 to 6 months, 1 to 3 months, less than 1 month, less than 1 week)
    - job post visibility (Public - All contractors will be able to see your job and apply to it.; Invitation-Only - Only contractors you invite will be able to view and apply to your job.)
    - attachment
    - estimated start date
    - looking to be staff member (can only work for this publishing house)
    """


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


class Conversation(ndb.Model):
    user_one = ndb.KeyProperty(kind=models.User)
    user_two = ndb.KeyProperty(kind=models.User)
    ip = ndb.StringProperty()
    time = ndb.DateTimeProperty(auto_now_add=True)


class Conversation_reply(ndb.Model):
    reply = ndb.TextProperty()
    user = ndb.KeyProperty(kind=models.User)
    ip = ndb.StringProperty()
    time = ndb.DateTimeProperty(auto_now_add=True)
    conversation = ndb.KeyProperty(kind=Conversation)


class Marked_contractors(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    marked = ndb.KeyProperty(kind=ProDetails)


class Marked_authors(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    marked = ndb.KeyProperty(kind=AuthorProfile)


class Marked_publishinghouses(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    marked = ndb.KeyProperty(kind=PublishingHouse)


class Manuscript(ndb.Model):
    author = ndb.KeyProperty(kind=AuthorProfile)
    user = ndb.KeyProperty(kind=models.User)
    title = ndb.StringProperty()
    tagline = ndb.StringProperty()
    summary = ndb.TextProperty()
    sample = ndb.TextProperty()
    genres = ndb.StringProperty(repeated=True)
    display = ndb.StringProperty(choices=['pb_users', 'submissions'])
    co_authors = ndb.StringProperty(repeated=True)
    ownership = ndb.BooleanProperty()
    full_manuscript_key = ndb.BlobKeyProperty()
    full_manuscript_filename = ndb.StringProperty()
    full_manuscript_uploaded_on = ndb.DateTimeProperty()
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    updated_on = ndb.DateTimeProperty(auto_now=True)


class ManuscriptSubmission(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    manuscript = ndb.KeyProperty(kind=Manuscript)
    publishinghouse = ndb.KeyProperty(kind=PublishingHouse)
    status = ndb.StringProperty(choices=['sent', 'read', 'rejected', 'accepted', 'pass', 'negotiating', 'canceled', 'acquired'])
    coverletter = ndb.TextProperty()
    responseletter = ndb.TextProperty()
    passresponseletter = ndb.TextProperty()
    submitted_on = ndb.DateTimeProperty(auto_now_add=True)
    updated_on = ndb.DateTimeProperty(auto_now=True)


class Marked_submissions(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    marked = ndb.KeyProperty(kind=ManuscriptSubmission)


class Coverletter(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    name = ndb.StringProperty()
    content = ndb.TextProperty()


class ResponseLetter(ndb.Model):
    user = ndb.KeyProperty(kind=models.User)
    name = ndb.StringProperty()
    content = ndb.TextProperty()
