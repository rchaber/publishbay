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

import urllib2

from baymodels import models as bmodels

import config.utils as utils


class SecureRequestHandler(BaseHandler):
    """
    Only accessible to users that are logged in
    """

    @user_required
    def get(self, **kwargs):
        user_session = self.user
        user_session_object = self.auth.store.get_session(self.request)

        user_info = models.User.get_by_id(long(self.user_id))
        user_info_object = self.auth.store.user_model.get_by_auth_token(
            user_session['user_id'], user_session['token'])

        try:
            params = {
                "user_session": user_session,
                "user_session_object": user_session_object,
                "user_info": user_info,
                "user_info_object": user_info_object,
                "userinfo_logout-url": self.auth_config['logout_url'],
            }
            return self.render_template('secure_zone.html', **params)
        except (AttributeError, KeyError), e:
            return "Secure zone error:" + " %s." % e


class EditAssociationsHandler(BaseHandler):
    """
    Handler for Edit Account Associations
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for edit account associations """

        params = {}
        if self.user:
            user_info = models.User.get_by_id(long(self.user_id))
            providers_info = user_info.get_social_providers_info()
            if not user_info.password:
                params['local_account'] = False
            else:
                params['local_account'] = True
            params['used_providers'] = providers_info['used']
            params['unused_providers'] = providers_info['unused']
            params['country'] = user_info.country

        return self.render_template('edit_associations.html', **params)

    def post(self):
        """ Get fields from POST dict """

        try:
            user_info = models.User.get_by_id(long(self.user_id))

        except (AttributeError, TypeError), e:
            login_error_message = _('Sorry you are not logged in.')
            self.add_message(login_error_message, 'error')
            self.redirect_to('login')


class DeleteSocialProviderHandler(BaseHandler):
    """
    Delete Social association with an account
    """

    @user_required
    def post(self, provider_name):
        if self.user:
            user_info = models.User.get_by_id(long(self.user_id))
            if len(user_info.get_social_providers_info()['used']) > 1 or (user_info.password is not None):
                social_user = models.SocialUser.get_by_user_and_provider(user_info.key, provider_name)
                if social_user:
                    social_user.key.delete()
                    message = _('%s successfully disassociated.' % provider_name)
                    self.add_message(message, 'success')
                else:
                    message = _('Social account on %s not found for this user.' % provider_name)
                    self.add_message(message, 'error')
            else:
                message = _('Social account on %s cannot be deleted for user.'
                            '  Please create a username and password to delete social account.' % provider_name)
                self.add_message(message, 'error')
        time.sleep(1)
        self.redirect_to('edit-associations')


class EditProDetailsHandler(BaseHandler):
    """
    Handler for Edit User Contact Info
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for edit professional details """


        params = {}

        self.form.display_full_name.data = True
        self.form.profile_visibility.data = 'everyone'
        self.form.overview.data = ''

        params['english_level'] = ''
        params['upload_url'] = blobstore.create_upload_url('/upload')

        if self.user:
            user_pro_details = bmodels.ProDetails.get_by_userkey(self.user_key)
            if user_pro_details:
                self.form.display_full_name.data = user_pro_details.display_full_name
                params['display_full_name'] = self.form.display_full_name.data
                # self.form.picture.data = user_pro_details.picture
                self.form.title.data = user_pro_details.title
                self.form.overview.data = user_pro_details.overview
                params['overviewdata'] = self.form.overview.data
                self.form.profile_visibility.data = user_pro_details.profile_visibility
                self.form.english_level.data = user_pro_details.english_level
                params['english_level'] = user_pro_details.english_level
                self.form.address1.data = user_pro_details.address1
                self.form.address2.data = user_pro_details.address2
                self.form.city.data = user_pro_details.city
                self.form.state.data = user_pro_details.state
                self.form.zipcode.data = user_pro_details.zipcode
                self.form.phone.data = user_pro_details.phone

        joblist = utils.joblist
        remain = len(joblist) % 3
        if remain == 0:
            params['joblist_left'] = joblist[0:len(joblist)/3]
            params['joblist_center'] = joblist[len(joblist)/3:len(joblist)/3*2]
            params['joblist_right'] = joblist[len(joblist)/3*2:]
        else:
            params['joblist_left'] = joblist[0:(len(joblist)-remain)/2]
            params['joblist_center'] = joblist[(len(joblist)-remain)/2:len(joblist)-remain]
            params['joblist_right'] = joblist[-remain:]

        params['profile_visibility'] = self.form.profile_visibility.data

        return self.render_template('edit_pro_details.html', **params)

    def post(self):
        """ Get fields from POST dict """

        # if not self.form.validate():
            # return self.get()

        # print self.request.get('upload_url')
        # print dir(self.request.get('picture'))
        # urllib2.Request(self.request.get('upload_url'), picture=self.request.get('picture').encode)

        # self.request.get('upload_url')
        # a = blobstore_handlers.BlobstoreUploadHandler()
        # print dir(a)
        # upload = a.get_uploads()[0]
        # print upload.key


        k = models.User.get_by_id(long(self.user_id)).key

        user_pro_details = bmodels.ProDetails.get_by_userkey(k)

        if not user_pro_details:
            user_pro_details = bmodels.ProDetails()
            user_pro_details.user = k

        display_full_name = (self.form.display_full_name.data == "True")
        overview = self.form.overview.data
        # picture = self.request.get('picture')

        # if picture:
          #   user_pro_details.picture = 
        title = self.form.title.data
        profile_visibility = self.form.profile_visibility.data
        english_level = int(self.form.english_level.data)  # problem is here when nothing is selected
        address1 = self.form.address1.data
        address2 = self.form.address2.data
        city = self.form.city.data
        state = self.form.state.data.upper()
        zipcode = self.form.zipcode.data
        phone = self.form.phone.data


        try:
            message = ''
            user_pro_details.display_full_name = display_full_name
            # user_pro_details.picture = picture # this isn't working
            user_pro_details.title = title
            user_pro_details.overview = overview
            user_pro_details.profile_visibility = profile_visibility
            user_pro_details.english_level = english_level
            user_pro_details.address1 = address1
            user_pro_details.address2 = address2
            user_pro_details.city = city
            user_pro_details.state = state
            user_pro_details.zipcode = zipcode
            user_pro_details.phone = phone
            user_pro_details.put()
            message += " " + _('Your contact info has been updated.')
            self.add_message(message, 'success')
            return self.get()

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error updating contact info: ' + e)
            print 'here'
            message = _('Unable to update contact info. Please try again later.')
            self.add_message(message, 'error')
            return self.get()

    @webapp2.cached_property
    def form(self):
        return bayforms.EditProDetails(self)
