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
import cherrypy
import hashlib
import hmac

from six.moves import urllib

from girder.api import access
from girder.api.describe import Description, describeRoute
from girder.api.rest import RestException, Resource
from .constants import PluginSettings


class DiscourseSso(Resource):
    """
    Discourse Single-Sign-On provider implementation. Allows using Girder
    authentication in place of Discourse authentication to avoid users having to
    create an additional account.
    https://meta.discourse.org/t/official-single-sign-on-for-discourse/13045
    """
    def __init__(self):
        super(DiscourseSso, self).__init__()
        self.resourceName = 'discourse_sso'
        self.route('GET', (), self.login)

    @describeRoute(
        Description('Authenticate for Discourse SSO')
        .param('sso', 'SSO payload from Discourse.')
        .param('sig', 'HMAC-SHA256 hexadecimal digest of payload.')
    )
    @access.cookie
    @access.public
    def login(self, params):
        Group = self.model('group')
        Setting = self.model('setting')

        self.requireParams(('sso', 'sig'), params)

        user = self.getCurrentUser()
        if not user:
            # TODO: Improve by automatically continuing Discourse authentication
            # after user logs in, or by providing login view as part of this
            # plugin
            raise cherrypy.HTTPRedirect('/')

        sso = params['sso']
        sig = params['sig']

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
                group['name']
                for group in Group.find({
                    '_id': {'$in': user.get('groups', [])}
                })
            )
        }
        payload = urllib.parse.urlencode(payload)
        payload = payload.encode('utf-8')
        payload = base64.b64encode(payload)

        digest = hmac.new(key=secret, msg=payload, digestmod=hashlib.sha256).hexdigest()

        args = urllib.parse.urlencode({
            'sso': payload,
            'sig': digest
        })

        raise cherrypy.HTTPRedirect(url + '?' + args)
