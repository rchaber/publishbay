# -*- coding: utf-8 -*-

# standard library imports
import logging
import time
import re

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
            manuscript = bmodels.Manuscript.get_by_id(int(manuscript_id))
            params['title'] = manuscript.title
            params['tagline'] = manuscript.tagline
            params['summary'] = manuscript.summary
            params['sample'] = re.sub(r'[\n\r]', r' ', manuscript.sample)
            params['genres_list'] = manuscript.genres
            params['display_manuscript'] = manuscript.display
            params['co_authors'] = ', '.join(manuscript.co_authors)
            params['ownership'] = False
            params['is_new_manuscript'] = False
            params['manuscript_id'] = manuscript_id
        else:
            params['title'] = ''
            params['tagline'] = ''
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

        manuscript_id = self.request.POST.get('manuscript_id')

        if manuscript_id:
            manuscript = bmodels.Manuscript.get_by_id(int(manuscript_id))
        else:
            manuscript = bmodels.Manuscript()

        co_authors = self.request.POST.get('co_authors')
        if co_authors:
            co_authors = co_authors.split(',')
            co_authors = [c.strip() for c in co_authors]
        else:
            co_authors = []

        try:
            message = ''
            manuscript.author = self.user_key
            manuscript.title = self.request.POST.get('title')
            manuscript.tagline = self.request.POST.get('tagline')
            manuscript.summary = self.request.POST.get('summary').replace('\r\r\n', '\r\n')
            manuscript.genres = checked_genres
            manuscript.display = self.request.POST.get('display_manuscript')
            manuscript.co_authors = co_authors
            manuscript.ownership = (self.request.POST.get('ownership') == "True")
            manuscript.sample = self.request.POST.get('wysiwyg').replace('\r\r\n', '\r\n')
            manuscript.put()
            message += " " + _('Your manuscript has been uploaded/updated.')
            self.add_message(message, 'success')
            self.redirect('/')

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error creating/updating manuscript: ' + e)
            message = _('Unable to create/update manuscript. Please try again later.')
            self.add_message(message, 'error')
            return self.get()


class MyManuscriptsHandler(BaseHandler):
    """
    Handler for listing my manuscripts
    """

    @user_required
    def get(self):

        PAGE_SIZE = 5

        manuscripts = []
        params = {}
        items = []

        genrefilter = self.request.GET.getall('genre')

        offset = 0

        new_page = self.request.GET.get('page')
        if new_page:
            new_page = int(new_page)
            offset = int(new_page - 1) * PAGE_SIZE
        else:
            new_page = 1

        query1 = bmodels.Manuscript.query(bmodels.Manuscript.author == self.user_key)

        if genrefilter:
            query = query1.filter(bmodels.Manuscript.genres.IN(genrefilter))
        else:
            query = query1

        count = query.count()
        items = query.fetch(PAGE_SIZE, offset=offset)

        # the following line returns the equivalent to math.ceil(float), just saving from importing another lib
        number_of_pages = count/PAGE_SIZE if count % PAGE_SIZE == 0 else count/PAGE_SIZE + 1

        for i in items:
            d = {}
            d['manuscript_id'] = i.key.id()
            d['title'] = i.title
            d['tagline'] = i.tagline
            d['summary'] = i.summary.replace('\r\n', ' ').replace('\n', ' ')
            d['genres'] = i.genres
            d['co_authors'] = ', '.join(i.co_authors)
            manuscripts.append(d)

        paging = utils.pagination(number_of_pages, new_page, 5) if len(manuscripts) > 0 else [[1], 0]

        params['count'] = count
        params['manuscripts'] = manuscripts

        params['marks'] = paging[0] if len(paging) > 0 else 'no_marks'
        params['active'] = 'mark_' + str(paging[0][paging[1]]) if len(paging) > 0 else 'no_marks'
        params['previous'] = str(new_page - 1) if new_page > 1 else None
        params['next'] = str(new_page + 1) if new_page < number_of_pages else None

        params['genrelist_fiction'] = utils.genres_fiction
        params['genrelist_nonfiction'] = utils.genres_nonfiction
        params['genres'] = genrefilter

        return self.render_template('/author/mymanuscripts.html', **params)


class ViewManuscriptHandler(BaseHandler):

    @user_required
    def get(self):

        manuscript_id = self.request.GET.get('mid')

        print manuscript_id

        manuscript = bmodels.Manuscript.get_by_id(int(manuscript_id))

        params = {}

        params['manuscript_id'] = manuscript_id
        params['title'] = manuscript.title
        params['tagline'] = manuscript.tagline
        params['summary'] = manuscript.summary
        params['co_authors'] = ', '.join(manuscript.co_authors)
        params['genres'] = manuscript.genres
        params['sample'] = manuscript.sample

        return self.render_template('/author/view_manuscript.html', **params)
