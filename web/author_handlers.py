# -*- coding: utf-8 -*-

# standard library imports
import logging
import time

# related third party imports
import webapp2
from webapp2_extras.i18n import gettext as _

# local application/library specific imports

from boilerplate import models
from boilerplate.lib.basehandler import BaseHandler
from boilerplate.lib.basehandler import user_required

# from google.appengine.ext import blobstore
# from google.appengine.ext.webapp import blobstore_handlers

# from google.appengine.api import users
# from google.appengine.api import images

# import urllib2
import urllib

# from pprint import pprint as pprint

from baymodels import models as bmodels

import config.utils as utils


"""
class Manuscript(ndb.Model):
    author = ndb.KeyProperty(kind=models.User)
    title = ndb.StringProperty()
    summary = ndb.TextProperty()
    sample = ndb.TextProperty()
    genres = ndb.StringProperty(repeated=True)
    display = ndb.StringProperty()
    co_authors = ndb.StringProperty(repeated=True)
    ownership = ndb.BooleanProperty()
    uploaded_on = ndb.DateTimeProperty(auto_now_add=True)
    updated_on = ndb.DateTimeProperty(auto_now=True)
"""


class EditManuscriptHandler(BaseHandler):
    """
    Handler for Add/Update Manuscript
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for adding/updating a manuscript """

        manuscript_id = self.request.GET.get('manuscript_id')

        params = {}

        if manuscript_id:
            manuscript = bmodels.Manuscript.get_by_id(self.request.GET.get('manuscript_id'))
            params['title'] = manuscript.title
            params['summary'] = manuscript.summary
            params['sample'] = manuscript.sample
            params['genres_list'] = manuscript.genres
            params['display_manuscript'] = manuscript.display
            params['co_authors'] = ', '.join(manuscript.co_authors)
            params['ownership'] = False
            params['is_new_manuscript'] = False
        else:
            params['title'] = ''
            params['summary'] = ''
            params['sample'] = ''
            params['genres_list'] = ''
            params['display_manuscript'] = 'pb_users'
            params['co_authors'] = ''
            params['ownership'] = False
            params['is_new_manuscript'] = True

        params['fiction_genres_left'] = utils.split_3cols(utils.genres_fiction)['left']
        params['fiction_genres_center'] = utils.split_3cols(utils.genres_fiction)['center']
        params['fiction_genres_right'] = utils.split_3cols(utils.genres_fiction)['right']
        params['nonfiction_genres_left'] = utils.split_3cols(utils.genres_nonfiction)['left']
        params['nonfiction_genres_center'] = utils.split_3cols(utils.genres_nonfiction)['center']
        params['nonfiction_genres_right'] = utils.split_3cols(utils.genres_nonfiction)['right']

        return self.render_template('/author/edit_manuscript.html', **params)

    def post(self):
        """ Get fields from POST dict """

        checked_genres = self.request.POST.getall('genres')

        pseudonyms = self.request.POST.get('pseudonyms').replace('  ', ' ').replace(' ,', ',').split(',')
        pseudonyms = [i.lstrip().rstrip() for i in pseudonyms]

        # k = models.User.get_by_id(long(self.user_id)).key
        print checked_genres
        print pseudonyms

        author_profile = bmodels.AuthorProfile.get_by_userkey(self.user_key)
        if not author_profile:
            author_profile = bmodels.AuthorProfile()
            author_profile.user = self.user_key

        try:
            message = ''
            author_profile.title = self.request.POST.get('title')
            author_profile.overview = self.request.POST.get('overview').replace('\r\r\n', '\r\n')
            author_profile.ghostwrites = (self.request.POST.get('ghostwrites') == "True")
            author_profile.genres = checked_genres
            author_profile.pseudonyms = pseudonyms
            author_profile.put()
            message += " " + _('Your author profile has been updated.')
            self.add_message(message, 'success')
            self.redirect('/settings/profile')

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error creating/updating author profile: ' + e)
            message = _('Unable to create/update author profile. Please try again later.')
            self.add_message(message, 'error')
            return self.get()