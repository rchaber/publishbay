"""
Using redirect route instead of simple routes since it supports strict_slash
Simple route: http://webapp-improved.appspot.com/guide/routing.html#simple-routes
RedirectRoute: http://webapp-improved.appspot.com/api/webapp2_extras/routes.html#webapp2_extras.routes.RedirectRoute
"""

from webapp2_extras.routes import RedirectRoute
from web import handlers
from web import browse_handlers
from web import publisher_handlers
from web import author_handlers
secure_scheme = 'https'

_routes = [
    RedirectRoute('/secure/', handlers.SecureRequestHandler, name='secure', strict_slash=True),

    RedirectRoute('/settings/social', handlers.EditAssociationsHandler, name='edit-associations', strict_slash=True),
    RedirectRoute('/social_login/<provider_name>/delete', handlers.DeleteSocialProviderHandler, name='delete-social-provider', strict_slash=True),
    RedirectRoute('/settings/prodetails', handlers.EditProDetailsHandler, name='edit-prodetails', strict_slash=True),
    RedirectRoute('/settings/display_prodetails', handlers.DisplayProDetailsHandler, name='display-prodetails', strict_slash=True),
    RedirectRoute('/settings/display_publishinghouse', handlers.DisplayPublishingHouseHandler, name='display-publishinghouse', strict_slash=True),
    RedirectRoute('/settings/publishinghouse', handlers.EditPublishingHouseHandler, name='edit-publishinghouse', strict_slash=True),
    RedirectRoute('/settings/display_authorprofile', handlers.DisplayAuthorProfileHandler, name='display-authorprofile', strict_slash=True),
    RedirectRoute('/settings/authorprofile', handlers.EditAuthorProfileHandler, name='edit-authorprofile', strict_slash=True),

    RedirectRoute('/settings/display_contactinfo', handlers.DisplayContactInfoHandler, name='display-contactinfo', strict_slash=True),
    RedirectRoute('/settings/contactinfo', handlers.EditContactInfoHandler, name='edit-contactinfo', strict_slash=True),
    RedirectRoute('/settings/basic', handlers.BasicSettingsHandler, name='basic-settings', strict_slash=True),
    RedirectRoute('/upload_picture', handlers.BasicSettingsHandler, name='upload-picture', strict_slash=True),
    RedirectRoute('/upload_logo', handlers.EditPublishingHouseHandler, name='upload-logo', strict_slash=True),

    RedirectRoute('/browse/contractors', browse_handlers.BrowseContractorsHandler, name='browse-contractors', strict_slash=True),
    RedirectRoute('/browse/contractors/view', browse_handlers.ViewContractorsHandler, name='view-contractors', strict_slash=True),
    RedirectRoute('/browse/contractors/mark', handlers.SaveContractorHandler, name='save-contractor', strict_slash=True),
    RedirectRoute('/browse/viewsavedcontractors', browse_handlers.ViewSavedContractorsHandler, name='view-saved-contractors', strict_slash=True),

    RedirectRoute('/browse/authors', browse_handlers.BrowseAuthorsHandler, name='browse-authors', strict_slash=True),
    RedirectRoute('/browse/authors/view', browse_handlers.ViewAuthorsHandler, name='view-authors', strict_slash=True),
    RedirectRoute('/browse/authors/mark', handlers.SaveAuthorHandler, name='save-author', strict_slash=True),
    RedirectRoute('/browse/authors/viewmanuscript', browse_handlers.ViewManuscriptDetailsHandler, name='view-manuscript-details', strict_slash=True),
    RedirectRoute('/browse/viewsavedauthors', browse_handlers.ViewSavedAuthorsHandler, name='view-saved-authors', strict_slash=True),

    RedirectRoute('/browse/manuscripts', browse_handlers.BrowseManuscriptsHandler, name='browse-manuscripts', strict_slash=True),

    RedirectRoute('/browse/publishinghouses', browse_handlers.BrowsePublishingHousesHandler, name='browse-publishinghouses', strict_slash=True),
    RedirectRoute('/browse/publishinghouses/view', browse_handlers.ViewPublishingHousesHandler, name='view-publishinghouses', strict_slash=True),
    RedirectRoute('/browse/publishinghouses/mark', handlers.SavePublishingHouseHandler, name='save-publishinghouse', strict_slash=True),
    RedirectRoute('/browse/viewsavedpublishinghouses', browse_handlers.ViewSavedPublishingHousesHandler, name='view-saved-publishinghouses', strict_slash=True),

    RedirectRoute('/author/editmanuscript', author_handlers.EditManuscriptHandler, name='edit-manuscript', strict_slash=True),
    RedirectRoute('/author/upload_manuscript', author_handlers.UploadManuscriptHandler, name='upload-manuscript', strict_slash=True),
    RedirectRoute('/author/delete_manuscript', author_handlers.RemoveManuscriptHandler, name='delete-full-manuscript-file', strict_slash=True),
    RedirectRoute('/author/mymanuscripts', author_handlers.MyManuscriptsHandler, name='my-manuscripts', strict_slash=True),
    RedirectRoute('/author/viewmanuscript', author_handlers.ViewManuscriptHandler, name='view-manuscript', strict_slash=True),
    RedirectRoute('/author/submitmanuscript', author_handlers.SubmitManuscriptHandler, name='submit-manuscript', strict_slash=True),
    RedirectRoute('/author/mysubmissions', author_handlers.MySubmissionsHandler, name='my-submissions', strict_slash=True),
    RedirectRoute('/author/manuscript_sample', author_handlers.ManuscriptSampleHandler, name='manuscript-sample', strict_slash=True),

    RedirectRoute('/author/viewupdate_submission', author_handlers.AuthorViewUpdateSubmissionHandler, name='author-viewupdate-submission', strict_slash=True),
    RedirectRoute('/publisher/viewupdate_submission', publisher_handlers.PublisherViewUpdateSubmissionHandler, name='publisher-viewupdate-submission', strict_slash=True),

    RedirectRoute('/author/loadcoverletter', author_handlers.LoadCoverletterHandler, name='load-coverletter', strict_slash=True),
    RedirectRoute('/publisher/loadresponseletter', publisher_handlers.LoadResponseLetterHandler, name='load-responseletter', strict_slash=True),
    RedirectRoute('/author/loadproposalletter', author_handlers.LoadProposalLetterHandler, name='load-proposalletter', strict_slash=True),

    RedirectRoute('/publisher/submissionsreceived', publisher_handlers.SubmissionsReceivedHandler, name='submissions-received', strict_slash=True),
    RedirectRoute('/publisher/respondinquiry', publisher_handlers.RespondInquiryHandler, name='respond-inquiry', strict_slash=True),
    RedirectRoute('/publisher/view_responseletter', publisher_handlers.ViewResponseLetterHandler, name='view-responseletter', strict_slash=True),

]


def get_routes():
    return _routes


def add_routes(app):
    if app.debug:
        secure_scheme = 'http'
    for r in _routes:
        app.router.add(r)
