#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

import six

from girder.models.model_base import ValidationException
from girder.utility import setting_utilities
from girder.utility.plugin_utilities import registerPluginWebroot

from .constants import PluginSettings
from . import api


@setting_utilities.validator(PluginSettings.DISCOURSE_SSO_SECRET)
def validateSsoSecret(doc):
    """Validate SSO secret setting."""
    if not doc['value']:
        raise ValidationException('Discourse SSO secret is required.', 'value')
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException(
            'Discourse SSO secret must be a string.', 'value')
    if len(doc['value']) < 10:
        raise ValidationException(
            'Discourse SSO secret must be at least 10 characters.', 'value')


def load(info):
    registerPluginWebroot(api.DiscourseSsoWebroot(), 'discourse_sso')
