# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import urllib.parse

import pytest

from girder.models.group import Group
from girder.models.model_base import ValidationException
from girder.models.setting import Setting
from pytest_girder.assertions import assertStatus, assertStatusOk

from isic_discourse_sso import DiscourseSSO
from isic_discourse_sso.settings import PluginSettings


def assert_signature(secret, payload, expected_signature):
    """Assert that HMAC-SHA256 digest matches expected signature."""
    computed_signature = hmac.new(key=secret, msg=payload, digestmod=hashlib.sha256).hexdigest()
    assert expected_signature == computed_signature


@pytest.mark.plugin('isic_discourse_sso', DiscourseSSO)
def test_discourse_login(server, user, admin):
    group1 = Group().createGroup(name='Group 1', creator=user)
    Group().addUser(group1, user)
    group2 = Group().createGroup(name='Group&2', creator=user)
    Group().addUser(group2, user)

    # Configure plugin settings
    Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, '0123456789')

    # Test when not logged in
    resp = server.request(
        path='/discourse_sso',
        user=None,
        params={
            'sso': 'bm9uY2U9Y2RlNWQ5NWYyNzA2MmViMDljOTg3MzZjM2YyYWVjY2Umc'
            'mV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5sb2'
            'NhbGhvc3QuY29tJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg==',
            'sig': '3bdd07d3b8720c0e464715c43874bbb640213de2b54885dff2266061a174e9a1',
        },
    )
    assertStatus(resp, 401)

    # Test digest mismatch
    resp = server.request(
        path='/discourse_sso',
        user=user,
        params={
            'sso': 'bm9uY2U9Y2RlNWQ5NWYyNzA2MmViMDljOTg3MzZjM2YyYWVjY2Umc'
            'mV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5sb2'
            'NhbGhvc3QuY29tJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg==',
            'sig': 'badbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadb',
        },
    )
    assertStatus(resp, 400)

    # Test bad request (missing return_sso_url)
    resp = server.request(
        path='/discourse_sso',
        user=user,
        params={
            'sso': 'bm9uY2U9MTExMTE=',
            'sig': '5180d3dd81e8e2e5f48013a8b34153548b952c9e7ac35ac9e9a6edf1694c0683',
        },
    )
    assertStatus(resp, 400)

    # Test bad request (missing nonce)
    resp = server.request(
        path='/discourse_sso',
        user=user,
        params={
            'sso': 'cmV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmxvY2FsaG9zdCUyRnJldHVybl9zc29fdXJs',
            'sig': '0df632d04824162d7622af6c2e67ee7e816eb2b7b73cdc208c3892e6954f4df8',
        },
    )
    assertStatus(resp, 400)

    # Test proper request
    resp = server.request(
        path='/discourse_sso',
        user=user,
        params={
            'sso': 'bm9uY2U9Y2RlNWQ5NWYyNzA2MmViMDljOTg3MzZjM2YyYWVjY2Umc'
            'mV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5sb2'
            'NhbGhvc3QuY29tJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg==',
            'sig': '3bdd07d3b8720c0e464715c43874bbb640213de2b54885dff2266061a174e9a1',
        },
    )
    assertStatusOk(resp)
    assert 'returnUrl' in resp.json
    return_url = resp.json['returnUrl']
    parsed_url = urllib.parse.urlparse(return_url)
    params = urllib.parse.parse_qs(parsed_url.query)
    assert 'sso' in params and 'sig' in params
    sso = params['sso'][0]
    sig = params['sig'][0]

    assert_signature(
        secret='0123456789'.encode('utf-8'), payload=sso.encode('utf-8'), expected_signature=sig
    )

    sso = base64.b64decode(sso)
    sso = sso.decode('utf-8')
    parsed = urllib.parse.parse_qs(sso)

    for key in (
        'nonce',
        'email',
        'external_id',
        'username',
        'name',
        'require_activation',
        'admin',
        'add_groups',
    ):
        assert key in parsed
    assert parsed['nonce'][0] == 'cde5d95f27062eb09c98736c3f2aecce'
    assert parsed['email'][0] == 'user@email.com'
    assert parsed['external_id'][0] == str(user['_id'])
    assert parsed['username'][0] == 'user'
    assert parsed['name'][0] == 'user user'
    assert parsed['require_activation'][0] == 'true'
    assert parsed['admin'][0] == 'false'
    assert parsed['add_groups'][0] == 'Group 1,Group&2'

    # Test proper request for admin user
    resp = server.request(
        path='/discourse_sso',
        user=admin,
        params={
            'sso': 'bm9uY2U9Y2RlNWQ5NWYyNzA2MmViMDljOTg3MzZjM2YyYWVjY2Umc'
            'mV0dXJuX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRpc2NvdXJzZS5sb2'
            'NhbGhvc3QuY29tJTJGc2Vzc2lvbiUyRnNzb19sb2dpbg==',
            'sig': '3bdd07d3b8720c0e464715c43874bbb640213de2b54885dff2266061a174e9a1',
        },
    )
    assertStatusOk(resp)
    assert 'returnUrl' in resp.json
    return_url = resp.json['returnUrl']
    parsed_url = urllib.parse.urlparse(return_url)
    params = urllib.parse.parse_qs(parsed_url.query)
    assert 'sso' in params and 'sig' in params
    sso = params['sso'][0]
    sig = params['sig'][0]

    assert_signature(
        secret='0123456789'.encode('utf-8'), payload=sso.encode('utf-8'), expected_signature=sig
    )

    sso = base64.b64decode(sso)
    sso = sso.decode('utf-8')
    parsed = urllib.parse.parse_qs(sso)

    for key in ('nonce', 'email', 'external_id', 'username', 'name', 'require_activation', 'admin'):
        assert key in parsed
    assert parsed['nonce'][0] == 'cde5d95f27062eb09c98736c3f2aecce'
    assert parsed['email'][0] == 'admin@email.com'
    assert parsed['external_id'][0] == str(admin['_id'])
    assert parsed['username'][0] == 'admin'
    assert parsed['name'][0] == 'Admin Admin'
    assert parsed['require_activation'][0] == 'false'
    assert parsed['admin'][0] == 'true'
    assert 'add_groups' not in parsed


@pytest.mark.plugin('isic_discourse_sso', DiscourseSSO)
def test_sso_secret_setting_validation(server):
    """Test validation of SSO secret setting."""
    # Test valid SSO secret settings
    Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, '0000000000')
    Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, 'j2zNLBXBsurcU0LfypwR')
    Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, '0000000000')

    # Test invalid SSO secret settings
    with pytest.raises(ValidationException):
        Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, None)
    with pytest.raises(ValidationException):
        Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, 1)
    with pytest.raises(ValidationException):
        Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, '')
    with pytest.raises(ValidationException):
        Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, '00000')
    with pytest.raises(ValidationException):
        Setting().set(PluginSettings.DISCOURSE_SSO_SECRET, '000000000')
