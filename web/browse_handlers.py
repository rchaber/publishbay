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


class BrowseContractorsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for browsing and searching contractors
    """

    _DEFAULT_DOC_LIMIT = 5  # default number of search results to display per page.
    _OFFSET_LIMIT = 1000
    _NAV_LEN = 5

    def parseParams(self):
        """Filter the param set to the expected params."""
        qparams = {
            'qtype': '',
            'query': '',
            'sort': '',
            'offset': '0'
        }
        for k, v in qparams.iteritems():
            # Possibly replace default values.
            qparams[k] = self.request.get(k, v)
        return qparams

    @user_required
    def get(self):
        """Handles GET requests to the paging by cursors sub-application.

        It doesn't uses cursors. Instead, it uses offset along with a paginate custom function to navigate through the results.
        """

        PAGE_SIZE = 5
        # LIMIT = 500

        # options = ndb.QueryOptions(limit=LIMIT)

        # THE FOLLOWING CALLS SEARCH API - LEAVING OUT FOR THIS VERSION
        # query_string = self.request.get('query').strip()
        # print query_string

        # qresponse = None
        # qresponse_items = None

        # if query_string:
        #     qparams = self.parseParams()
        #     qresponse = self.doContractorSearch(qparams)
        #     qresponse_items = [bmodels.ProDetails.get_by_id(int(i)) for i in qresponse.get('search_response')]

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

        paging = tools.pagination(number_of_pages, new_page, 5)

        params['count'] = count
        params['contractors'] = contractors

        params['marks'] = paging[0]
        params['active'] = 'mark_' + str(paging[0][paging[1]])
        params['previous'] = str(new_page - 1) if new_page > 1 else None
        params['next'] = str(new_page + 1) if new_page < number_of_pages else None

        params['joblist'] = utils.joblist
        params['jobs'] = jobfilter

        # search_input is the query string in the Seach box
        # params['search_input'] = query_string if query_string else ''

        return self.render_template('browse/browse_contractors.html', **params)

    def post(self):
        qparams = self.parseParams()
        self.redirect('/browse/contractors?' + urllib.urlencode(
            dict([k, v.encode('utf-8')] for k, v in qparams.items()))
        )

    def _getDocLimit(self):
        """if the doc limit is not set in the config file, use the default."""
        doc_limit = self._DEFAULT_DOC_LIMIT
        try:
            doc_limit = int(search_config.DOC_LIMIT)
        except ValueError:
            logging.error('DOC_LIMIT not properly set in config file; using default.')
        return doc_limit

    def doContractorSearch(self, params):
        """Perform a contractor search and display the results."""

        # the contractor fields that we can sort on from the UI, and their mappings to
        # search.SortExpression parameters
        sort_info = docs.ContractorDoc.getSortMenu()
        sort_dict = docs.ContractorDoc.getSortDict()
        query = params.get('query', '')
        user_query = query
        print "user_query "+user_query
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
            print search_results
            print returned_count

        except search.Error:
            logging.exception("Search error:")  # log the exception stack trace
            msg = _('There was a search error.')
            self.add_message(msg, 'error')
            self.redirect_to('browse-contractors')

        csearch_response = []
        # For each document returned from the search
        for doc in search_results:
            cdoc = docs.ContractorDoc(doc)
            pid = cdoc.getPID()
            print "pid = "+pid
            csearch_response.append(pid)

        print "csearch_response = " + str(csearch_response)

        if not query:
            print_query = 'All'
        else:
            print_query = query

        logging.debug('returned_count: %s', returned_count)

        # construct the return dict
        qresponse = {
            'base_pquery': user_query,
            'qtype': 'contractor',
            'query': query, 'print_query': print_query,
            'sort_order': sortq,
            'first_res': offsetval + 1, 'last_res': offsetval + returned_count,
            'returned_count': returned_count,
            'number_found': search_results.number_found,
            'search_response': csearch_response,
            'sort_info': sort_info}

        return qresponse

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
            print "here _buildQuery else sortq"
            if sortq == docs.ContractorDoc.LAST_NAME:
                expr_list = [sort_dict.get(docs.ContractorDoc.LAST_NAME), sort_dict.get(docs.ContractorDoc.NAME)]
            else:
                expr_list = [sort_dict.get(docs.ContractorDoc.UPDATED), sort_dict.get(docs.ContractorDoc.NAME)]
            sortopts = search.SortOptions(expressions=expr_list)
            # logging.info("sortopts: %s", sortopts)
            search_query = search.Query(
                query_string=query.strip(),
                options=search.QueryOptions(
                    limit=doc_limit,
                    offset=offsetval,
                    sort_options=sortopts,
                    returned_fields=returned_fields))
            print "search_query"
            print search_query
        return search_query


class ViewContractorsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for viewing contractors pages
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for edit professional details """

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
            # params['joblist'] = urllib.unquote(', '.join(contractor.jobs))
            params['joblist'] = contractor.jobs
            params['city'] = contractor.city
            params['state'] = contractor.state
            params['contractor_id'] = contractor_id

        return self.render_template('browse/view_contractor.html', **params)


class BrowseAuthorsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for browsing and searching authors
    """

    _DEFAULT_DOC_LIMIT = 5  # default number of search results to display per page.
    _OFFSET_LIMIT = 1000
    _NAV_LEN = 5

    def parseParams(self):
        """Filter the param set to the expected params."""
        qparams = {
            'qtype': '',
            'query': '',
            'sort': '',
            'offset': '0'
        }
        for k, v in qparams.iteritems():
            # Possibly replace default values.
            qparams[k] = self.request.get(k, v)
        return qparams

    @user_required
    def get(self):
        """Handles GET requests to the paging by cursors sub-application.

        It doesn't uses cursors. Instead, it uses offset along with a paginate custom function to navigate through the results.
        """

        PAGE_SIZE = 5
        # LIMIT = 500

        # options = ndb.QueryOptions(limit=LIMIT)

        # THE FOLLOWING CALLS SEARCH API - LEAVING OUT FOR THIS VERSION
        # query_string = self.request.get('query').strip()
        # print query_string

        # qresponse = None
        # qresponse_items = None

        # if query_string:
        #     qparams = self.parseParams()
        #     qresponse = self.doContractorSearch(qparams)
        #     qresponse_items = [bmodels.ProDetails.get_by_id(int(i)) for i in qresponse.get('search_response')]

        authors = []
        params = {}
        items = []

        genrefilter = self.request.GET.getall('genre')
        print genrefilter

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

        paging = tools.pagination(number_of_pages, new_page, 5)

        params['count'] = count
        params['authors'] = authors

        params['marks'] = paging[0]
        params['active'] = 'mark_' + str(paging[0][paging[1]])
        params['previous'] = str(new_page - 1) if new_page > 1 else None
        params['next'] = str(new_page + 1) if new_page < number_of_pages else None

        params['genrelist_fiction'] = utils.genres_fiction
        params['genrelist_nonfiction'] = utils.genres_nonfiction
        params['genres'] = genrefilter

        # search_input is the query string in the Seach box
        # params['search_input'] = query_string if query_string else ''

        return self.render_template('browse/browse_authors.html', **params)

    def post(self):
        qparams = self.parseParams()
        self.redirect('/browse/contractors?' + urllib.urlencode(
            dict([k, v.encode('utf-8')] for k, v in qparams.items()))
        )

    def _getDocLimit(self):
        """if the doc limit is not set in the config file, use the default."""
        doc_limit = self._DEFAULT_DOC_LIMIT
        try:
            doc_limit = int(search_config.DOC_LIMIT)
        except ValueError:
            logging.error('DOC_LIMIT not properly set in config file; using default.')
        return doc_limit

    def doContractorSearch(self, params):
        """Perform a contractor search and display the results."""

        # the contractor fields that we can sort on from the UI, and their mappings to
        # search.SortExpression parameters
        sort_info = docs.ContractorDoc.getSortMenu()
        sort_dict = docs.ContractorDoc.getSortDict()
        query = params.get('query', '')
        user_query = query
        print "user_query "+user_query
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
            print search_results
            print returned_count

        except search.Error:
            logging.exception("Search error:")  # log the exception stack trace
            msg = _('There was a search error.')
            self.add_message(msg, 'error')
            self.redirect_to('browse-contractors')

        csearch_response = []
        # For each document returned from the search
        for doc in search_results:
            cdoc = docs.ContractorDoc(doc)
            pid = cdoc.getPID()
            print "pid = "+pid
            csearch_response.append(pid)

        print "csearch_response = " + str(csearch_response)

        if not query:
            print_query = 'All'
        else:
            print_query = query

        logging.debug('returned_count: %s', returned_count)

        # construct the return dict
        qresponse = {
            'base_pquery': user_query,
            'qtype': 'contractor',
            'query': query, 'print_query': print_query,
            'sort_order': sortq,
            'first_res': offsetval + 1, 'last_res': offsetval + returned_count,
            'returned_count': returned_count,
            'number_found': search_results.number_found,
            'search_response': csearch_response,
            'sort_info': sort_info}

        return qresponse

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
            print "here _buildQuery else sortq"
            if sortq == docs.ContractorDoc.LAST_NAME:
                expr_list = [sort_dict.get(docs.ContractorDoc.LAST_NAME), sort_dict.get(docs.ContractorDoc.NAME)]
            else:
                expr_list = [sort_dict.get(docs.ContractorDoc.UPDATED), sort_dict.get(docs.ContractorDoc.NAME)]
            sortopts = search.SortOptions(expressions=expr_list)
            # logging.info("sortopts: %s", sortopts)
            search_query = search.Query(
                query_string=query.strip(),
                options=search.QueryOptions(
                    limit=doc_limit,
                    offset=offsetval,
                    sort_options=sortopts,
                    returned_fields=returned_fields))
            print "search_query"
            print search_query
        return search_query


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