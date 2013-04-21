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

from baymodels import models as bmodels


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


class EditContactInfoHandler(BaseHandler):
    """
    Handler for Edit User Contact Info
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for edit contact info """

        params = {}
        if self.user:
            user_contact_info = bmodels.ContactInfo.get_by_userkey(self.user_key)
            if user_contact_info:
                self.form.address1.data = user_contact_info.address1
                self.form.address2.data = user_contact_info.address2
                self.form.city.data = user_contact_info.city
                self.form.state.data = user_contact_info.state
                self.form.zipcode.data = user_contact_info.zipcode
                self.form.phone1.data = user_contact_info.phone1
                self.form.phone2.data = user_contact_info.phone2

        return self.render_template('edit_contact_info.html', **params)

    def post(self):
        """ Get fields from POST dict """

        if not self.form.validate():
            return self.get()

        address1 = self.form.address1.data
        address2 = self.form.address2.data
        city = self.form.city.data
        state = self.form.state.data.upper()
        zipcode = self.form.zipcode.data
        phone = self.form.phone.data

        k = models.User.get_by_id(long(self.user_id)).key
        user_contact_info = bmodels.ContactInfo.get_by_userkey(k)

        if not user_contact_info:
            user_contact_info = bmodels.ContactInfo()
            user_contact_info.user = k

        try:
            message = ''
            user_contact_info.address1 = address1
            user_contact_info.address2 = address2
            user_contact_info.city = city
            user_contact_info.state = state
            user_contact_info.zipcode = zipcode
            user_contact_info.phone = phone
            user_contact_info.put()
            message += " " + _('Your contact info has been updated.')
            self.add_message(message, 'success')
            return self.get()

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error updating contact info: ' + e)
            message = _('Unable to update contact info. Please try again later.')
            self.add_message(message, 'error')
            return self.get()

    @webapp2.cached_property
    def form(self):
        return bayforms.EditContactInfo(self)
