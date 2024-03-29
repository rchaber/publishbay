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

import bayforms as bayforms

from boilerplate import models
from boilerplate.lib.basehandler import BaseHandler
from boilerplate.lib.basehandler import user_required

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

# from google.appengine.api import users
# from google.appengine.api import images

# import urllib2
import urllib

# from pprint import pprint as pprint

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


class DisplayContactInfoHandler(BaseHandler):
    """
    Handler for Displaying User Contact Info
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for edit professional details """

        params = {}

        if self.user:
            user_contacinfo = bmodels.ContactInfo.get_by_userkey(self.user_key)
            if user_contacinfo:
                params['there_is_contactinfo'] = True
                params['address1'] = user_contacinfo.address1
                params['address2'] = user_contacinfo.address2
                params['city'] = user_contacinfo.city
                params['state'] = user_contacinfo.state
                params['zipcode'] = user_contacinfo.zipcode
                params['phone'] = user_contacinfo.phone
            else:
                params['there_is_contactinfo'] = False

        return self.render_template('display_contactinfo.html', **params)


class EditContactInfoHandler(BaseHandler):
    """
    Handler for Edit User Contact Info
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for edit professional details """

        params = {}

        params['there_is_contactinfo'] = False

        if self.user:
            user_contacinfo = bmodels.ContactInfo.get_by_userkey(self.user_key)
            if user_contacinfo:
                params['there_is_contactinfo'] = True
                self.form.address1.data = user_contacinfo.address1
                self.form.address2.data = user_contacinfo.address2
                self.form.city.data = user_contacinfo.city
                self.form.state.data = user_contacinfo.state
                self.form.zipcode.data = user_contacinfo.zipcode
                self.form.phone.data = user_contacinfo.phone

        return self.render_template('edit_contactinfo.html', **params)

    def post(self):
        """ Get fields from POST dict """

        user_contacinfo = bmodels.ContactInfo.get_by_userkey(self.user_key)
        if not user_contacinfo:
            user_contacinfo = bmodels.ContactInfo()
            user_contacinfo.user = self.user_key

        address1 = self.form.address1.data
        address2 = self.form.address2.data
        city = self.form.city.data
        state = self.form.state.data.upper()
        zipcode = self.form.zipcode.data
        phone = self.form.phone.data

        try:
            message = ''
            user_contacinfo.address1 = address1
            user_contacinfo.address2 = address2
            user_contacinfo.city = city
            user_contacinfo.state = state
            user_contacinfo.zipcode = zipcode
            user_contacinfo.phone = phone

            user_contacinfo.put()
            message += " " + _('Your contact info has been updated.')

            self.add_message(message, 'success')
            self.redirect('/settings/profile')

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error updating contact info: ' + str(e))
            message = _('Unable to update contact info. Please try again later.')
            self.add_message(message, 'error')
            return self.get()

    @webapp2.cached_property
    def form(self):
        return bayforms.EditContactInfo(self)


class BasicSettingsHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler for Edit Basic Settings
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for edit basic settings """

        params = {}

        params['upload_url'] = blobstore.create_upload_url('/upload_picture')
        params['display_full_name'] = True
        params['picture_url'] = None

        if self.user:
            user_basicsettings = bmodels.BasicSettings.get_by_userkey(self.user_key)
            if user_basicsettings:
                params['display_full_name'] = user_basicsettings.display_full_name
                if user_basicsettings.picture_key and user_basicsettings.picture_key != '':
                    params['picture_url'] = '/serve/%s' % user_basicsettings.picture_key

        return self.render_template('edit_basic_settings.html', **params)

    def post(self):
        """ Get fields from POST dict """

        upload_picture = self.get_uploads()
        # print upload_picture[0].filename
        if upload_picture:
            picture_key = upload_picture[0].key()
        else:
            picture_key = None

        user_basicsettings = bmodels.BasicSettings.get_by_userkey(self.user_key)
        if not user_basicsettings:
            user_basicsettings = bmodels.BasicSettings()
            user_basicsettings.user = self.user_key

        # if picture changes, then the old one is deleted from Blobstore
        if (picture_key and picture_key != user_basicsettings.picture_key) and user_basicsettings:
            try:
                blobstore.delete(user_basicsettings.picture_key)
            except:
                pass

        display_full_name = (self.request.POST.get('display_full_name') == "True")

        try:
            message = ''
            user_basicsettings.display_full_name = display_full_name
            if picture_key != '':
                user_basicsettings.picture_key = picture_key

            user_basicsettings.put()
            message += " " + _('Basic settings have been updated.')

            self.add_message(message, 'success')
            self.redirect('/settings/profile')

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error updating basic settings: ' + str(e))
            message = _('Unable to update basic settings. Please try again later.')
            self.add_message(message, 'error')
            return self.get()


class DisplayProDetailsHandler(BaseHandler):
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
        params['overviewdata'] = ''
        params['joblist'] = ''

        if self.user:
            user_pro_details = bmodels.ProDetails.get_by_userkey(self.user_key)
            if user_pro_details:
                params['there_is_profile'] = True
                params['title'] = user_pro_details.title
                params['overview'] = user_pro_details.overview
                params['profile_visibility'] = user_pro_details.profile_visibility
                params['english_level'] = user_pro_details.english_level
                params['joblist'] = urllib.unquote(', '.join(user_pro_details.jobs))
            else:
                params['there_is_profile'] = False

        return self.render_template('display_pro_details.html', **params)


class EditProDetailsHandler(BaseHandler):
    """
    Handler for Edit Contractor Info
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
                self.form.title.data = user_pro_details.title
                params['overviewdata'] = user_pro_details.overview
                self.form.profile_visibility.data = user_pro_details.profile_visibility
                self.form.english_level.data = user_pro_details.english_level
                params['english_level'] = user_pro_details.english_level
                params['joblist'] = user_pro_details.jobs

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

        jobs = self.request.POST.getall('jobs')

        user = self.user_key.get()

        user_pro_details = bmodels.ProDetails.get_by_userkey(self.user_key)
        if not user_pro_details:
            user_pro_details = bmodels.ProDetails()
            user_pro_details.user = self.user_key

        overview = self.request.POST.get('overview').replace('\r\r\n', '\r\n')

        title = self.request.POST.get('title')
        profile_visibility = self.form.profile_visibility.data
        english_level = int(self.request.POST.get('english_level'))

        try:
            message = ''
            user_pro_details.title = title
            user_pro_details.overview = overview
            user_pro_details.profile_visibility = profile_visibility
            user_pro_details.english_level = english_level
            user_pro_details.jobs = jobs
            print user_pro_details

            user_pro_details.put()
            message += " " + _('Your contractor info has been updated.')

            self.add_message(message, 'success')
            self.redirect('/settings/profile')

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error updating contractor info: ' + str(e))
            message = _('Unable to update contractor info. Please try again later.')
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
        params['genres'] = ''
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
                params['genres'] = publishing_house.genres
                params['unsolicited'] = publishing_house.unsolicited
                params['show_in_job_posts'] = publishing_house.show_in_job_posts

        print params['genres']
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
        params['genres'] = []
        params['show_in_job_posts'] = ''
        params['logo_url'] = ''
        params['unsolicited'] = True
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
                params['genres'] = [str(i) for i in publishing_house.genres]
                params['show_in_job_posts'] = publishing_house.show_in_job_posts
                params['unsolicited'] = publishing_house.unsolicited

        params['fiction_genres'] = utils.genres_fiction
        params['nonfiction_genres'] = utils.genres_nonfiction

        return self.render_template('edit_publishing_house.html', **params)

    def post(self):
        """ Get fields from POST dict """

        # if not self.form.validate():
            # return self.get()

        checked_genres = self.request.POST.getall('genres')

        upload_logo = self.get_uploads()
        if upload_logo:
            logo_key = upload_logo[0].key()
        else:
            logo_key = ''

        publishing_house = bmodels.PublishingHouse.get_by_ownerkey(self.user_key)
        if not publishing_house:
            publishing_house = bmodels.PublishingHouse()
            publishing_house.owner = self.user_key

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
            publishing_house.unsolicited = (self.request.POST.get('unsolicited') == "True")
            publishing_house.put()
            message += " " + _('Your publishing house info has been updated.')
            self.add_message(message, 'success')
            self.redirect('/settings/profile')

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error creating/updating publishing house: ' + e)
            message = _('Unable to create/update publishing house. Please try again later.')
            self.add_message(message, 'error')
            return self.get()


class DisplayAuthorProfileHandler(BaseHandler):
    """
    Handler for Display Author Profile
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for display author profile """

        params = {}

        params['title'] = ''
        params['pseudonyms'] = ''
        params['overview'] = ''
        params['genres_list'] = ''
        params['freelance'] = ''
        params['ghostwrites'] = ''
        params['there_is_author_profile'] = False

        if self.user:
            author_profile = bmodels.AuthorProfile.get_by_userkey(self.user_key)
            if author_profile:
                params['there_is_author_profile'] = True
                params['title'] = author_profile.title
                params['overview'] = author_profile.overview
                params['pseudonyms'] = urllib.unquote(', '.join(author_profile.pseudonyms))
                params['genres_list'] = author_profile.genres
                params['freelance'] = author_profile.freelance
                params['ghostwrites'] = author_profile.ghostwrites

        return self.render_template('display_author_profile.html', **params)


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
        params['genres_list'] = []
        params['freelance'] = ''
        params['ghostwrites'] = ''
        params['there_is_author_profile'] = False

        if self.user:
            author_profile = bmodels.AuthorProfile.get_by_userkey(self.user_key)
            if author_profile:
                params['title'] = author_profile.title
                params['overview'] = author_profile.overview
                params['pseudonyms'] = ', '.join(author_profile.pseudonyms)
                params['genres'] = [str(i) for i in author_profile.genres]
                params['freelance'] = author_profile.freelance
                params['ghostwrites'] = author_profile.ghostwrites
                params['there_is_author_profile'] = True

        params['fiction_genres'] = utils.genres_fiction
        params['nonfiction_genres'] = utils.genres_nonfiction

        return self.render_template('edit_author_profile.html', **params)

    def post(self):
        """ Get fields from POST dict """

        checked_genres = self.request.POST.getall('genres')

        pseudonyms = self.request.POST.get('pseudonyms').replace('  ', ' ').replace(' ,', ',').split(',')
        pseudonyms = [i.lstrip().rstrip() for i in pseudonyms]

        # k = models.User.get_by_id(long(self.user_id)).key
        print checked_genres
        print pseudonyms

        author_profile = bmodels.AuthorProfile.get_by_userkey(self.user_key)
        if not author_profile:
            author_profile = bmodels.AuthorProfile()
            author_profile.user = self.user_key

        try:
            message = ''
            author_profile.title = self.request.POST.get('title')
            author_profile.overview = self.request.POST.get('overview').replace('\r\r\n', '\r\n')
            author_profile.freelance = (self.request.POST.get('freelance') == "True")
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


class SaveContractorHandler(BaseHandler):

    @user_required
    def get(self):
        contractor_id = self.request.GET.get('contractor_id')
        print "contractor_id: "+contractor_id
        contractor = bmodels.ProDetails.get_by_id(int(contractor_id))
        q = bmodels.Marked_contractors.query(bmodels.Marked_contractors.user == self.user_key, bmodels.Marked_contractors.marked == contractor.key).get()
        js = ''
        if not q:
            mark = bmodels.Marked_contractors()
            mark.user = self.user_key
            mark.marked = contractor.key
            mark.put()
            js = "$('#mark').addClass('marked'); $('.btn .icon-bookmark').css('opacity', '1');"
            js += "$('#mark .icon-bookmark').addClass('icon-white');"
        else:
            q.key.delete()
            js = "$('#mark').removeClass('marked'); $('.btn .icon-bookmark').css('opacity', '.3');"
            js += "$('#mark .icon-bookmark').removeClass('icon-white');"
        print "here2"
        self.response.out.write(js)


class SaveAuthorHandler(BaseHandler):

    @user_required
    def get(self):
        author_id = self.request.GET.get('author_id')
        print "author_id: "+author_id
        author = bmodels.AuthorProfile.get_by_id(int(author_id))
        q = bmodels.Marked_authors.query(bmodels.Marked_authors.user == self.user_key, bmodels.Marked_authors.marked == author.key).get()
        js = ''
        if not q:
            mark = bmodels.Marked_authors()
            mark.user = self.user_key
            mark.marked = author.key
            mark.put()
            js = "$('#mark').addClass('marked'); $('.btn .icon-bookmark').css('opacity', '1');"
            js += "$('#mark .icon-bookmark').addClass('icon-white');"
        else:
            q.key.delete()
            js = "$('#mark').removeClass('marked'); $('.btn .icon-bookmark').css('opacity', '.3');"
            js += "$('#mark .icon-bookmark').removeClass('icon-white');"
        print "here2"
        self.response.out.write(js)


class SavePublishingHouseHandler(BaseHandler):

    @user_required
    def get(self):
        publishinghouse_id = self.request.GET.get('publishinghouse_id')
        publishinghouse = bmodels.PublishingHouse.get_by_id(int(publishinghouse_id))
        q = bmodels.Marked_publishinghouses.query(bmodels.Marked_publishinghouses.user == self.user_key, bmodels.Marked_publishinghouses.marked == publishinghouse.key).get()
        js = ''
        if not q:
            mark = bmodels.Marked_publishinghouses()
            mark.user = self.user_key
            mark.marked = publishinghouse.key
            mark.put()
            js = "$('#mark').addClass('marked'); $('.btn .icon-bookmark').css('opacity', '1');"
            js += "$('#mark .icon-bookmark').addClass('icon-white');"
        else:
            q.key.delete()
            js = "$('#mark').removeClass('marked'); $('.btn .icon-bookmark').css('opacity', '.3');"
            js += "$('#mark .icon-bookmark').removeClass('icon-white');"
        self.response.out.write(js)
