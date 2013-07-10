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

import config.utils as utils


# submission_status = {'submitted': 'Submitted',
#                      'rev_inq': 'Reviewing Inquiry',
#                      'inq_rej': 'Inquiry Rejected',
#                      'req_prop': 'Requesting Proposal',
#                      'prop_sent': 'Proposal Sent',
#                      'eval_prop': 'Evaluating Proposal',
#                      'prop_rej': 'Proposal Rejected',
#                      'offer': 'Offer',
#                      'deal': 'Deal',
#                      'offer_rej': 'Offer Rejected',
#                      'canceled': 'Canceled',
#                      'development': 'Development',
#                      'published': 'Published'}


class SubmissionsReceivedHandler(BaseHandler):

    @user_required
    def get(self):

        status_filter = self.request.GET.get('status_filter') if self.request.GET.get('status_filter') else 'all'

        phouse_key = bmodels.PublishingHouse.get_by_ownerkey(self.user_key).key

        if status_filter != 'all':
            submissions_fetch = bmodels.ManuscriptSubmission.query(bmodels.ManuscriptSubmission.publishinghouse == phouse_key, bmodels.ManuscriptSubmission.status == status_filter).fetch()
            status_filter_label = 'Status: ' + utils.submission_status[status_filter]
        else:
            submissions_fetch = bmodels.ManuscriptSubmission.query(bmodels.ManuscriptSubmission.publishinghouse == phouse_key).fetch()
            status_filter_label = 'Status: All'

        params = {}
        submissions = []
        for item in submissions_fetch:
            d = {}
            manuscript = item.manuscript.get()
            author = bmodels.AuthorProfile.get_by_userkey(item.user)
            d['submission_id'] = item.key.id()
            d['manuscript_title'] = manuscript.title
            d['author'] = author.name + ' ' + author.last_name
            d['author_id'] = author.key.id()
            d['status'] = utils.submission_status[item.status]
            d['coverletter'] = True if (item.coverletter and item.coverletter.strip() != '') else False
            d['responseletter'] = True if (item.responseletter and item.responseletter.strip() != '') else False
            d['submitted_on'] = item.submitted_on.strftime('%Y-%m-%d %H:%M')
            d['status_updated_on'] = item.updated_on.strftime('%Y-%m-%d %H:%M')
            # d['class'] = utils.cl[utils.sta.index(item.status)]
            submissions.append(d)

        params['status_filter'] = status_filter
        params['status_filter_label'] = status_filter_label
        params['submissions'] = submissions

        return self.render_template('publisher/submissions_received.html', **params)


class ManageSubmissionHandler(BaseHandler):

    @user_required
    def get(self):

        submission_id = self.request.GET.get('submission_id')
        submission = bmodels.ManuscriptSubmission.get_by_id(int(submission_id))

        if submission.status == 'submitted':
            try:
                submission.status = 'rev_inq'
                submission.put()
            except:
                pass

        manuscript = submission.manuscript.get()
        params = {}

        r = bmodels.SavedResponseLetter.query(bmodels.SavedResponseLetter.user == self.user_key).fetch()
        saved_responseletters = [[a.key.id(), a.name] for a in r]

        params['submission_id'] = submission_id
        params['author'] = submission.manuscript.get().user.get().name + ' ' + submission.manuscript.get().user.get().last_name
        params['author_id'] = submission.manuscript.get().author.id()
        params['coverletter'] = submission.coverletter
        params['title'] = manuscript.title
        params['tagline'] = manuscript.tagline
        params['summary'] = manuscript.summary
        params['sample'] = manuscript.sample
        params['genres'] = manuscript.genres
        params['co_authors'] = ', '.join(manuscript.co_authors)
        params['submitted_on'] = submission.submitted_on.strftime('%Y-%m-%d')
        params['status'] = utils.submission_status[submission.status]
        params['status_updated_on'] = submission.updated_on.strftime('%Y-%m-%d %H:%M')
        params['saved_responseletters'] = saved_responseletters

        params['submission_locked'] = False
        if submission.status in utils.submission_status_locked:
            params['submission_locked'] = True

        params['responseletter'] = submission.responseletter

        return self.render_template('publisher/manage_submission.html', **params)

    def post(self):
        """ Get fields from POST dict """

        submission_id = self.request.POST.get('submission_id')
        submission = bmodels.ManuscriptSubmission.get_by_id(int(submission_id))

        responseletter_save = (self.request.POST.get('responseletter_save_checkbox') == 'True')

        content = self.request.POST.get('responseletter').replace('\r', ' ').replace('\n', ' ')
        if content.strip() != '':
            submission.responseletter = content.strip()
        responseletter_name = self.request.POST.get('responseletter_name').lower().strip()
        if responseletter_name != '' and responseletter_save:
            q = bmodels.SavedResponseLetter.query(bmodels.SavedResponseLetter.name == responseletter_name).get()
            if not q:
                q = bmodels.SavedResponseLetter()
                q.user = self.user_key
                q.name = responseletter_name
            q.content = content
            q.put()

        try:
            message = ''
            submission.status = self.request.POST.get('status')

            submission.put()
            message += _('Submission updated and response sent. Please reload.')

            self.add_message(message, 'success')
            if submission.status == 'rejected':
                self.redirect('/publisher/submissionsreceived?status_filter=rejected')
            elif submission.status == 'accepted':
                self.redirect('/publisher/submissionsreceived?status_filter=accepted')
            else:
                self.redirect('/publisher/submissionsreceived')

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error responding submission: ' + str(e))
            message = _('Unable to send response and update submission. Please try again later.')
            self.add_message(message, 'error')
            return self.get()


class LoadResponseLetterHandler(BaseHandler):

    @user_required
    def get(self):
        responseletter_id = self.request.GET.get('responseletter_id')
        responseletter = bmodels.SavedResponseLetter.get_by_id(int(responseletter_id))
        js = ''
        if responseletter:
            js = "CKEDITOR.instances.responseletter.setData('%s');" % responseletter.content
        self.response.out.write(js)


