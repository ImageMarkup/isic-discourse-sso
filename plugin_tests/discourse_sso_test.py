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

from six.moves import urllib

from girder.models.model_base import ValidationException
from tests import base



def setUpModule():
    base.enabledPlugins.append('discourse_sso')
    base.startServer()


def tearDownModule():
    base.stopServer()


class DiscourseSsoTestCase(base.TestCase):
    def assertSignature(self, secret, payload, expectedSignature):
        """Assert that HMAC-SHA256 digest matches expected signature."""
        computedSignature = hmac.new(key=secret, msg=payload, digestmod=hashlib.sha256).hexdigest()
        self.assertEqual(expectedSignature, computedSignature)

    def testDiscourseLogin(self):
        Group = self.model('group')
        Setting = self.model('setting')
        User = self.model('user')

        # Create users and groups
        # This admin user will automatically have 'emailVerified' == True
        adminUser = User.createUser(
            email='user2@email.com',
            login='user2login',
            firstName='Admin',
            lastName='Last',
            password='user2password',
            admin=True
        )
        normalUser = User.createUser(
            email='user1@email.com',
            login='user1login',
            firstName='First',
            lastName='Last',
            password='user1password',
            admin=False
        )
        group1 = Group.createGroup(
            name='Group 1',
            creator=normalUser
        )
        Group.addUser(group1, normalUser)
        group2 = Group.createGroup(
            name='Group&2',
            creator=normalUser
        )
        Group.addUser(group2, normalUser)

        # Test required parameters
        self.ensureRequiredParams(
            path='/discourse_sso',
            required=('sso', 'sig'),
            user=normalUser)

        # Configure plugin settings
        Setting.set(
            PluginSettings.DISCOURSE_SSO_SECRET,
            '0123456789')

        # Test when not logged in
        resp = self.request(
            path='/discourse_sso',
            user=None,
            params={
                'sso': 'bm9uY2U9Y2RlNWQ5NWYyNzA2MmViMDljOTg3MzZjM2YyYWVjY2Umc'
                       'mV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5sb2'
                       'NhbGhvc3QuY29tJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg==',
                'sig': '3bdd07d3b8720c0e464715c43874bbb640213de2b54885dff2266061a174e9a1'
            },
            isJson=False)
        self.assertRedirect(resp)

        # Test digest mismatch
        resp = self.request(
            path='/discourse_sso',
            user=normalUser,
            params={
                'sso': 'bm9uY2U9Y2RlNWQ5NWYyNzA2MmViMDljOTg3MzZjM2YyYWVjY2Umc'
                       'mV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5sb2'
                       'NhbGhvc3QuY29tJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg==',
                'sig': 'badbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadb'
            })
        self.assertStatus(resp, 400)
        self.assertEqual(resp.json['message'], 'Digest mismatch.')

        # Test bad request (missing return_sso_url)
        resp = self.request(
            path='/discourse_sso',
            user=normalUser,
            params={
                'sso': 'bm9uY2U9MTExMTE=',
                'sig': '5180d3dd81e8e2e5f48013a8b34153548b952c9e7ac35ac9e9a6edf1694c0683'
            })
        self.assertStatus(resp, 400)
        self.assertEqual(resp.json['message'], 'Bad request.')

        # Test bad request (missing nonce)
        resp = self.request(
            path='/discourse_sso',
            user=normalUser,
            params={
                'sso': 'cmV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmxvY2FsaG9zdCUyRnJldHVybl9zc29fdXJs',
                'sig': '0df632d04824162d7622af6c2e67ee7e816eb2b7b73cdc208c3892e6954f4df8'
            })
        self.assertStatus(resp, 400)
        self.assertEqual(resp.json['message'], 'Bad request.')

        # Test proper request
        resp = self.request(
            path='/discourse_sso',
            user=normalUser,
            params={
                'sso': 'bm9uY2U9Y2RlNWQ5NWYyNzA2MmViMDljOTg3MzZjM2YyYWVjY2Umc'
                       'mV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5sb2'
                       'NhbGhvc3QuY29tJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg==',
                'sig': '3bdd07d3b8720c0e464715c43874bbb640213de2b54885dff2266061a174e9a1'
            },
            isJson=False)
        self.assertRedirect(resp)
        url = resp.headers['Location']
        parsedUrl = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsedUrl.query)
        self.assertHasKeys(params, ('sso', 'sig'))
        sso = params['sso'][0]
        sig = params['sig'][0]

        self.assertSignature(
            secret='0123456789'.encode('utf-8'),
            payload=sso.encode('utf-8'),
            expectedSignature=sig)

        sso = base64.b64decode(sso)
        sso = sso.decode('utf-8')
        parsed = urllib.parse.parse_qs(sso)

        self.assertHasKeys(
            parsed,
            ('nonce', 'email', 'external_id', 'username', 'name',
             'require_activation', 'admin', 'add_groups'))
        self.assertEqual(parsed['nonce'][0], 'cde5d95f27062eb09c98736c3f2aecce')
        self.assertEqual(parsed['email'][0], 'user1@email.com')
        self.assertEqual(parsed['external_id'][0], str(normalUser['_id']))
        self.assertEqual(parsed['username'][0], 'user1login')
        self.assertEqual(parsed['name'][0], 'First Last')
        self.assertEqual(parsed['require_activation'][0], 'true')
        self.assertEqual(parsed['admin'][0], 'false')
        self.assertEqual(parsed['add_groups'][0], 'Group 1,Group&2')

        # Test proper request for admin user
        resp = self.request(
            path='/discourse_sso',
            user=adminUser,
            params={
                'sso': 'bm9uY2U9Y2RlNWQ5NWYyNzA2MmViMDljOTg3MzZjM2YyYWVjY2Umc'
                       'mV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5sb2'
                       'NhbGhvc3QuY29tJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg==',
                'sig': '3bdd07d3b8720c0e464715c43874bbb640213de2b54885dff2266061a174e9a1'
            },
            isJson=False)
        self.assertRedirect(resp)
        url = resp.headers['Location']
        parsedUrl = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsedUrl.query)
        self.assertHasKeys(params, ('sso', 'sig'))
        sso = params['sso'][0]
        sig = params['sig'][0]

        self.assertSignature(
            secret='0123456789'.encode('utf-8'),
            payload=sso.encode('utf-8'),
            expectedSignature=sig)

        sso = base64.b64decode(sso)
        sso = sso.decode('utf-8')
        parsed = urllib.parse.parse_qs(sso)

        self.assertHasKeys(
            parsed,
            ('nonce', 'email', 'external_id', 'username', 'name',
             'require_activation', 'admin'))
        self.assertEqual(parsed['nonce'][0], 'cde5d95f27062eb09c98736c3f2aecce')
        self.assertEqual(parsed['email'][0], 'user2@email.com')
        self.assertEqual(parsed['external_id'][0], str(adminUser['_id']))
        self.assertEqual(parsed['username'][0], 'user2login')
        self.assertEqual(parsed['name'][0], 'Admin Last')
        self.assertEqual(parsed['require_activation'][0], 'false')
        self.assertEqual(parsed['admin'][0], 'true')
        self.assertNotIn('add_groups', parsed)

    def testSsoSecretSettingValidation(self):
        """Test validation of SSO secret setting."""
        Setting = self.model('setting')

        # Test valid SSO secret settings
        Setting.set(
            PluginSettings.DISCOURSE_SSO_SECRET,
            '0000000000')
        Setting.set(
            PluginSettings.DISCOURSE_SSO_SECRET,
            'j2zNLBXBsurcU0LfypwR')
        Setting.set(
            PluginSettings.DISCOURSE_SSO_SECRET,
            '0000000000')

        # Test invalid SSO secret settings
        self.assertRaises(
            ValidationException,
            Setting.set, PluginSettings.DISCOURSE_SSO_SECRET, None)
        self.assertRaises(
            ValidationException,
            Setting.set, PluginSettings.DISCOURSE_SSO_SECRET, 1)
        self.assertRaises(
            ValidationException,
            Setting.set, PluginSettings.DISCOURSE_SSO_SECRET, '')
        self.assertRaises(
            ValidationException,
            Setting.set, PluginSettings.DISCOURSE_SSO_SECRET, '00000')
        self.assertRaises(
            ValidationException,
            Setting.set, PluginSettings.DISCOURSE_SSO_SECRET, '000000000')
