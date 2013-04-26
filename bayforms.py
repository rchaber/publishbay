from wtforms import fields
from wtforms import Form
from wtforms import validators
from boilerplate.lib import utils
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.i18n import ngettext, gettext

from boilerplate import forms as forms

from config import utils as bayutils

FIELD_MAXLENGTH = 50  # intended to stop maliciously long input


class EditProDetails(forms.BaseForm):
    display_full_name = fields.RadioField(_('Display Name'), choices=[('True', _('show your full name')), ('False', _(' - show your first name and last initial'))], coerce=unicode)
    title = fields.TextField(_('Title'), [validators.Length(max=FIELD_MAXLENGTH)])
    profile_visibility = fields.RadioField(_('Profile Visibility'), choices=[
                                                                                ('everyone', _('Anyone can see your profile whether or not they are logged into PublishBay.')), 
                                                                                ('pb_users_only', _('Only PublishBay users who are logged in to PublishBay can see your profile.')), 
                                                                                ('hidden', _('Clients can see your profile only if you have applied to their job.'))
                                                                            ])
    english_level = fields.SelectField(_('English level'), choices=[1, 2, 3, 4, 5])
    address1 = fields.TextField(_('Address 1'), [validators.Length(max=FIELD_MAXLENGTH)])
    address2 = fields.TextField(_('Address 2'), [validators.Length(max=FIELD_MAXLENGTH)])
    city = fields.TextField(_('City'), [validators.Length(max=FIELD_MAXLENGTH)])
    state = fields.TextField(_('State'), [validators.Length(max=FIELD_MAXLENGTH)])
    zipcode = fields.TextField(_('ZIP'), [validators.Length(max=FIELD_MAXLENGTH)])
    phone = fields.TextField(_('Phone'), [validators.Length(max=FIELD_MAXLENGTH)])


class EditPublishingHouse(forms.BaseForm):
    pass