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
import math

# related third party imports
import webapp2
from webapp2_extras.i18n import gettext as _

# local application/library specific imports

from boilerplate import forms as forms
import bayforms as bayforms

from boilerplate import models
from boilerplate.lib.basehandler import BaseHandler
from boilerplate.lib.basehandler import user_required

from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import users
# from google.appengine.api import images

from pprint import pprint as pprint

from baymodels import models as bmodels

import config.utils as utils


class BrowseContractorsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for browsing and searching contractors
    """

    @user_required
    def get(self):
        """Handles GET requests to the paging by cursors sub-application.

        If there is a bookmark value in the query parameters, uses it to create
        a cursor and page using it. Includes up to PAGE_SIZE results and a link
        to the next page of results if any more exist.
        My:
        There will be 7 pagination links: 'Previous', 'a', 'b', 'c', 'd', 'e', 'Next'.
        That is, if we are in the first page, position 'a' corresponds to '1', 'b' to '2' and so on.
        If there are 7 pages and we are on page 6, position 'd' will be active with value 6.
        If there are 7 pages and we are on page 4, position 'c' will be active with value 4. And so on.
        Therefore we need to find 5 cursors for positions 'a' through 'e'. However, if active page is not c,
        then we don't need to produce new cursors.
        First things first. We have a query result with count 83. Number of pages will be 9.
        Let's start off by finding the first five cursors. That means we have to fetch 50 elements.
        Let's find the better solution. Let's use keys_only=True for fetching. Otherwise we can use offset.
        """
        PAGE_SIZE = 5
        LIMIT = 500
        params = {}

        cursor = None
        bookmark = self.request.get('bookmark')
        if bookmark:
            cursor = ndb.Cursor.from_websafe_string(bookmark)

        query = bmodels.Prodetails.query()
        count = query.count()

        # the following line returns the equivalent to math.ceil(float), just saving from adding another lib to the mix
        number_of_pages = count/PAGE_SIZE if count % PAGE_SIZE == 0 else count/PAGE_SIZE + 1

        suggestions, next_cursor, more = query.fetch_page(PAGE_SIZE,
                                                          keys_only=True,
                                                          start_cursor=cursor)

        next_bookmark = None
        if more:
            next_bookmark = next_cursor.to_websafe_string()

        params['previous'] = next_bookmark
        params['a']

        self.render_response('suggestion.html', bookmark=next_bookmark,
                             suggestions=suggestions)

        return self.render_template('browse/browse_contractors.html', **params)

    def post(self):
        pass
