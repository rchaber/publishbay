# -*- coding: utf-8 -*-

"""
    A real simple app for using webapp2 with auth and session.

    It just covers the basics. Creating a user, login, logout
    and a decorator for protecting certain handlers.

    Routes are setup in routes.py and added in main.py
"""

# standard library imports
# import logging
# import time
# import urllib2
# import urllib

# related third party imports
# import webapp2
# from webapp2_extras.i18n import gettext as _

# local application/library specific imports

# from boilerplate import models
from boilerplate.lib.basehandler import BaseHandler
from boilerplate.lib.basehandler import user_required

# from google.appengine.ext import ndb
# from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

# from google.appengine.api import users
# from google.appengine.api import images

# from pprint import pprint as pprint

from baymodels import models as bmodels

import config.utils as utils


class BrowseContractorsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for browsing and searching contractors
    """

    @user_required
    def get(self):
        """
        Handles GET requests and paging. It doesn't uses cursors.
        Instead, it uses offset along with a paginate custom function to navigate through the results.
        """

        PAGE_SIZE = 5

        contractors = []
        params = {}
        items = []

        jobfilter = self.request.GET.getall('jobs')
        print jobfilter

        offset = 0

        new_page = self.request.GET.get('page')
        if new_page:
            new_page = int(new_page)
            offset = int(new_page - 1) * PAGE_SIZE
        else:
            new_page = 1

        if jobfilter:
            query = bmodels.ProDetails.query(bmodels.ProDetails.jobs.IN(jobfilter))
        else:
            query = bmodels.ProDetails.query()

        count = query.count()
        items = query.fetch(PAGE_SIZE, offset=offset)

        # the following line returns the equivalent to math.ceil(float), just saving from importing another lib
        number_of_pages = count/PAGE_SIZE if count % PAGE_SIZE == 0 else count/PAGE_SIZE + 1

        for i in items:
            d = {}
            d['profile_id'] = i.key.id()
            if i.display_full_name:
                d['name_to_display'] = i.name + ' ' + i.last_name
            else:
                d['name_to_display'] = i.name + ' ' + i.last_name[0] + '.'
            if i.picture_key != '':
                d['picture_url'] = '/serve/%s' % i.picture_key
            else:
                d['picture_url'] = ''
            d['title'] = i.title
            d['overview'] = i.overview.replace('\r\n', ' ').replace('\n', ' ')
            d['jobs'] = i.jobs
            contractors.append(d)

        paging = utils.pagination(number_of_pages, new_page, 5) if len(contractors) > 0 else [[1], 0]

        params['count'] = count
        params['contractors'] = contractors

        params['marks'] = paging[0] if len(paging) > 0 else 'no_marks'
        params['active'] = 'mark_' + str(paging[0][paging[1]]) if len(paging) > 0 else 'no_marks'
        params['previous'] = str(new_page - 1) if new_page > 1 else None
        params['next'] = str(new_page + 1) if new_page < number_of_pages else None

        params['joblist'] = utils.joblist
        params['jobs'] = jobfilter

        return self.render_template('browse/browse_contractors.html', **params)

    def post(self):
        pass


class ViewContractorsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for viewing contractors pages
    """

    @user_required
    def get(self):

        contractor_id = self.request.GET.get('pid')

        contractor = bmodels.ProDetails.get_by_id(int(contractor_id))

        params = {}

        q = bmodels.Marked_contractors.query(bmodels.Marked_contractors.user == self.user_key, bmodels.Marked_contractors.marked == contractor.key).get()

        params['marked'] = True if q else False

        if contractor:
            params['name'] = contractor.name
            params['last'] = contractor.last_name
            params['display_full_name'] = contractor.display_full_name
            if contractor.picture_key and contractor.picture_key != '':
                params['picture_url'] = '/serve/%s' % contractor.picture_key
            params['title'] = contractor.title
            params['overview'] = contractor.overview
            params['english_level'] = contractor.english_level
            params['joblist'] = contractor.jobs
            params['contractor_id'] = contractor_id
            c_contactinfo = bmodels.ContactInfo.get_by_userkey(contractor.user)
            params['city'] = c_contactinfo.city if c_contactinfo else ''
            params['state'] = c_contactinfo.state if c_contactinfo else ''

        return self.render_template('browse/view_contractor.html', **params)


class BrowseAuthorsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for browsing and searching authors
    """

    @user_required
    def get(self):
        """Handles GET requests to the paging by cursors sub-application.

        It doesn't uses cursors. Instead, it uses offset along with a paginate custom function to navigate through the results.
        """

        PAGE_SIZE = 5

        authors = []
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

        if genrefilter:
            query = bmodels.AuthorProfile.query(bmodels.AuthorProfile.genres.IN(genrefilter))
        else:
            query = bmodels.AuthorProfile.query()

        count = query.count()
        items = query.fetch(PAGE_SIZE, offset=offset)

        # the following line returns the equivalent to math.ceil(float), just saving from importing another lib
        number_of_pages = count/PAGE_SIZE if count % PAGE_SIZE == 0 else count/PAGE_SIZE + 1

        for i in items:
            d = {}
            d['author_id'] = i.key.id()
            if i.display_full_name:
                d['name_to_display'] = i.name + ' ' + i.last_name
            else:
                d['name_to_display'] = i.name + ' ' + i.last_name[0] + '.'
            # if i.picture_key != '':
            #     d['picture_url'] = '/serve/%s' % i.picture_key
            # else:
            #     d['picture_url'] = ''
            d['title'] = i.title
            d['overview'] = i.overview.replace('\r\n', ' ').replace('\n', ' ')
            d['genres'] = i.genres
            d['ghostwrites'] = i.ghostwrites
            authors.append(d)

        paging = utils.pagination(number_of_pages, new_page, 5) if len(authors) > 0 else [[1], 0]

        params['count'] = count
        params['authors'] = authors

        params['marks'] = paging[0] if len(paging) > 0 else 'no_marks'
        params['active'] = 'mark_' + str(paging[0][paging[1]]) if len(paging) > 0 else 'no_marks'
        params['previous'] = str(new_page - 1) if new_page > 1 else None
        params['next'] = str(new_page + 1) if new_page < number_of_pages else None

        params['genrelist_fiction'] = utils.genres_fiction
        params['genrelist_nonfiction'] = utils.genres_nonfiction
        params['genres'] = genrefilter

        return self.render_template('browse/browse_authors.html', **params)

    def post(self):
        pass


class ViewAuthorsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for viewing authors pages
    """

    @user_required
    def get(self):

        author_id = self.request.GET.get('aid')

        author = bmodels.AuthorProfile.get_by_id(int(author_id))

        params = {}

        q = bmodels.Marked_authors.query(bmodels.Marked_authors.user == self.user_key, bmodels.Marked_authors.marked == author.key).get()

        params['marked'] = True if q else False

        if author:
            params['name'] = author.name
            params['last'] = author.last_name
            params['display_full_name'] = author.display_full_name
            # if author.picture_key and author.picture_key != '':
            #     params['picture_url'] = '/serve/%s' % author.picture_key
            params['title'] = author.title
            params['overview'] = author.overview
            params['author_id'] = author_id
            params['genres'] = author.genres
            params['ghostwrites'] = author.ghostwrites
            params['pseudonyms'] = ', '.join(author.pseudonyms)

        return self.render_template('browse/view_author.html', **params)
