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


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, file_key):
        file_view = str(urllib.unquote(file_key))
        blob_info = blobstore.BlobInfo.get(file_view)
        self.send_blob(blob_info)


class DisplayProDetailsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for Edit User Contact Info
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for edit professional details """

        params = {}

        params['profile_visibility'] = 'everyone'
        params['display_full_name'] = False
        params['english_level'] = 0
        params['picture_url'] = ''
        params['overviewdata'] = ''
        params['joblist'] = ''

        if self.user:
            user_pro_details = bmodels.ProDetails.get_by_userkey(self.user_key)
            if user_pro_details:
                params['there_is_profile'] = True
                params['display_full_name'] = user_pro_details.display_full_name
                if user_pro_details.picture_key and user_pro_details.picture_key != '':
                    params['picture_url'] = '/serve/%s' % user_pro_details.picture_key
                params['title'] = user_pro_details.title
                params['overview'] = user_pro_details.overview
                params['profile_visibility'] = user_pro_details.profile_visibility
                params['english_level'] = user_pro_details.english_level
                params['joblist'] = ', '.join(user_pro_details.jobs)
                params['address1'] = user_pro_details.address1
                params['address2'] = user_pro_details.address2
                params['city'] = user_pro_details.city
                params['state'] = user_pro_details.state
                params['zipcode'] = user_pro_details.zipcode
                params['phone'] = user_pro_details.phone
            else:
                params['there_is_profile'] = False

        return self.render_template('display_pro_details.html', **params)


class EditProDetailsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for Edit User Contact Info
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for edit professional details """

        params = {}

        self.form.display_full_name.data = False
        self.form.profile_visibility.data = 'everyone'

        params['english_level'] = 0
        params['upload_url'] = blobstore.create_upload_url('/upload_picture')
        params['picture_url'] = ''
        params['overviewdata'] = ''
        params['joblist'] = []
        params['there_is_profile'] = False

        if self.user:
            user_pro_details = bmodels.ProDetails.get_by_userkey(self.user_key)
            if user_pro_details:
                params['there_is_profile'] = True
                self.form.display_full_name.data = user_pro_details.display_full_name
                params['display_full_name'] = self.form.display_full_name.data
                if user_pro_details.picture_key and user_pro_details.picture_key != '':
                    params['picture_url'] = '/serve/%s' % user_pro_details.picture_key
                self.form.title.data = user_pro_details.title
                params['overviewdata'] = user_pro_details.overview
                self.form.profile_visibility.data = user_pro_details.profile_visibility
                self.form.english_level.data = user_pro_details.english_level
                params['english_level'] = user_pro_details.english_level
                params['joblist'] = user_pro_details.jobs
                self.form.address1.data = user_pro_details.address1
                self.form.address2.data = user_pro_details.address2
                self.form.city.data = user_pro_details.city
                self.form.state.data = user_pro_details.state
                self.form.zipcode.data = user_pro_details.zipcode
                self.form.phone.data = user_pro_details.phone

        a = utils.split_3cols(utils.joblist)
        params['joblist_left'] = a['left']
        params['joblist_center'] = a['center']
        params['joblist_right'] = a['right']

        params['profile_visibility'] = self.form.profile_visibility.data

        return self.render_template('edit_pro_details.html', **params)

    def post(self):
        """ Get fields from POST dict """

        # if not self.form.validate():
            # return self.get()

        jobs = self.request.POST.get('joblist').replace('&', '').split('jobs=')[1:]

        upload_picture = self.get_uploads()
        if upload_picture:
            picture_key = upload_picture[0].key()
        else:
            picture_key = ''

        k = models.User.get_by_id(long(self.user_id)).key

        user_pro_details = bmodels.ProDetails.get_by_userkey(k)
        if not user_pro_details:
            user_pro_details = bmodels.ProDetails()
            user_pro_details.user = k

        # if picture changes, then the old one is deleted from Blobstore
        if (picture_key != '' and picture_key != user_pro_details.picture_key) and user_pro_details:
            try:
                blobstore.delete(user_pro_details.picture_key)
            except:
                pass

        display_full_name = (self.form.display_full_name.data == "True")
        overview = self.request.POST.get('overview').replace('\r\r\n', '\r\n')

        title = self.form.title.data
        profile_visibility = self.form.profile_visibility.data
        english_level = int(self.request.POST.get('english_level'))
        address1 = self.form.address1.data
        address2 = self.form.address2.data
        city = self.form.city.data
        state = self.form.state.data.upper()
        zipcode = self.form.zipcode.data
        phone = self.form.phone.data

        try:
            message = ''
            user_pro_details.display_full_name = display_full_name
            if picture_key != '':
                print 'here1'
                user_pro_details.picture_key = picture_key
            user_pro_details.title = title
            user_pro_details.overview = overview
            user_pro_details.profile_visibility = profile_visibility
            user_pro_details.english_level = english_level
            user_pro_details.jobs = jobs
            user_pro_details.address1 = address1
            user_pro_details.address2 = address2
            user_pro_details.city = city
            user_pro_details.state = state
            user_pro_details.zipcode = zipcode
            user_pro_details.phone = phone
            user_pro_details.put()
            message += " " + _('Your contact info has been updated.')
            self.add_message(message, 'success')
            self.redirect('/settings/profile')

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error updating contact info: ' + e)
            message = _('Unable to update contact info. Please try again later.')
            self.add_message(message, 'error')
            return self.get()

    @webapp2.cached_property
    def form(self):
        return bayforms.EditProDetails(self)


class DisplayPublishingHouseHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for Display Publishing House
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for create/edit publishing house """

        params = {}

        params['name'] = ''
        params['tagline'] = ''
        params['description'] = ''
        params['ph_genres_list'] = ''
        params['show_in_job_posts'] = ''
        params['logo_url'] = ''
        params['there_is_ph'] = False

        if self.user:
            publishing_house = bmodels.PublishingHouse.get_by_ownerkey(self.user_key)
            if publishing_house:
                params['there_is_ph'] = True
                params['name'] = publishing_house.name
                params['tagline'] = publishing_house.tagline
                params['description'] = publishing_house.description
                if publishing_house.logo_key and publishing_house.logo_key != '':
                    params['logo_url'] = '/serve/%s' % publishing_house.logo_key
                params['ph_genres_list'] = ', '.join(publishing_house.genres)
                params['show_in_job_posts'] = publishing_house.show_in_job_posts

        return self.render_template('display_publishing_house.html', **params)


class EditPublishingHouseHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for Create/Edit Publishing House
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for create/edit publishing house """

        params = {}

        params['upload_url'] = blobstore.create_upload_url('/upload_logo')
        params['name'] = ''
        params['tagline'] = ''
        params['description'] = ''
        params['pb_genres_list'] = ''
        params['show_in_job_posts'] = ''
        params['logo_url'] = ''
        params['there_is_ph'] = False

        if self.user:
            publishing_house = bmodels.PublishingHouse.get_by_ownerkey(self.user_key)
            if publishing_house:
                params['there_is_ph'] = True
                params['name'] = publishing_house.name
                params['tagline'] = publishing_house.tagline
                params['description'] = publishing_house.description
                if publishing_house.logo_key and publishing_house.logo_key != '':
                    params['logo_url'] = '/serve/%s' % publishing_house.logo_key
                params['pb_genres_list'] = publishing_house.genres
                params['show_in_job_posts'] = publishing_house.show_in_job_posts

        params['fiction_genres_left'] = utils.split_3cols(utils.genres_fiction)['left']
        params['fiction_genres_center'] = utils.split_3cols(utils.genres_fiction)['center']
        params['fiction_genres_right'] = utils.split_3cols(utils.genres_fiction)['right']
        params['nonfiction_genres_left'] = utils.split_3cols(utils.genres_nonfiction)['left']
        params['nonfiction_genres_center'] = utils.split_3cols(utils.genres_nonfiction)['center']
        params['nonfiction_genres_right'] = utils.split_3cols(utils.genres_nonfiction)['right']

        return self.render_template('edit_publishing_house.html', **params)

    def post(self):
        """ Get fields from POST dict """

        print 'got here'
        # if not self.form.validate():
            # return self.get()
        print self.request.POST.get('checked_genres')

        checked_genres = self.request.POST.get('checked_genres').replace('&', '').replace('+', ' ').replace('%26', '&').split('genres=')[1:]

        upload_logo = self.get_uploads()
        if upload_logo:
            logo_key = upload_logo[0].key()
        else:
            logo_key = ''

        k = models.User.get_by_id(long(self.user_id)).key

        publishing_house = bmodels.PublishingHouse.get_by_ownerkey(k)
        if not publishing_house:
            publishing_house = bmodels.PublishingHouse()
            publishing_house.owner = k

        # if logo changes, then the old one is deleted from Blobstore
        if (logo_key != '' and logo_key != publishing_house.logo_key) and publishing_house:
            try:
                blobstore.delete(publishing_house.logo_key)
            except:
                pass

        try:
            message = ''
            publishing_house.name = self.request.POST.get('name')
            if logo_key != '':
                publishing_house.logo_key = logo_key
            publishing_house.tagline = self.request.POST.get('tagline')
            publishing_house.description = self.request.POST.get('description').replace('\r\r\n', '\r\n')
            publishing_house.show_in_job_posts = (self.request.POST.get('show_in_job_posts') == "True")
            publishing_house.genres = checked_genres
            publishing_house.put()
            message += " " + _('Your publishing house info has been updated.')
            self.add_message(message, 'success')
            self.redirect('/settings/profile')

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error creating/updating publishing house: ' + e)
            message = _('Unable to create/update publishing house. Please try again later.')
            self.add_message(message, 'error')
            return self.get()


class EditAuthorProfileHandler(BaseHandler):
    """
    Handler for Create/Edit Author Profile
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for create/edit author profile """

        params = {}

        params['title'] = ''
        params['pseudonyms'] = ''
        params['overview'] = ''
        params['genres_list'] = ''
        params['ghostwrites'] = ''

        if self.user:
            author_profile = bmodels.AuthorProfile.get_by_userkey(self.user_key)
            if author_profile:
                params['title'] = author_profile.title
                params['overview'] = author_profile.overview
                params['pseudonyms'] = ', '.join(author_profile.pseudonyms)
                params['genres_list'] = author_profile.genres
                params['ghostwrites'] = author_profile.ghostwrites

        params['fiction_genres_left'] = utils.split_3cols(utils.genres_fiction)['left']
        params['fiction_genres_center'] = utils.split_3cols(utils.genres_fiction)['center']
        params['fiction_genres_right'] = utils.split_3cols(utils.genres_fiction)['right']
        params['nonfiction_genres_left'] = utils.split_3cols(utils.genres_nonfiction)['left']
        params['nonfiction_genres_center'] = utils.split_3cols(utils.genres_nonfiction)['center']
        params['nonfiction_genres_right'] = utils.split_3cols(utils.genres_nonfiction)['right']

        return self.render_template('edit_author_profile.html', **params)

    def post(self):
        """ Get fields from POST dict """

        checked_genres = self.request.POST.get('checked_genres').replace('&', '').replace('+', ' ').replace('%26', '&').split('genres=')[1:]
        print checked_genres

        pseudonyms = self.request.POST.get('pseudonyms').replace('  ', ' ').replace(' ,', ',').split(',')
        pseudonyms = [i.lstrip().rstrip() for i in pseudonyms]

        k = models.User.get_by_id(long(self.user_id)).key

        author_profile = bmodels.AuthorProfile.get_by_userkey(k)
        if not author_profile:
            author_profile = bmodels.AuthorProfile()
            author_profile.user = k

        try:
            message = ''
            author_profile.name = self.request.POST.get('name')
            author_profile.title = self.request.POST.get('title')
            author_profile.overview = self.request.POST.get('overview').replace('\r\r\n', '\r\n')
            author_profile.ghostwrites = (self.request.POST.get('ghostwrites') == "True")
            author_profile.genres = checked_genres
            author_profile.pseudonyms = pseudonyms
            author_profile.put()
            message += " " + _('Your author profile has been updated.')
            self.add_message(message, 'success')
            self.redirect('/settings/profile')

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error creating/updating author profile: ' + e)
            message = _('Unable to create/update author profile. Please try again later.')
            self.add_message(message, 'error')
            return self.get()


class JobPostHandler():
    """
    fields:
    - Job (select)
    - Title (text)
    - description (textarea)
    - estimated duration (select: more than 6 months, 3 to 6 months, 1 to 3 months, less than 1 month, less than 1 week)
    - job post visibility (Public - All contractors will be able to see your job and apply to it.; Invitation-Only - Only contractors you invite will be able to view and apply to your job.)
    - attachment
    - estimated start date
    - looking to be staff member (can only work for this publishing house)
    """
    pass
