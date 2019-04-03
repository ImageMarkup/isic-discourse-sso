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

import base64
import hashlib
import hmac
import urllib.parse

import cherrypy
import pkg_resources

from girder.api.rest import getCurrentUser, RestException
from girder.utility.model_importer import ModelImporter
from girder.utility.webroot import WebrootBase

from isic_discourse_sso.constants import PluginSettings


class DiscourseSsoWebroot(WebrootBase):
    def __init__(self, templatePath=None):
        if not templatePath:
            templatePath = pkg_resources.resource_filename('isic_discourse_sso', 'webroot.mako')
        super(DiscourseSsoWebroot, self).__init__(templatePath)

        self.vars = {'apiRoot': '/api/v1', 'staticRoot': '/static', 'title': 'ISIC Archive Login'}

    def GET(self, **params):
        # Allow cookies for the rest of the request; normally, this would be done in "handleRoute"
        # after setting a decorator, but this endpoint may return HTML, so it doesn't use the normal
        # Girder API utilities
        setattr(cherrypy.request, 'girderAllowCookie', True)

        user = getCurrentUser()
        if not user:
            return self._renderHTML()

        try:
            # self.requireParams(('sso', 'sig'), params)
            sso = params.get('sso')
            if not sso:
                raise RestException('missing parameter: sso')
            sig = params.get('sig')
            if not sig:
                raise RestException('missing parameter: sig')

            self.redirect(user, sso, sig)
        except RestException:
            raise cherrypy.HTTPRedirect('/')

    def redirect(self, user, sso, sig):
        """
        Discourse Single-Sign-On provider implementation.

        Allows using Girder authentication in place of Discourse authentication to avoid users
        having to create an additional account.
        https://meta.discourse.org/t/official-single-sign-on-for-discourse/13045

        'sso', 'SSO payload from Discourse.'
        'sig', 'HMAC-SHA256 hexadecimal digest of payload.'
        """
        Group = ModelImporter.model('group')
        Setting = ModelImporter.model('setting')

        secret = Setting.get(PluginSettings.DISCOURSE_SSO_SECRET)

        secret = secret.encode('utf-8')
        sso = sso.encode('utf-8')

        # Ensure HMAC-SHA256 digest matches provided signature
        if sig != hmac.new(key=secret, msg=sso, digestmod=hashlib.sha256).hexdigest():
            raise RestException('Digest mismatch.')

        # Extract nonce and return URL
        qs = base64.b64decode(sso)
        qs = qs.decode('utf-8')
        parsed = urllib.parse.parse_qs(qs)
        if 'nonce' not in parsed or 'return_sso_url' not in parsed:
            raise RestException('Bad request.')
        nonce = parsed['nonce'][0]
        url = parsed['return_sso_url'][0]

        payload = {
            'nonce': nonce,
            'email': user['email'],
            'external_id': str(user['_id']),
            'username': user['login'],
            'name': '%s %s' % (user['firstName'], user['lastName']),
            'require_activation': 'false' if user['emailVerified'] else 'true',
            'admin': 'true' if user['admin'] else 'false',
            # Note, this list matches Discourse groups' "name" (which may only include numbers,
            # letters and underscores), not "Full Name" (which is human readable), so it may be of
            # limited utility
            'add_groups': ','.join(
                group['name'] for group in Group.find({'_id': {'$in': user.get('groups', [])}})
            ),
        }
        payload = urllib.parse.urlencode(payload)
        payload = payload.encode('utf-8')
        payload = base64.b64encode(payload)

        digest = hmac.new(key=secret, msg=payload, digestmod=hashlib.sha256).hexdigest()

        args = urllib.parse.urlencode({'sso': payload, 'sig': digest})

        raise cherrypy.HTTPRedirect(url + '?' + args)
