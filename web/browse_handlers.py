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

# from pprint import pprint as pprint

from baymodels import models as bmodels

from tools import docs as docs

import config.utils as utils
import config.search_config as search_config


def pagination(number_of_pages, current_page, nav_len):  # better algorithm to paginate
    if nav_len > number_of_pages:
        nav_len = number_of_pages
    center = float(nav_len) / 2 + 1
    if current_page < center:
        nav_bar = [i for i in range(1, nav_len + 1)]
    elif current_page > number_of_pages - nav_len / 2:
        nav_bar = [i for i in range(number_of_pages - nav_len + 1, number_of_pages + 1)]
    else:
        start = current_page - nav_len / 2
        nav_bar = [i for i in range(start, start + nav_len)]
    active_mark = nav_bar.index(current_page)
    return nav_bar, active_mark


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

        It doesn't uses cursors. Instead, it uses offset along with a paginate custom function to navigate through the results.
        """

        PAGE_SIZE = 5
        # LIMIT = 500

        # options = ndb.QueryOptions(limit=LIMIT)

        params = {}

        query_string = self.request.get('query').strip()
        jobfilter = self.request.get('jobfilter')
        jobfilter = jobfilter.split('|')

        new_page = self.request.get('page')
        new_page = int(new_page) if new_page else 1
        offset = 0
        if new_page:
            offset = int(new_page - 1) * PAGE_SIZE

        if jobfilter == ['']:
            query = bmodels.ProDetails.query()
        else:
            query = bmodels.ProDetails.query(bmodels.ProDetails.jobs.IN(jobfilter))
        count = query.count()
        items = query.fetch(PAGE_SIZE, offset=offset)

        # the following line returns the equivalent to math.ceil(float), just saving from importing another lib
        number_of_pages = count/PAGE_SIZE if count % PAGE_SIZE == 0 else count/PAGE_SIZE + 1

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

        paging = pagination(number_of_pages, new_page, 5)

        params['count'] = count
        params['contractors'] = contractors

        params['marks'] = paging[0]
        params['active'] = 'mark_' + str(paging[0][paging[1]])
        params['previous'] = str(new_page - 1) if new_page > 1 else None
        params['next'] = str(new_page + 1) if new_page < number_of_pages else None

        params['joblist'] = utils.joblist
        params['jobfilter'] = jobfilter

        params['search_input'] = query_string if query_string else ''

        return self.render_template('browse/browse_contractors.html', **params)

    def post(self):
        pass


class ContractorSearchHandler(BaseHandler):
    """The handler for doing a contractor search."""
    # NOT BEING USED RIGHT NOW, NEEDS MORE WORK

    _DEFAULT_DOC_LIMIT = 5  # default number of search results to display per page.
    _OFFSET_LIMIT = 1000
    _NAV_LEN = 5

    def parseParams(self):
        """Filter the param set to the expected params."""
        params = {
            'qtype': '',
            'query': '',
            'sort': '',
            'offset': '0'
        }
        for k, v in params.iteritems():
            # Possibly replace default values.
            params[k] = self.request.get(k, v)
        return params

    def post(self):
        params = self.parseParams()
        self.redirect('/browse/contractors?' + urllib.urlencode(
            dict([k, v.encode('utf-8')] for k, v in params.items()))
        )

    def _getDocLimit(self):
        """if the doc limit is not set in the config file, use the default."""
        doc_limit = self._DEFAULT_DOC_LIMIT
        try:
            doc_limit = int(search_config.DOC_LIMIT)
        except ValueError:
            logging.error('DOC_LIMIT not properly set in config file; using default.')
        return doc_limit

    def get(self):
        """Handle a contractor search request."""

        params = self.parseParams()
        self.doContractorSearch(params)

    def doContractorSearch(self, params):
        """Perform a contractor search and display the results."""

        # the contractor fields that we can sort on from the UI, and their mappings to
        # search.SortExpression parameters
        sort_info = docs.ContractorDoc.getSortMenu()
        sort_dict = docs.ContractorDoc.getSortDict()
        query = params.get('query', '')
        user_query = query
        doc_limit = self._getDocLimit()

        sortq = params.get('sort')
        try:
            offsetval = int(params.get('offset', 0))
        except ValueError:
            offsetval = 0

        try:
            # build the query and perform the search
            search_query = self._buildQuery(
                query, sortq, sort_dict, doc_limit, offsetval
            )
            search_results = docs.ContractorDoc.getIndex().search(search_query)
            returned_count = len(search_results.results)

        except search.Error:
            logging.exception("Search error:")  # log the exception stack trace
            msg = _('There was a search error.')
            self.add_message(msg, 'error')
            self.redirect_to('browse-contractors')

        csearch_response = []
        # For each document returned from the search
        for doc in search_results:
            # logging.info("doc: %s ", doc)
            cdoc = docs.ContractorDoc(doc)

            username = cdoc.getUsername()
            name = cdoc.getName()
            last_name = cdoc.getLastName()
            title = cdoc.getTitle()
            overview = cdoc.getOverview()
            jobs = cdoc.getJobs()

            # for this result, generate a result array of selected doc fields, to
            # pass to the template renderer
            csearch_response.append(
                [doc, urllib.quote_plus(username),
                    name, last_name, title, overview, jobs])

        if not query:
            print_query = 'All'
        else:
            print_query = query

        # using my own pagination (pagination - not paginate):
        # pagination(number_of_pages, current_page, nav_len) return nav_bar (list), active_mark (integer, list index)
        number_of_pages = returned_count / self._getDocLimit()
        current_page = offsetval / self._getDocLimit()
        pages = pagination(number_of_pages, current_page, search_config.NAV_LEN)

        logging.debug('returned_count: %s', returned_count)

########################

        # construct the template values
        template_values = {
            'base_pquery': user_query, 'next_link': next_link,
            'prev_link': prev_link, 'qtype': 'product',
            'query': query, 'print_query': print_query,
            'sort_order': sortq,
            'first_res': offsetval + 1, 'last_res': offsetval + returned_count,
            'returned_count': returned_count,
            'number_found': search_results.number_found,
            'search_response': psearch_response,
            'cat_info': cat_info, 'sort_info': sort_info,
            'ratings_links': rlinks}
        # render the result page.
        self.render_template('index.html', template_values)

    def _buildQuery(self, query, sortq, sort_dict, doc_limit, offsetval):
        """Build and return a search query object."""

        # computed and returned fields examples.  Their use is not required
        # for the application to function correctly.
        returned_fields = [docs.ContractorDoc.USERNAME, docs.ContractorDoc.NAME,
                           docs.ContractorDoc.LAST_NAME, docs.ContractorDoc.TITLE,
                           docs.ContractorDoc.OVERVIEW, docs.ContractorDoc.JOBS]

        if sortq == 'relevance':
            # If sorting on 'relevance', use the Match scorer.
            sortopts = search.SortOptions(match_scorer=search.MatchScorer())
            search_query = search.Query(
                query_string=query.strip(),
                options=search.QueryOptions(
                    limit=doc_limit,
                    offset=offsetval,
                    sort_options=sortopts,
                    returned_fields=returned_fields)
            )
        else:
            # Otherwise (not sorting on relevance), use the selected field as the
            # first dimension of the sort expression, and the average rating as the
            # second dimension, unless we're sorting on rating, in which case price
            # is the second sort dimension.
            # We get the sort direction and default from the 'sort_dict' var.
            if sortq == docs.ContractorDoc.LAST_NAME:
                expr_list = [sort_dict.get(sortq), sort_dict.get(docs.ContractorDoc.LAST_NAME)]
            else:
                expr_list = [sort_dict.get(sortq), sort_dict.get(
                    docs.ContractorDoc.NAME)]
            sortopts = search.SortOptions(expressions=expr_list)
            # logging.info("sortopts: %s", sortopts)
            search_query = search.Query(
                query_string=query.strip(),
                options=search.QueryOptions(
                    limit=doc_limit,
                    offset=offsetval,
                    sort_options=sortopts,
                    snippeted_fields=[docs.ContractorDoc.DESCRIPTION],
                    returned_fields=returned_fields))
        return search_query
