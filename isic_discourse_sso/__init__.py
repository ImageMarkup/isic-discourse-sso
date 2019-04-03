# -*- coding: utf-8 -*-
from girder.models.model_base import ValidationException
from girder.plugin import getPlugin, GirderPlugin, registerPluginWebroot
from girder.utility import setting_utilities

from isic_discourse_sso import api
from isic_discourse_sso.constants import PluginSettings


@setting_utilities.validator(PluginSettings.DISCOURSE_SSO_SECRET)
def validateSsoSecret(doc):
    """Validate SSO secret setting."""
    if not doc['value']:
        raise ValidationException('Discourse SSO secret is required.', 'value')
    if not isinstance(doc['value'], str):
        raise ValidationException('Discourse SSO secret must be a string.', 'value')
    if len(doc['value']) < 10:
        raise ValidationException('Discourse SSO secret must be at least 10 characters.', 'value')


class DiscourseSSO(GirderPlugin):
    DISPLAY_NAME = 'Discourse SSO'

    def load(self, info):
        getPlugin('oauth').load(info)
        registerPluginWebroot(api.DiscourseSsoWebroot(), 'isic_discourse_sso')
