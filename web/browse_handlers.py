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


def paginate(number_of_pages, current_page):
    positions = ['a', 'b', 'c', 'd', 'e']
    if current_page < 3:
        current_position = ['a', 'b'][current_page - 1]
        pages = range(1, 6)
    elif current_page > number_of_pages - 2:
        current_position = ['d', 'e'][number_of_pages - current_page - 1]
        pages = range(number_of_pages - 4, number_of_pages + 1)
    else:
        current_position = 'c'
        pages = range(current_page - 2, current_page + 3)
    if number_of_pages < 5:
        positions = positions[:number_of_pages]
        current_position = positions[current_page - 1]
        pages = range(1, number_of_pages + 1)
    positions_pages = {}
    for i in positions:
        positions_pages[i] = pages[positions.index(i)]
    return positions, current_position, positions_pages


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
        # LIMIT = 500

        # options = ndb.QueryOptions(limit=LIMIT)

        params = {}

        query = bmodels.ProDetails.query()
        count = query.count()

        new_page = self.request.get('page')
        new_page = int(new_page) if new_page else 1
        offset = 0
        if new_page:
            offset = int(new_page - 1) * PAGE_SIZE

        # the following line returns the equivalent to math.ceil(float), just saving from importing another lib
        number_of_pages = count/PAGE_SIZE if count % PAGE_SIZE == 0 else count/PAGE_SIZE + 1

        items = query.fetch(PAGE_SIZE, offset=offset)

        contractors = []
        for i in items:
            d = {}
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

        print contractors

        pagination = paginate(number_of_pages, new_page)

        for i in pagination[2].keys():
            params['mark_'+i] = pagination[2][i]

        params['previous'] = new_page - 1 if new_page > 1 else None
        params['next'] = new_page + 1 if new_page < number_of_pages else None
        params['active'] = 'mark_' + pagination[1]
        params['count'] = count
        params['contractors'] = contractors
        params['marks'] = pagination[2]

        return self.render_template('browse/browse_contractors.html', **params)

    def post(self):
        pass
