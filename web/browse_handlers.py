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


# related third party imports
import webapp2
from webapp2_extras.i18n import gettext as _

# local application/library specific imports

from boilerplate import forms as forms
import bayforms as bayforms

from boilerplate import models
from boilerplate.lib.basehandler import BaseHandler
from boilerplate.lib.basehandler import user_required

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import users
# from google.appengine.api import images

import urllib2
import urllib

from pprint import pprint as pprint

from baymodels import models as bmodels

import config.utils as utils


class BrowseContractorsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for browsing and searching contractors
    """

    @user_required
    def get(self):
        params = {}

        return self.render_template('browse/browse_contractors.html', **params)

    def post(self):
        pass
