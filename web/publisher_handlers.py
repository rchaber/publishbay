# -*- coding: utf-8 -*-

"""
    A real simple app for using webapp2 with auth and session.

    It just covers the basics. Creating a user, login, logout
    and a decorator for protecting certain handlers.

    Routes are setup in routes.py and added in main.py
"""

# standard library imports
import logging
import time
import urllib2
import urllib

# related third party imports
# import webapp2
from webapp2_extras.i18n import gettext as _

# local application/library specific imports

# from boilerplate import models
from boilerplate.lib.basehandler import BaseHandler
from boilerplate.lib.basehandler import user_required

# from google.appengine.ext import ndb
# from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

# from google.appengine.api import users
# from google.appengine.api import images
from google.appengine.api import search

from pprint import pprint as pprint

from baymodels import models as bmodels

import config.utils as utils


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

        return self.render_template('publisher/view_saved_contractors.html', **params)


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

        return self.render_template('publisher/view_saved_authors.html', **params)


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

        return self.render_template('publisher/view_saved_publishinghouses.html', **params)


class SubmissionsReceivedHandler(BaseHandler):

    @user_required
    def get(self):

        status_filter = self.request.GET.get('status_filter') if self.request.GET.get('status_filter') else 'unread'

        phouse_key = bmodels.PublishingHouse.get_by_ownerkey(self.user_key).key

        if status_filter == 'unread':
            submissions_fetch = bmodels.ManuscriptSubmission.query(bmodels.ManuscriptSubmission.publishinghouse == phouse_key, bmodels.ManuscriptSubmission.status == 'sent').fetch()
            status_filter_label = 'Status: unread'
        elif status_filter == 'read':
            submissions_fetch = bmodels.ManuscriptSubmission.query(bmodels.ManuscriptSubmission.publishinghouse == phouse_key, bmodels.ManuscriptSubmission.status == 'read').fetch()
            status_filter_label = 'Status: read'
        elif status_filter == 'rejected':
            submissions_fetch = bmodels.ManuscriptSubmission.query(bmodels.ManuscriptSubmission.publishinghouse == phouse_key, bmodels.ManuscriptSubmission.status == 'rejected').fetch()
            status_filter_label = 'Status: rejected'
        elif status_filter == 'accepted':
            submissions_fetch = bmodels.ManuscriptSubmission.query(bmodels.ManuscriptSubmission.publishinghouse == phouse_key, bmodels.ManuscriptSubmission.status == 'accepted').fetch()
            status_filter_label = 'Status: accepted'
        elif status_filter == 'acquired':
            submissions_fetch = bmodels.ManuscriptSubmission.query(bmodels.ManuscriptSubmission.publishinghouse == phouse_key, bmodels.ManuscriptSubmission.status == 'acquired').fetch()
            status_filter_label = 'Status: acquired'
        else:
            submissions_fetch = bmodels.ManuscriptSubmission.query(bmodels.ManuscriptSubmission.publishinghouse == phouse_key).fetch()
            status_filter_label = 'All'

        params = {}
        submissions = []
        for item in submissions_fetch:
            d = {}
            manuscript = item.manuscript.get()
            author = bmodels.AuthorProfile.get_by_userkey(item.user)
            d['submission_id'] = item.key.id()
            d['manuscript_title'] = manuscript.title
            d['author'] = author.name + ' ' + author.last_name
            d['author_id'] = author.key.id()
            if item.status == 'sent':
                d['status'] = 'unread'
            else:
                d['status'] = item.status
            d['coverletter'] = 'True' if (item.coverletter and item.coverletter != '') else 'False'
            d['submitted_on'] = item.submitted_on.strftime('%Y-%m-%d %H:%M')
            d['status_updated_on'] = item.updated_on.strftime('%Y-%m-%d %H:%M')
            submissions.append(d)

        params['status_filter'] = status_filter
        params['status_filter_label'] = status_filter_label
        params['submissions'] = submissions

        return self.render_template('publisher/submissions_received.html', **params)


class ReadSubmissionHandler(BaseHandler):

    @user_required
    def get(self):

        submission_id = self.request.GET.get('submission_id')
        submission = bmodels.ManuscriptSubmission.get_by_id(int(submission_id))

        if submission.status == 'sent':
            try:
                submission.status = 'read'
                submission.put()
            except:
                pass

        manuscript = submission.manuscript.get()
        params = {}

        params['submission_id'] = submission_id
        params['author'] = submission.manuscript.get().user.get().name + ' ' + submission.manuscript.get().user.get().last_name
        params['author_id'] = submission.manuscript.get().author.id()
        params['coverletter'] = submission.coverletter
        params['title'] = manuscript.title
        params['tagline'] = manuscript.tagline
        params['summary'] = manuscript.summary
        params['sample'] = manuscript.sample
        params['genres'] = manuscript.genres
        params['co_authors'] = ', '.join(manuscript.co_authors)
        params['submitted_on'] = submission.submitted_on.strftime('%Y-%m-%d')
        params['status_updated_on'] = submission.updated_on.strftime('%Y-%m-%d %H:%M')

        return self.render_template('publisher/read_submission.html', **params)

"""
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
    uploaded_on = ndb.DateTimeProperty(auto_now_add=True)
    updated_on = ndb.DateTimeProperty(auto_now=True)
"""