# -*- coding: utf-8 -*-
from girder.models.model_base import ValidationException
from girder.utility import setting_utilities


class PluginSettings:
    DISCOURSE_SSO_SECRET = 'discourse_sso.sso_secret'


@setting_utilities.validator(PluginSettings.DISCOURSE_SSO_SECRET)
def validate_sso_secret(doc):
    """Validate SSO secret setting."""
    if not doc['value']:
        raise ValidationException('Discourse SSO secret is required.', 'value')
    if not isinstance(doc['value'], str):
        raise ValidationException('Discourse SSO secret must be a string.', 'value')
    if len(doc['value']) < 10:
        raise ValidationException('Discourse SSO secret must be at least 10 characters.', 'value')
