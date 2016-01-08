# -*- coding: utf-8 -*-
from mock import MagicMock
from zeit.web.core.comments import get_thread
from zeit.web.core.security import AuthenticationPolicy
from zeit.web.core.security import get_community_user_info
import pytest


@pytest.fixture
def policy():
    return AuthenticationPolicy()


def test_cookieless_request_returns_nothing(policy, dummy_request):
    assert policy.authenticated_userid(dummy_request) is None


def test_cookieless_request_clears_session(policy, dummy_request):
    dummy_request.session['user'] = dict(uid='bar')
    policy.authenticated_userid(dummy_request)
    assert 'user' not in dummy_request.session


def test_empty_cache_triggers_backend_fills_cache(
        policy, dummy_request, mockserver_factory):
    user_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <user>
        <uid>457322</uid>
        <name>test-user</name>
        <roles>
            <role>authenticated user</role>
        </roles>
    </user>
    """
    server = mockserver_factory(user_xml)
    dummy_request.registry.settings['community_host'] = server.url
    dummy_request.cookies['my_sso_cookie'] = 'foo'
    dummy_request.headers['Cookie'] = ''
    assert 'user' not in dummy_request.session
    assert policy.authenticated_userid(dummy_request) == '457322'
    assert dummy_request.session['user']['name'] == 'test-user'


@pytest.mark.xfail(reason='Testing misconfigurations is an unsolved issue.')
def test_unreachable_agatho_should_not_produce_error():
    mocked_request = MagicMock()
    mocked_request.registry.settings['agatho_host'] = (
        'http://thisurlshouldnotexist.moep/')
    assert get_thread('http://xml.zeit.de/artikel/01', mocked_request) is None


def test_unreachable_community_should_not_produce_error(dummy_request):
    dummy_request.registry.settings['community_host'] = (
        'http://thisurlshouldnotexist.moep/')
    dummy_request.cookies['drupal-userid'] = 23
    dummy_request.headers['Cookie'] = ''
    user_info = dict(uid=0, name=None, picture=None, roles=[],
                     mail=None, premoderation=False)
    assert get_community_user_info(dummy_request) == user_info


@pytest.mark.xfail(reason='Testing broken dependencies is an unsolved issue.')
def test_malformed_agatho_response_should_not_produce_error(http_testserver):
    mocked_request = MagicMock()
    mocked_request.registry.settings['agatho_host'] = http_testserver.url
    assert get_thread('http://xml.zeit.de/artikel/01', mocked_request) is None


@pytest.mark.xfail(reason='Testing broken dependencies is an unsolved issue.')
def test_malformed_community_response_should_not_produce_error(
        dummy_request, http_testserver):
    dummy_request.registry.settings['community_host'] = http_testserver.url
    dummy_request.cookies['drupal-userid'] = 23
    dummy_request.headers['Cookie'] = ''
    user_info = dict(uid=0, name=None, picture=None, roles=[], mail=None)
    assert get_community_user_info(dummy_request) == user_info


def test_get_community_user_info_strips_malformed_picture_value(
        dummy_request, mockserver_factory):
    user_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <user>
        <picture>0</picture>
    </user>
    """
    server = mockserver_factory(user_xml)
    dummy_request.registry.settings['community_host'] = server.url
    user_info = get_community_user_info(dummy_request)
    assert user_info['picture'] is None


def test_get_community_user_info_replaces_community_host(
        dummy_request, mockserver_factory):
    user_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <user>
        <picture>{server}/picture.png</picture>
    </user>
    """
    server = mockserver_factory(user_xml)
    dummy_request.registry.settings['community_host'] = server.url
    user_info = get_community_user_info(dummy_request)
    assert user_info['picture'] == 'http://static_community/foo/picture.png'
