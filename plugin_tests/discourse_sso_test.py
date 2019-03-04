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
from girder.utility.server import loadRouteTable
import hashlib
import hmac

from girder.models.group import Group
from girder.models.setting import Setting
from isic_archive import User
from pytest_girder.assertions import assertStatus
from six.moves import urllib

from girder.models.model_base import ValidationException

from girder_discourse_sso import DiscourseSSO
from girder_discourse_sso.constants import PluginSettings
import pytest


def assertSignature(secret, payload, expectedSignature):
    """Assert that HMAC-SHA256 digest matches expected signature."""
    computedSignature = hmac.new(key=secret, msg=payload, digestmod=hashlib.sha256).hexdigest()
    assert expectedSignature == computedSignature


@pytest.mark.plugin('girder_discourse_sso', DiscourseSSO)
def testDiscourseLogin(server, user, admin):
    group1 = Group().createGroup(
        name='Group 1',
        creator=user
    )
    Group().addUser(group1, user)
    group2 = Group().createGroup(
        name='Group&2',
        creator=user
    )
    Group().addUser(group2, user)

    # Configure plugin settings
    Setting().set(
        PluginSettings.DISCOURSE_SSO_SECRET,
        '0123456789')

    # Test when not logged in
    resp = server.request(
        path='/girder_discourse_sso',
        appPrefix='/girder_discourse_sso',
        prefix='',
        user=None,
        params={
            'sso': 'bm9uY2U9Y2RlNWQ5NWYyNzA2MmViMDljOTg3MzZjM2YyYWVjY2Umc'
                   'mV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5sb2'
                   'NhbGhvc3QuY29tJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg==',
            'sig': '3bdd07d3b8720c0e464715c43874bbb640213de2b54885dff2266061a174e9a1'
        },
        isJson=False)
    assertStatus(resp, 303)

    # Test digest mismatch
    resp = server.request(
        path='/girder_discourse_sso',
        appPrefix='/girder_discourse_sso',
        prefix='',
        user=user,
        params={
            'sso': 'bm9uY2U9Y2RlNWQ5NWYyNzA2MmViMDljOTg3MzZjM2YyYWVjY2Umc'
                   'mV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5sb2'
                   'NhbGhvc3QuY29tJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg==',
            'sig': 'badbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadb'
        })
    assertStatus(resp, 400)
    assert resp.json['message'] == 'Digest mismatch.'

    # Test bad request (missing return_sso_url)
    resp = server.request(
        path='/girder_discourse_sso',
        appPrefix='/girder_discourse_sso',
        prefix='',
        user=user,
        params={
            'sso': 'bm9uY2U9MTExMTE=',
            'sig': '5180d3dd81e8e2e5f48013a8b34153548b952c9e7ac35ac9e9a6edf1694c0683'
        })
    assertStatus(resp, 400)
    assert resp.json['message'] == 'Bad request.'

    # Test bad request (missing nonce)
    resp = server.request(
        path='/girder_discourse_sso',
        appPrefix='/girder_discourse_sso',
        prefix='',
        user=user,
        params={
            'sso': 'cmV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmxvY2FsaG9zdCUyRnJldHVybl9zc29fdXJs',
            'sig': '0df632d04824162d7622af6c2e67ee7e816eb2b7b73cdc208c3892e6954f4df8'
        })
    assertStatus(resp, 400)
    assert resp.json['message'] == 'Bad request.'

    # Test proper request
    resp = server.request(
        path='/girder_discourse_sso',
        appPrefix='/girder_discourse_sso',
        prefix='',
        user=user,
        params={
            'sso': 'bm9uY2U9Y2RlNWQ5NWYyNzA2MmViMDljOTg3MzZjM2YyYWVjY2Umc'
                   'mV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5sb2'
                   'NhbGhvc3QuY29tJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg==',
            'sig': '3bdd07d3b8720c0e464715c43874bbb640213de2b54885dff2266061a174e9a1'
        },
        isJson=False)
    assertStatus(resp, 303)
    url = resp.headers['Location']
    parsedUrl = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsedUrl.query)
    assert 'sso' in params and 'sig' in params
    sso = params['sso'][0]
    sig = params['sig'][0]

    assertSignature(
        secret='0123456789'.encode('utf-8'),
        payload=sso.encode('utf-8'),
        expectedSignature=sig)

    sso = base64.b64decode(sso)
    sso = sso.decode('utf-8')
    parsed = urllib.parse.parse_qs(sso)

    for key in ('nonce', 'email', 'external_id', 'username', 'name',
         'require_activation', 'admin', 'add_groups'):
        assert key in parsed
    assert parsed['nonce'][0] == 'cde5d95f27062eb09c98736c3f2aecce'
    assert parsed['email'][0] == 'user1@email.com'
    assert parsed['external_id'][0] == str(user['_id'])
    assert parsed['username'][0] == 'user1login'
    assert parsed['name'][0] == 'First Last'
    assert parsed['require_activation'][0] == 'true'
    assert parsed['admin'][0] == 'false'
    assert parsed['add_groups'][0] == 'Group 1,Group&2'

    # Test proper request for admin user
    resp = server.request(
        path='/girder_discourse_sso',
        appPrefix='/girder_discourse_sso',
        prefix='',
        user=admin,
        params={
            'sso': 'bm9uY2U9Y2RlNWQ5NWYyNzA2MmViMDljOTg3MzZjM2YyYWVjY2Umc'
                   'mV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5sb2'
                   'NhbGhvc3QuY29tJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg==',
            'sig': '3bdd07d3b8720c0e464715c43874bbb640213de2b54885dff2266061a174e9a1'
        },
        isJson=False)
    assertStatus(resp, 303)
    url = resp.headers['Location']
    parsedUrl = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsedUrl.query)
    assert 'sso' in params and 'sig' in params
    sso = params['sso'][0]
    sig = params['sig'][0]

    assertSignature(
        secret='0123456789'.encode('utf-8'),
        payload=sso.encode('utf-8'),
        expectedSignature=sig)

    sso = base64.b64decode(sso)
    sso = sso.decode('utf-8')
    parsed = urllib.parse.parse_qs(sso)

    for key in ('nonce', 'email', 'external_id', 'username', 'name',
         'require_activation', 'admin'):
        assert key in parsed
    assert parsed['nonce'][0] == 'cde5d95f27062eb09c98736c3f2aecce'
    assert parsed['email'][0] == 'user2@email.com'
    assert parsed['external_id'][0] == str(admin['_id'])
    assert parsed['username'][0] == 'user2login'
    assert parsed['name'][0] == 'Admin Last'
    assert parsed['require_activation'][0] == 'false'
    assert parsed['admin'][0] == 'true'
    assert 'add_groups' not in parsed


@pytest.mark.plugin('girder_discourse_sso', DiscourseSSO)
def testSsoSecretSettingValidation(server):
    """Test validation of SSO secret setting."""
    # Test valid SSO secret settings
    Setting().set(
        PluginSettings.DISCOURSE_SSO_SECRET,
        '0000000000')
    Setting().set(
        PluginSettings.DISCOURSE_SSO_SECRET,
        'j2zNLBXBsurcU0LfypwR')
    Setting().set(
        PluginSettings.DISCOURSE_SSO_SECRET,
        '0000000000')

    # Test invalid SSO secret settings
    with pytest.raises(
        ValidationException):
        Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, None)
    with pytest.raises(
        ValidationException):
        Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, 1)
    with pytest.raises(
        ValidationException):
        Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, '')
    with pytest.raises(
        ValidationException):
        Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, '00000')
    with pytest.raises(
        ValidationException):
        Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, '000000000')
