"""
Using redirect route instead of simple routes since it supports strict_slash
Simple route: http://webapp-improved.appspot.com/guide/routing.html#simple-routes
RedirectRoute: http://webapp-improved.appspot.com/api/webapp2_extras/routes.html#webapp2_extras.routes.RedirectRoute
"""

from webapp2_extras.routes import RedirectRoute
from web import handlers
secure_scheme = 'https'

_routes = [
    RedirectRoute('/secure/', handlers.SecureRequestHandler, name='secure', strict_slash=True),

    RedirectRoute('/settings/social', handlers.EditAssociationsHandler, name='edit-associations', strict_slash=True),
    RedirectRoute('/social_login/<provider_name>/delete', handlers.DeleteSocialProviderHandler, name='delete-social-provider', strict_slash=True),
    RedirectRoute('/settings/prodetails', handlers.EditProDetailsHandler, name='edit-prodetails', strict_slash=True),
    RedirectRoute('/settings/display_prodetails', handlers.DisplayProDetailsHandler, name='display-prodetails', strict_slash=True),
    RedirectRoute('/upload_picture', handlers.EditProDetailsHandler, name='upload-picture', strict_slash=True),
    RedirectRoute('/settings/display_publishinghouse', handlers.DisplayPublishingHouseHandler, name='display-publishinghouse', strict_slash=True),
    RedirectRoute('/settings/publishinghouse', handlers.EditPublishingHouseHandler, name='edit-publishinghouse', strict_slash=True),
    RedirectRoute('/upload_logo', handlers.EditPublishingHouseHandler, name='upload-logo', strict_slash=True),
    RedirectRoute('/settings/display_authorprofile', handlers.DisplayAuthorProfileHandler, name='display-authorprofile', strict_slash=True),
    RedirectRoute('/settings/authorprofile', handlers.EditAuthorProfileHandler, name='edit-authorprofile', strict_slash=True),

]


def get_routes():
    return _routes


def add_routes(app):
    if app.debug:
        secure_scheme = 'http'
    for r in _routes:
        app.router.add(r)
