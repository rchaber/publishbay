from wtforms import fields
from wtforms import Form
from wtforms import validators
from boilerplate.lib import utils
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.i18n import ngettext, gettext

from boilerplate import forms as forms

FIELD_MAXLENGTH = 50  # intended to stop maliciously long input


class EditContactInfo(forms.BaseForm):
    address1 = fields.TextField(_('Address 1'), [validators.Length(max=FIELD_MAXLENGTH)])
    address2 = fields.TextField(_('Address 2'), [validators.Length(max=FIELD_MAXLENGTH)])
    city = fields.TextField(_('City'), [validators.Length(max=FIELD_MAXLENGTH)])
    state = fields.TextField(_('State'), [validators.Length(max=FIELD_MAXLENGTH)])
    zipcode = fields.TextField(_('ZIP'), [validators.Length(max=FIELD_MAXLENGTH)])
    phone1 = fields.TextField(_('Phone 1'), [validators.Length(max=FIELD_MAXLENGTH)])
    phone2 = fields.TextField(_('Phone 2'), [validators.Length(max=FIELD_MAXLENGTH)])
    pass
