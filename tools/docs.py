#!/usr/bin/env python
#
# Copyright 2012 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Contains 'helper' classes for managing search.Documents.
BaseDocumentManager provides some common utilities, and the Product subclass
adds some Product-document-specific helper methods.
"""

import collections
import copy
import datetime
import logging
import re
import string
import urllib

import categories
import config
import errors
import models

from google.appengine.api import search
from google.appengine.ext import ndb


class BaseDocumentManager(object):
    """Abstract class. Provides helper methods to manage search.Documents."""

    _INDEX_NAME = None
    _VISIBLE_PRINTABLE_ASCII = frozenset(
        set(string.printable) - set(string.whitespace))

    def __init__(self, doc):
        """Builds a dict of the fields mapped against the field names, for
        efficient access.
        """
        self.doc = doc
        fields = doc.fields

    def getFieldVal(self, fname):
        """Get the value of the document field with the given name.  If there is
        more than one such field, the method returns None."""
        try:
            return self.doc.field(fname).value
        except ValueError:
            return None

    def setFirstField(self, new_field):
        """Set the value of the (first) document field with the given name."""
        for i, field in enumerate(self.doc.fields):
            if field.name == new_field.name:
                self.doc.fields[i] = new_field
                return True
        return False

    @classmethod
    def isValidDocId(cls, doc_id):
        """Checks if the given id is a visible printable ASCII string not starting
        with '!'.  Whitespace characters are excluded.
        """
        for char in doc_id:
            if char not in cls._VISIBLE_PRINTABLE_ASCII:
                return False
        return not doc_id.startswith('!')

    @classmethod
    def getIndex(cls):
        return search.Index(name=cls._INDEX_NAME)

    @classmethod
    def deleteAllInIndex(cls):
        """Delete all the docs in the given index."""
        docindex = cls.getIndex()

        try:
            while True:
                # until no more documents, get a list of documents,
                # constraining the returned objects to contain only the doc ids,
                # extract the doc ids, and delete the docs.
                document_ids = [document.doc_id
                                                for document in docindex.get_range(ids_only=True)]
                if not document_ids:
                    break
                docindex.delete(document_ids)
        except search.Error:
            logging.exception("Error removing documents:")

    @classmethod
    def getDoc(cls, doc_id):
        """Return the document with the given doc id. One way to do this is via
        the get_range method, as shown here.  If the doc id is not in the
        index, the first doc in the index will be returned instead, so we need
        to check for that case."""
        if not doc_id:
            return None
        try:
            index = cls.getIndex()
            response = index.get_range(
                    start_id=doc_id, limit=1, include_start_object=True)
            if response.results and response.results[0].doc_id == doc_id:
                return response.results[0]
            return None
        except search.InvalidRequest:  # catches ill-formed doc ids
            return None

    @classmethod
    def removeDocById(cls, doc_id):
        """Remove the doc with the given doc id."""
        try:
            cls.getIndex().delete(doc_id)
        except search.Error:
            logging.exception("Error removing doc id %s.", doc_id)

    @classmethod
    def add(cls, documents):
        """wrapper for search index add method; specifies the index name."""
        try:
            return cls.getIndex().put(documents)
        except search.Error:
            logging.exception("Error adding documents.")


# class Store(BaseDocumentManager):

#   _INDEX_NAME = config.STORE_INDEX_NAME
#   STORE_NAME = 'store_name'
#   STORE_LOCATION = 'store_location'
#   STORE_ADDRESS = 'store_address'


class ContractorDoc(BaseDocumentManager):
    """Provides helper methods to manage Product documents.  All Product documents
    built using these methods will include a core set of fields (see the
    _buildCoreProductFields method).  We use the given product id (the Product
    entity key) as the doc_id.  This is not required for the entity/document
    design-- each explicitly point to each other, allowing their ids to be
    decoupled-- but using the product id as the doc id allows a document to be
    reindexed given its product info, without having to fetch the
    existing document."""
    # We are using username as the doc_id

    _INDEX_NAME = config.CONTRACTOR_INDEX_NAME

    # 'core' contractor document field names
    # USER = 'user'
    USERNAME = 'username'
    NAME = 'name'
    LAST_NAME = 'last_name'
    TITLE = 'title'
    OVERVIEW = 'overview'
    JOBS = 'jobs'
    UPDATED = 'updated_on'

    _SORT_OPTIONS = [
                [NAME, 'name', search.SortExpression(
                        expression=NAME,
                        direction=search.SortExpression.ASCENDING, default_value='zzz')],
                [LAST_NAME, 'last name', search.SortExpression(
                        expression=LAST_NAME,
                        direction=search.SortExpression.ASCENDING, default_value='zzz')],
                [USERNAME, 'username', search.SortExpression(
                        expression=USERNAME,
                        direction=search.SortExpression.ASCENDING, default_value='zzz')],
                [JOBS, 'jobs', search.SortExpression(
                        expression=JOBS,
                        direction=search.SortExpression.ASCENDING, default_value='')],
                [UPDATED, 'modified', search.SortExpression(
                        expression=UPDATED,
                        direction=search.SortExpression.DESCENDING, default_value=1)]
            ]

    _SORT_MENU = None
    _SORT_DICT = None

    @classmethod
    def deleteAllInProductIndex(cls):
        cls.deleteAllInIndex()

    @classmethod
    def getSortMenu(cls):
        if not cls._SORT_MENU:
            cls._buildSortMenu()
        return cls._SORT_MENU

    @classmethod
    def getSortDict(cls):
        if not cls._SORT_DICT:
            cls._buildSortDict()
        return cls._SORT_DICT

    @classmethod
    def _buildSortMenu(cls):
        """Build the default set of sort options used for Product search.
        Of these options, all but 'relevance' reference core fields that
        all Products will have."""
        res = [(elt[0], elt[1]) for elt in cls._SORT_OPTIONS]
        cls._SORT_MENU = [('relevance', 'relevance')] + res

    @classmethod
    def _buildSortDict(cls):
        """Build a dict that maps sort option keywords to their corresponding
        SortExpressions."""
        cls._SORT_DICT = {}
        for elt in cls._SORT_OPTIONS:
            cls._SORT_DICT[elt[0]] = elt[2]

    @classmethod
    def getDocFromUsername(cls, username):
        """Given a username, get its doc. We're using the username as the doc id, so we can
        do this via a direct fetch."""
        return cls.getDoc(username)

    @classmethod
    def removeDocByUsername(cls, username):
        """Given a doc's username, remove the doc matching it from the contractor index."""
        cls.removeDocById(username)

# 'accessor' convenience methods

    def getUSERNAME(self):
        """Get the value of the 'username' field of a ContractorDoc doc."""
        return self.getFieldVal(self.USERNAME)

    def getName(self):
        """Get the value of the 'name' field of a ContractorDoc doc."""
        return self.getFieldVal(self.NAME)

    def getLastName(self):
        """Get the value of the 'last_name' field of a ContractorDoc doc."""
        return self.getFieldVal(self.LAST_NAME)

    def getOverview(self):
        """Get the value of the 'overview' field of a ContractorDoc doc."""
        return self.getFieldVal(self.OVERVIEW)

    @classmethod
    def _buildContractorFields(
            cls, username, name, last_name, title, overview, jobs):
        """Construct a document field list for the fields of Contractors (ProDetails)."""
        fields = [search.TextField(name=cls.USERNAME, value=username),
                            # The 'updated' field is always set to the current date.
                            search.DateField(name=cls.UPDATED,
                                    value=datetime.datetime.now().date()),
                            search.TextField(name=cls.NAME, value=name),
                            search.TextField(name=cls.LAST_NAME, value=last_name),
                            search.TextField(name=cls.TITLE, value=title),
                            # strip the markup from the description value, which can
                            # potentially come from user input.  We do this so that
                            # we don't need to sanitize the description in the
                            # templates, showing off the Search API's ability to mark up query
                            # terms in generated snippets.  This is done only for
                            # demonstration purposes; in an actual app,
                            # it would be preferrable to use a library like Beautiful Soup
                            # instead.
                            # We'll let the templating library escape all other rendered
                            # values for us, so this is the only field we do this for.
                            search.TextField(
                                    name=cls.OVERVIEW,
                                    value=re.sub(r'<[^>]*?>', '', overview)),
                            search.TextField(name=cls.JOBS, value=jobs)
                         ]
        return fields

    @classmethod
    def _createDocument(
            cls, username=None, name=None, last_name=None, title=None, overview=None,
            jobs=None, **params):
        """Create a Document object from given params."""
        # check for the fields that are always required.
        if username and name and last_name:
            # First, check that the given username has only visible ascii characters,
            # and does not contain whitespace. The username will be used as the doc_id,
            # which has these requirements.
            if not cls.isValidDocId(username):
                raise errors.OperationFailedError("Illegal username %s" % username)
            # construct the document fields from the params
            resfields = cls._buildContractorFields(
                    username=username, name=name, last_name=last_name,
                    title=title, overview=overview,
                    jobs=jobs, **params)
            # build and index the document.  Use the pid (product id) as the doc id.
            # (If we did not do this, and left the doc_id unspecified, an id would be
            # auto-generated.)
            d = search.Document(doc_id=username, fields=resfields)
            return d
        else:
            raise errors.OperationFailedError('Missing parameter.')
