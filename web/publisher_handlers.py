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

from tools import docs as docs
from tools import tools as tools

import config.utils as utils
import config.search_config as search_config


class ViewSavedContractorsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for viewing saved contractors
    """

    _DEFAULT_DOC_LIMIT = 5  # default number of search results to display per page.
    _OFFSET_LIMIT = 1000
    _NAV_LEN = 5

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
