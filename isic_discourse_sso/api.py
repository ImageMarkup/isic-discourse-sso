# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import urllib.parse

from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
from girder.api.rest import getCurrentUser, Resource
from girder.exceptions import GirderException, RestException
from girder.models.group import Group
from girder.models.setting import Setting

from isic_discourse_sso.settings import PluginSettings


class DiscourseSsoResource(Resource):
    def __init__(self):
        super().__init__()
        self.resourceName = 'discourse_sso'

        self.route('GET', (), self.discourse_sso)

    @access.user
    @autoDescribeRoute(
        Description('Login via Discourse SSO.')
        .param('sso', 'SSO payload from Discourse.')
        .param('sig', 'HMAC-SHA256 hexadecimal digest of payload.')
        .errorResponse()
    )
    def discourse_sso(self, sso, sig):
        """
        Discourse Single-Sign-On provider implementation.

        Allows using Girder authentication in place of Discourse authentication to avoid users
        having to create an additional account.
        https://meta.discourse.org/t/official-single-sign-on-for-discourse/13045
        """
        user = getCurrentUser()

        secret = Setting().get(PluginSettings.DISCOURSE_SSO_SECRET)
        if not secret:
            raise GirderException('Setting DISCOURSE_SSO_SECRET is not set.')

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
                group['name'] for group in Group().find({'_id': {'$in': user.get('groups', [])}})
            ),
        }
        payload = urllib.parse.urlencode(payload)
        payload = payload.encode('utf-8')
        payload = base64.b64encode(payload)

        digest = hmac.new(key=secret, msg=payload, digestmod=hashlib.sha256).hexdigest()

        args = urllib.parse.urlencode({'sso': payload, 'sig': digest})

        return {'returnUrl': url + '?' + args}
