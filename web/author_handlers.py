# -*- coding: utf-8 -*-

# standard library imports
import logging
import re

# related third party imports
from webapp2_extras.i18n import gettext as _

# local application/library specific imports
from boilerplate.lib.basehandler import BaseHandler
from boilerplate.lib.basehandler import user_required

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

# from google.appengine.api import images

from baymodels import models as bmodels

from datetime import datetime as datetime

import config.utils as utils
from pprint import pprint as pprint


class EditManuscriptHandler(BaseHandler):
    """
    Handler for Add/Update Manuscript
    """

    @user_required
    def get(self):
        """ Returns a simple HTML form for adding/updating a manuscript """

        manuscript_id = self.request.GET.get('manuscript_id')

        params = {}

        if manuscript_id:
            manuscript = bmodels.Manuscript.get_by_id(long(manuscript_id))
            if manuscript.full_manuscript_key and manuscript.full_manuscript_key != '':
                params['full_manuscript_url'] = '/serve/%s' % manuscript.full_manuscript_key
            params['title'] = manuscript.title
            params['tagline'] = manuscript.tagline
            params['summary'] = manuscript.summary
            params['sample'] = re.sub(r'[\n\r]', r' ', manuscript.sample)
            params['genres_list'] = [str(i) for i in manuscript.genres]
            params['display_manuscript'] = manuscript.display
            params['co_authors'] = ', '.join(manuscript.co_authors)
            params['ownership'] = False
            params['is_new_manuscript'] = False
            params['manuscript_id'] = manuscript_id
        else:
            params['title'] = ''
            params['tagline'] = ''
            params['summary'] = ''
            params['sample'] = ''
            params['genres_list'] = []
            params['display_manuscript'] = 'pb_users'
            params['co_authors'] = ''
            params['ownership'] = False
            params['is_new_manuscript'] = True

        params['fiction_genres'] = utils.genres_fiction
        params['nonfiction_genres'] = utils.genres_nonfiction

        params['new_manuscript'] = (self.request.GET.get('new_manuscript') == 'True')

        return self.render_template('/author/edit_manuscript.html', **params)

    def post(self):
        """ Get fields from POST dict """

        checked_genres = self.request.POST.getall('genres')

        manuscript_id = self.request.POST.get('manuscript_id')

        if manuscript_id:
            manuscript = bmodels.Manuscript.get_by_id(long(manuscript_id))
        else:
            manuscript = bmodels.Manuscript()

        co_authors = self.request.POST.get('co_authors')
        if co_authors:
            co_authors = co_authors.split(',')
            co_authors = [c.strip() for c in co_authors]
        else:
            co_authors = []

        try:
            message = ''
            manuscript.user = self.user_key
            manuscript.author = bmodels.AuthorProfile.get_by_userkey(self.user_key).key
            manuscript.title = self.request.POST.get('title')
            manuscript.tagline = self.request.POST.get('tagline')
            manuscript.summary = self.request.POST.get('summary').replace('\r\r\n', '\r\n')
            manuscript.genres = checked_genres
            manuscript.display = self.request.POST.get('display_manuscript')
            manuscript.co_authors = co_authors
            manuscript.ownership = (self.request.POST.get('ownership') == 'True')
            manuscript.sample = self.request.POST.get('wysiwyg').replace('\r\r\n', '\r\n')
            manuscript.put()
            message += " " + _('Your manuscript has been created/updated.')
            self.add_message(message, 'success')
            self.redirect('/')

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error creating/updating manuscript: ' + e)
            message = _('Unable to create/update manuscript. Please try again later.')
            self.add_message(message, 'error')
            return self.get()


class RemoveManuscriptHandler(BaseHandler):
    @user_required
    def get(self):
        js = ''
        manuscript = bmodels.Manuscript.get_by_id(long(self.request.GET.get('manuscript_id')))
        try:
            blobstore.delete(manuscript.full_manuscript_key)
            manuscript.full_manuscript_filename = None
            manuscript.full_manuscript_uploaded_on = None
            manuscript.full_manuscript_key = None
            manuscript.put()
            js = '$("#dd-filename, #dd-uploaded").text("-");bootbox.alert("Full manuscript file successfully deleted");'
            print js
        except:
            pass
        self.response.out.write(js)


class UploadManuscriptHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    """
    Handler to upload full manuscripts
    """

    @user_required
    def get(self):

        params = {}
        params['manuscript_id'] = self.request.GET.get('manuscript_id')
        manuscript = bmodels.Manuscript.get_by_id(long(params['manuscript_id']))

        if manuscript.full_manuscript_filename is not None and manuscript.full_manuscript_filename != '':
            params['full_manuscript_filename'] = manuscript.full_manuscript_filename
            if manuscript.full_manuscript_uploaded_on:
                params['uploaded_on'] = datetime.strftime(manuscript.full_manuscript_uploaded_on, '%Y-%m-%d %H:%M:%S')

        params['upload_url'] = blobstore.create_upload_url('/author/upload_manuscript')

        return self.render_template('/author/upload_manuscript.html', **params)

    def post(self):
        """ Get fields from POST dict """

        manuscript_id = self.request.POST.get('manuscript_id')
        manuscript = bmodels.Manuscript.get_by_id(long(manuscript_id))
        upload_full_manuscript = self.get_uploads()

        if upload_full_manuscript:
            try:
                blobstore.delete(manuscript.full_manuscript_key)
            except:
                pass
            full_manuscript_key = upload_full_manuscript[0].key()
            full_manuscript_filename = upload_full_manuscript[0].filename
            full_manuscript_uploaded_on = datetime.now()
        else:
            full_manuscript_key = None

        pprint(upload_full_manuscript[0].__dict__)
        print upload_full_manuscript[0].filename
        print full_manuscript_key

        try:
            message = ''
            manuscript.full_manuscript_key = full_manuscript_key
            manuscript.full_manuscript_filename = full_manuscript_filename
            manuscript.full_manuscript_uploaded_on = full_manuscript_uploaded_on
            manuscript.put()
            message += " " + _('Full manuscript successfully uploaded.')
            self.add_message(message, 'success')

        except (AttributeError, KeyError, ValueError), e:
            logging.error('Error creating/updating manuscript: ' + e)
            message = _('Unable to create/update manuscript. Please try again later.')
            self.add_message(message, 'error')

        self.redirect('/author/viewmanuscript?mid=%s' % manuscript_id)


class MyManuscriptsHandler(BaseHandler):
    """
    Handler for listing my manuscripts
    """

    @user_required
    def get(self):

        PAGE_SIZE = 5

        manuscripts = []
        params = {}
        items = []

        genrefilter = self.request.GET.getall('genre')

        offset = 0

        new_page = self.request.GET.get('page')
        if new_page:
            new_page = int(new_page)
            offset = int(new_page - 1) * PAGE_SIZE
        else:
            new_page = 1

        query1 = bmodels.Manuscript.query(bmodels.Manuscript.user == self.user_key)

        if genrefilter:
            query = query1.filter(bmodels.Manuscript.genres.IN(genrefilter))
        else:
            query = query1

        count = query.count()
        items = query.fetch(PAGE_SIZE, offset=offset)

        # the following line returns the equivalent to math.ceil(float), just saving from importing another lib
        number_of_pages = count/PAGE_SIZE if count % PAGE_SIZE == 0 else count/PAGE_SIZE + 1

        for i in items:
            d = {}
            d['manuscript_id'] = i.key.id()
            d['title'] = i.title
            d['tagline'] = i.tagline
            d['summary'] = i.summary.replace('\r\n', ' ').replace('\n', ' ')
            d['genres'] = i.genres
            d['co_authors'] = ', '.join(i.co_authors)
            manuscripts.append(d)

        paging = utils.pagination(number_of_pages, new_page, 5) if len(manuscripts) > 0 else [[1], 0]

        params['count'] = count
        params['manuscripts'] = manuscripts

        params['marks'] = paging[0] if len(paging) > 0 else 'no_marks'
        params['active'] = 'mark_' + str(paging[0][paging[1]]) if len(paging) > 0 else 'no_marks'
        params['previous'] = str(new_page - 1) if new_page > 1 else None
        params['next'] = str(new_page + 1) if new_page < number_of_pages else None

        params['genrelist_fiction'] = utils.genres_fiction
        params['genrelist_nonfiction'] = utils.genres_nonfiction
        params['genres'] = genrefilter

        return self.render_template('/author/mymanuscripts.html', **params)


class ViewManuscriptHandler(BaseHandler):

    @user_required
    def get(self):

        manuscript_id = self.request.GET.get('mid')

        manuscript = bmodels.Manuscript.get_by_id(long(manuscript_id))

        params = {}

        params['manuscript_id'] = manuscript_id
        params['title'] = manuscript.title
        params['tagline'] = manuscript.tagline
        params['summary'] = manuscript.summary
        params['co_authors'] = ', '.join(manuscript.co_authors)
        params['genres'] = manuscript.genres
        params['display_manuscript'] = manuscript.display
        params['sample'] = manuscript.sample
        params['full_manuscript_filename'] = manuscript.full_manuscript_filename

        return self.render_template('/author/view_manuscript.html', **params)


class SubmitManuscriptHandler(BaseHandler):

    @user_required
    def get(self):

        manuscript_id = self.request.GET.get('manuscript_id')

        manuscript = bmodels.Manuscript.get_by_id(long(manuscript_id))

        params = {}
        publishinghouses = []

        q = bmodels.Marked_publishinghouses.query(bmodels.Marked_publishinghouses.user == self.user_key)
        count = q.count()
        items = q.fetch()

        my_publishinghouse_id = bmodels.PublishingHouse.query(bmodels.PublishingHouse.owner == self.user_key).get().key.id()

        for i in items:
            d = {}
            publishinghouse = i.marked.get()
            if publishinghouse.unsolicited:
                d['publishinghouse_id'] = i.marked.get().key.id()
                d['name'] = publishinghouse.name
                if publishinghouse.logo_key != '' and publishinghouse.logo_key:
                    d['logo_url'] = '/serve/%s' % publishinghouse.logo_key
                else:
                    d['logo_url'] = ''
                d['tagline'] = publishinghouse.tagline
                d['description'] = publishinghouse.description.replace('\r\n', ' ').replace('\n', ' ')
                d['genres'] = publishinghouse.genres
                if d['publishinghouse_id'] != my_publishinghouse_id:  # it doesn't include user own publishing house
                    publishinghouses.append(d)
                # if len(genrefilter) > 0:
                #     if len(set(publishinghouse.jobs).intersection(set(genrefilter))) > 0:
                #         publishinghouses.append(d)
                # else:
                #     publishinghouses.append(d)

        c = bmodels.Coverletter.query(bmodels.Coverletter.user == self.user_key).fetch()
        saved_coverletters = [[a.key.id(), a.name] for a in c]

        params['manuscript_id'] = manuscript_id
        params['title'] = manuscript.title
        params['tagline'] = manuscript.tagline
        params['summary'] = manuscript.summary
        params['co_authors'] = ', '.join(manuscript.co_authors)
        params['genres'] = manuscript.genres

        params['count'] = count
        params['publishinghouses'] = sorted(publishinghouses, key=lambda pub: pub['name'])
        params['saved_coverletters'] = saved_coverletters
        # params['genrefilter'] = genrefilter

        return self.render_template('author/submit_manuscript.html', **params)

    def post(self):

        coverletter_save = (self.request.POST.get('coverletter_save_checkbox') == 'True')
        coverletter_checkbox = (self.request.POST.get('coverletter_checkbox') == 'True')

        if coverletter_checkbox:
            content = self.request.POST.get('coverletter').replace('\r', ' ').replace('\n', ' ')
            coverletter_name = self.request.POST.get('coverletter_name').lower().strip()
            if coverletter_name != '' and coverletter_save:
                q = bmodels.Coverletter.query(bmodels.Coverletter.name == coverletter_name).get()
                if not q:
                    q = bmodels.Coverletter()
                    q.user = self.user_key
                    q.name = coverletter_name
                q.content = content
                q.put()

        # check if manuscript has already been submitted to any of the publishing houses
        ph_ids_list = self.request.POST.getall('pid')
        phouses = [bmodels.PublishingHouse.get_by_id(long(p)).key for p in ph_ids_list]
        manuscript = bmodels.Manuscript.get_by_id(long(self.request.POST.get('manuscript_id')))

        already_submitted = bmodels.ManuscriptSubmission.query(bmodels.ManuscriptSubmission.manuscript == manuscript.key, bmodels.ManuscriptSubmission.publishinghouse.IN(phouses)).fetch()

        phouses_already_submitted = [p.publishinghouse for p in already_submitted]

        submission_confirmed = []
        submission_denied = []
        for p in phouses:
            if p not in phouses_already_submitted:
                submission = bmodels.ManuscriptSubmission()
                submission.user = self.user_key
                submission.publishinghouse = p
                submission.manuscript = manuscript.key
                submission.status = 'sent'
                if coverletter_checkbox:
                    submission.coverletter = content
                submission.put()
                submission_confirmed.append(p.get().name)
            else:
                submission_denied.append(p.get().name)

        submission_confirmed = '; '.join(submission_confirmed)
        submission_denied = '; '.join(submission_denied)

        if len(submission_confirmed) > 0:
            message = '<i>"%s"</i> submitted to: %s' % (manuscript.title, submission_confirmed)
            self.add_message(message, 'success')
        if len(submission_denied) > 0:
            message = 'Failed submissions. <i>"%s"</i> already been submitted to: %s' % (manuscript.title, submission_denied)
            self.add_message(message, 'error')

        self.redirect('/')


class LoadCoverletterHandler(BaseHandler):

    @user_required
    def get(self):
        coverletter_id = self.request.GET.get('coverletter_id')
        coverletter = bmodels.Coverletter.get_by_id(long(coverletter_id))
        js = ''
        if coverletter:
            js = "CKEDITOR.instances.coverletter.setData('%s');" % coverletter.content
        self.response.out.write(js)


class MySubmissionsHandler(BaseHandler):

    @user_required
    def get(self):

        status_filter = self.request.GET.get('status_filter') if self.request.GET.get('status_filter') else 'all'

        if status_filter == 'open':
            submissions_fetch = bmodels.ManuscriptSubmission.query(bmodels.ManuscriptSubmission.user == self.user_key, bmodels.ManuscriptSubmission.status.IN(['sent', 'read', 'negotiating'])).fetch()
            status_filter_label = 'Status: open'
        elif status_filter == 'closed':
            submissions_fetch = bmodels.ManuscriptSubmission.query(bmodels.ManuscriptSubmission.user == self.user_key, bmodels.ManuscriptSubmission.status.IN(['rejected', 'accepted', 'pass', 'canceled', 'acquired'])).fetch()
            status_filter_label = 'Status: closed'
        else:
            submissions_fetch = bmodels.ManuscriptSubmission.query(bmodels.ManuscriptSubmission.user == self.user_key).fetch()
            status_filter_label = 'All'

        params = {}
        submissions = []
        for item in submissions_fetch:
            d = {}
            manuscript = item.manuscript.get()
            publishinghouse = item.publishinghouse.get()
            d['submission_id'] = item.key.id()
            d['manuscript_id'] = manuscript.key.id()
            d['manuscript_title'] = manuscript.title
            d['publishinghouse'] = publishinghouse.name
            d['publishinghouse_id'] = publishinghouse.key.id()
            d['status'] = item.status.capitalize()
            d['coverletter'] = True if (item.coverletter and item.coverletter.strip() != '') else False
            d['responseletter'] = True if (item.responseletter and item.responseletter.strip() != '') else False
            d['submitted_on'] = item.submitted_on.strftime('%Y-%m-%d %H:%M')
            d['status_updated_on'] = item.updated_on.strftime('%Y-%m-%d %H:%M')
            d['class'] = utils.cl[utils.sta.index(item.status)]
            submissions.append(d)

        params['status_filter'] = status_filter
        params['status_filter_label'] = status_filter_label
        params['submissions'] = submissions

        return self.render_template('author/mysubmissions.html', **params)
