# -*- coding: utf-8 -*-
from mock import MagicMock
from zeit.web.core.comments import get_thread
from zeit.web.core.security import CommunityAuthenticationPolicy
from zeit.web.core.security import get_community_user_info
import pytest


@pytest.fixture
def policy():
    return CommunityAuthenticationPolicy()


def test_cookieless_request_returns_nothing(policy, dummy_request):
    assert policy.authenticated_userid(dummy_request) is None


def test_cookieless_request_clears_session(policy, dummy_request):
    dummy_request.session['user'] = dict(uid='bar')
    policy.authenticated_userid(dummy_request)
    assert 'user' not in dummy_request.session


def test_session_cache_has_precedence(policy, dummy_request):
    dummy_request.cookies['drupal-userid'] = 23
    dummy_request.session['user'] = dict(uid=23, name='s3crit')
    assert policy.authenticated_userid(dummy_request) == 23
    assert dummy_request.session['user']['name'] == 's3crit'


def test_session_cache_cleared_when_id_changes(
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
    mockserver_factory(user_xml)
    dummy_request.cookies['drupal-userid'] = 23
    # Session still contains old user id and sensitive information
    dummy_request.session['user'] = dict(uid=42, name='s3crit')
    dummy_request.cookies['drupal-userid'] = 23
    dummy_request.headers['Cookie'] = ''
    assert policy.authenticated_userid(dummy_request) == '457322'
    assert dummy_request.session['user']['name'] == 'test-user'


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
    mockserver_factory(user_xml)
    dummy_request.cookies['drupal-userid'] = 23
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
    user_info = dict(uid=0, name=None, picture=None, roles=[], mail=None)
    assert get_community_user_info(dummy_request) == user_info


@pytest.mark.xfail(reason='Testing broken dependencies is an unsolved issue.')
def test_malformed_agatho_response_should_not_produce_error(http_testserver):
    mocked_request = MagicMock()
    mocked_request.registry.settings['agatho_host'] = (
        'http://localhost:8889')
    assert get_thread('http://xml.zeit.de/artikel/01', mocked_request) is None


@pytest.mark.xfail(reason='Testing broken dependencies is an unsolved issue.')
def test_malformed_community_response_should_not_produce_error(
        dummy_request, http_testserver):
    dummy_request.registry.settings['community_host'] = (
        'http://localhost:8889')
    dummy_request.cookies['drupal-userid'] = 23
    dummy_request.headers['Cookie'] = ''
    user_info = dict(uid=0, name=None, picture=None, roles=[], mail=None)
    assert get_community_user_info(dummy_request) == user_info
