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

        # removes user own publishing house
        query = query.filter(bmodels.ProDetails.user != self.user_key)

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

        # removes user own publishing house
        query = query.filter(bmodels.AuthorProfile.user != self.user_key)

        count = query.count()
        items = query.fetch(PAGE_SIZE, offset=offset)

        # the following line returns the equivalent to math.ceil(float), just saving from importing another lib
        number_of_pages = count/PAGE_SIZE if count % PAGE_SIZE == 0 else count/PAGE_SIZE + 1

        for i in items:
            manuscripts = []
            manuscripts_records = bmodels.Manuscript.query(bmodels.Manuscript.author == i.key, bmodels.Manuscript.display == 'pb_users').fetch()
            if manuscripts_records:
                manuscripts = [[m.title, m.key.id()] for m in manuscripts_records]
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
            d['freelance'] = i.freelance
            d['manuscripts'] = manuscripts
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

        manuscripts = []
        manuscripts_query = bmodels.Manuscript.query(bmodels.Manuscript.author == author.key, bmodels.Manuscript.display == 'pb_users').fetch()
        if manuscripts_query:
            manuscripts = [[m.title, m.key.id()] for m in manuscripts_query]

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
            params['manuscripts'] = manuscripts
            params['genres'] = author.genres
            params['ghostwrites'] = author.ghostwrites
            params['freelance'] = author.freelance
            params['pseudonyms'] = ', '.join(author.pseudonyms)

        return self.render_template('browse/view_author.html', **params)


class BrowsePublishingHousesHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for browsing and searching publishing houses
    """

    @user_required
    def get(self):
        """
        It doesn't uses cursors. Instead, it uses offset along with a paginate custom function to navigate through the results.
        """

        PAGE_SIZE = 5

        publishinghouses = []
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
            query = bmodels.PublishingHouse.query(bmodels.PublishingHouse.genres.IN(genrefilter))
        else:
            query = bmodels.PublishingHouse.query()

        # removes user own publishing house
        query = query.filter(bmodels.PublishingHouse.owner != self.user_key)

        count = query.count()
        items = query.fetch(PAGE_SIZE, offset=offset)

        # the following line returns the equivalent to math.ceil(float), just saving from importing another lib
        number_of_pages = count/PAGE_SIZE if count % PAGE_SIZE == 0 else count/PAGE_SIZE + 1

        for i in items:
            d = {}
            d['name'] = i.name
            d['publishinghouse_id'] = i.key.id()
            if i.logo_key != '':
                d['logo_url'] = '/serve/%s' % i.logo_key
            else:
                d['logo_url'] = ''
            d['tagline'] = i.tagline
            d['description'] = i.description.replace('\r\n', ' ').replace('\n', ' ')
            d['genres'] = i.genres
            d['unsolicited'] = i.unsolicited
            publishinghouses.append(d)

        paging = utils.pagination(number_of_pages, new_page, 5) if len(publishinghouses) > 0 else [[1], 0]

        params['count'] = count
        params['publishinghouses'] = publishinghouses

        params['marks'] = paging[0] if len(paging) > 0 else 'no_marks'
        params['active'] = 'mark_' + str(paging[0][paging[1]]) if len(paging) > 0 else 'no_marks'
        params['previous'] = str(new_page - 1) if new_page > 1 else None
        params['next'] = str(new_page + 1) if new_page < number_of_pages else None

        params['genrelist_fiction'] = utils.genres_fiction
        params['genrelist_nonfiction'] = utils.genres_nonfiction
        params['genres'] = genrefilter

        return self.render_template('browse/browse_publishinghouses.html', **params)

    def post(self):
        pass


class ViewPublishingHousesHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for viewing publishing houses pages
    """

    @user_required
    def get(self):

        publishinghouse_id = self.request.GET.get('phid')

        publishinghouse = bmodels.PublishingHouse.get_by_id(int(publishinghouse_id))

        params = {}

        q = bmodels.Marked_publishinghouses.query(bmodels.Marked_publishinghouses.user == self.user_key, bmodels.Marked_publishinghouses.marked == publishinghouse.key).get()

        params['marked'] = True if q else False

        if publishinghouse:
            params['name'] = publishinghouse.name
            params['tagline'] = publishinghouse.tagline
            params['description'] = publishinghouse.description
            if publishinghouse.logo_key and publishinghouse.logo_key != '':
                params['logo_url'] = '/serve/%s' % publishinghouse.logo_key
            params['publishinghouse_id'] = publishinghouse_id
            params['genres'] = publishinghouse.genres
            params['unsolicited'] = publishinghouse.unsolicited

        return self.render_template('browse/view_publishinghouse.html', **params)


class ViewManuscriptDetailsHandler(BaseHandler):

    @user_required
    def get(self):

        manuscript_id = self.request.GET.get('mid')

        print manuscript_id

        manuscript = bmodels.Manuscript.get_by_id(int(manuscript_id))
        author = manuscript.author.get()

        if author.display_full_name:
            author_display_name = '%s %s' % (author.name, author.last_name)
        else:
            author_display_name = '%s %s.' % (author.name, author.last_name[0])

        params = {}

        params['manuscript_id'] = manuscript_id
        params['author'] = [author_display_name, author.key.id()]
        params['title'] = manuscript.title
        params['tagline'] = manuscript.tagline
        params['summary'] = manuscript.summary
        params['co_authors'] = ', '.join(manuscript.co_authors)
        params['genres'] = manuscript.genres
        params['sample'] = manuscript.sample

        return self.render_template('/browse/view_manuscript_details.html', **params)


class BrowseManuscriptsHandler(BaseHandler):
    """
    Handler for browsing manuscripts
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

        query1 = bmodels.Manuscript.query(bmodels.Manuscript.display == 'pb_users')

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

        return self.render_template('/browse/browse_manuscripts.html', **params)


class ViewSavedContractorsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for viewing saved contractors
    """

    @user_required
    def get(self):
        """Handles GET requests to the paging by cursors sub-application.

        It doesn't uses cursors. Instead, it uses offset along with a paginate custom function to navigate through the results.
        """

        PAGE_SIZE = 10

        contractors = []
        params = {}
        items = []

        jobfilter = self.request.GET.getall('jobs')
        print jobfilter
        print len(jobfilter)

        q = bmodels.Marked_contractors.query(bmodels.Marked_contractors.user == self.user_key)
        count = q.count()
        items = q.fetch()

        for i in items:
            d = {}
            contractor = i.marked.get()
            d['profile_id'] = i.marked.get().key.id()
            if contractor.display_full_name:
                d['name_to_display'] = contractor.name + ' ' + contractor.last_name
            else:
                d['name_to_display'] = contractor.name + ' ' + contractor.last_name[0] + '.'
            if contractor.picture_key != '' and contractor.picture_key:
                d['picture_url'] = '/serve/%s' % contractor.picture_key
            else:
                d['picture_url'] = ''
            d['title'] = contractor.title
            d['overview'] = contractor.overview.replace('\r\n', ' ').replace('\n', ' ')
            d['jobs'] = contractor.jobs
            if len(jobfilter) > 0:
                if len(set(contractor.jobs).intersection(set(jobfilter))) > 0:
                    contractors.append(d)
            else:
                contractors.append(d)

        params['count'] = count
        params['filter_count'] = len(contractors)
        params['contractors'] = contractors

        params['joblist'] = utils.joblist
        params['jobs'] = jobfilter

        return self.render_template('browse/view_saved_contractors.html', **params)


class ViewSavedAuthorsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for viewing saved contractors
    """

    @user_required
    def get(self):
        """Handles GET requests to the paging by cursors sub-application.

        It doesn't uses cursors. Instead, it uses offset along with a paginate custom function to navigate through the results.
        """

        PAGE_SIZE = 10

        authors = []
        params = {}
        items = []

        genrefilter = self.request.GET.getall('genre')
        print genrefilter
        print len(genrefilter)

        q = bmodels.Marked_authors.query(bmodels.Marked_authors.user == self.user_key)
        count = q.count()
        items = q.fetch()

        for i in items:
            d = {}
            author = i.marked.get()
            picture_key = bmodels.BasicSettings.get_by_userkey(author.user)
            d['author_id'] = i.marked.get().key.id()
            if author.display_full_name:
                d['name_to_display'] = author.name + ' ' + author.last_name
            else:
                d['name_to_display'] = author.name + ' ' + author.last_name[0] + '.'
            if picture_key != '' and picture_key:
                d['picture_url'] = '/serve/%s' % picture_key
            else:
                d['picture_url'] = ''
            d['title'] = author.title
            d['overview'] = author.overview.replace('\r\n', ' ').replace('\n', ' ')
            d['genres'] = author.genres
            if len(genrefilter) > 0:
                if len(set(author.genres).intersection(set(genrefilter))) > 0:
                    authors.append(d)
            else:
                authors.append(d)

        params['count'] = count
        params['filter_count'] = len(authors)
        params['authors'] = authors

        params['genrelist_fiction'] = utils.genres_fiction
        params['genrelist_nonfiction'] = utils.genres_nonfiction
        params['genres'] = genrefilter

        return self.render_template('browse/view_saved_authors.html', **params)


class ViewSavedPublishingHousesHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for viewing saved publishing houses
    """

    @user_required
    def get(self):
        """
        It doesn't uses cursors. Instead, it uses offset along with a paginate custom function to navigate through the results.
        """

        PAGE_SIZE = 10

        publishinghouses = []
        params = {}
        items = []

        genrefilter = self.request.GET.getall('genre')

        q = bmodels.Marked_publishinghouses.query(bmodels.Marked_publishinghouses.user == self.user_key)
        count = q.count()
        items = q.fetch()

        for i in items:
            d = {}
            publishinghouse = i.marked.get()
            d['publishinghouse_id'] = i.marked.get().key.id()
            d['name'] = publishinghouse.name
            if publishinghouse.logo_key != '' and publishinghouse.logo_key:
                d['logo_url'] = '/serve/%s' % publishinghouse.logo_key
            else:
                d['logo_url'] = ''
            d['tagline'] = publishinghouse.tagline
            d['description'] = publishinghouse.description.replace('\r\n', ' ').replace('\n', ' ')
            d['genres'] = publishinghouse.genres
            if len(genrefilter) > 0:
                if len(set(publishinghouse.jobs).intersection(set(genrefilter))) > 0:
                    publishinghouses.append(d)
            else:
                publishinghouses.append(d)

        params['count'] = count
        params['filter_count'] = len(publishinghouses)
        params['publishinghouses'] = publishinghouses

        params['genrelist_fiction'] = utils.genres_fiction
        params['genrelist_nonfiction'] = utils.genres_nonfiction
        params['genres'] = genrefilter

        return self.render_template('browse/view_saved_publishinghouses.html', **params)


