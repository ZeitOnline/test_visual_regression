import json

import jwt
import mock
import pytest
import requests

from zeit.web.core.comments import get_thread
from zeit.web.core.security import get_user_info
import zeit.web.core.security


def test_reload_community_should_produce_result(mock_metrics, monkeypatch):
    request = mock.Mock()

    def call(self, request, **kwargs):
        return 'result'

    monkeypatch.setattr(requests.Session, 'send', call)

    res = zeit.web.core.security._retry_request(request, 2)
    assert res == 'result'


def test_reload_community_should_be_recalled(mock_metrics, monkeypatch):
    request = mock.Mock().prepare()
    request.called = 0

    def call(self, request, **kwargs):
        request.called = request.called + 1
        raise Exception('provoked')

    monkeypatch.setattr(requests.Session, 'send', call)

    res = zeit.web.core.security._retry_request(request, 2)
    assert res is None
    assert request.called == 2


def test_reload_community_should_suceed_after_one_call(
        mock_metrics, monkeypatch):
    request = mock.Mock()
    request.called = 0

    def call(self, request, **kwargs):
        request.called = request.called + 1
        if request.called == 1:
            raise Exception('provoked')
        return 'result'

    monkeypatch.setattr(requests.Session, 'send', call)

    res = zeit.web.core.security._retry_request(request, 2)
    assert res == 'result'
    assert request.called == 2


def test_decode_sso_should_work(sso_keypair):
    cookie = jwt.encode({'id': '4711'}, sso_keypair['private'], 'RS256')
    res = zeit.web.core.security.get_user_info_from_sso_cookie(
        cookie, sso_keypair['public'])
    assert res['id'] == '4711'


def test_decode_sso_should_not_work():
    cookie = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJfcGVybWFuZW50Ijp0cnV'
              'lLCJyb2xlcyI6W10sImNyZWF0ZWQiOiIyMDE1LTA5LTExIDE3OjQxOjIxIiw'
              'iaWRlbnRpdHkuaWQiOjMsImlkZW50aXR5LmF1dGhfdHlwZSI6bnVsbCwiZW1'
              'haWwiOiJyb25ob2xkQGZvby5jb20iLCJzdGF0ZSI6ImFjdGl2ZSIsImxhc3Rf'
              'bW9kaWZpZWQiOiIyMDE1LTA5LTExIDE3OjQyOjM4IiwiZXhwIjoxNDQ0NjcyM'
              'DU4LCJwYXNzd29yZCI6ImNkMjMzNzVkNWRjZGU4NGMxYTZmMTJiYzdlZTFjZG'
              'RkNmE5ZjFjMjUiLCJpZCI6IjMiLCJuYW1lIjpudWxsfQ.L1_y5CSo_cQdvfVY'
              '5irxroq0FwGbhDumon2TETqfbCU9pOVqbh0bKX81P3O8uuHVY-hKoxE8TNxYs'
              'TgYE4eV7MsbA3uDpqMzhVnbq5kfQHNWt9LTKjn-q5sit4hiS02TErS75bgWHVZ'
              'tigMoSuCs8V-97DYldTx3bNaHr86Ut-eXrUkc9QSfDp_tH-NJ6NIevHeOW-t7'
              'v3hs_bsAR5fDzH6kjmoFdMlU4WCbuO9x27ofvXAK7Q1nqXUt9wYCB14WdZOQF'
              'dUQiBh0SXeuaEAgorlmK0Ks54RmB2XJKXVJboeSqkFixhdUwFnJ2byvTcx1A'
              'fzuLagrLQZ9OCWU4dyH4A')

    res = zeit.web.core.security.get_user_info_from_sso_cookie(cookie, 'foo')
    assert res is None


def test_cookieless_request_returns_nothing(dummy_request):
    assert not dummy_request.user


def test_cookieless_request_clears_session(dummy_request):
    dummy_request.session['user'] = dict(uid='bar')
    dummy_request.user
    assert 'user' not in dummy_request.session


def test_empty_cache_triggers_backend_fills_cache(
        dummy_request, mockserver_factory, monkeypatch):
    user_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <user>
        <uid>457322</uid>
        <name>test-user</name>
        <roles>
            <role>authenticated user</role>
        </roles>
    </user>
    """

    def sso_cookie_patch(cookie, key):
        return {
            'name': 'my_name',
            'email': 'my_email@example.com',
            'id': 'foo'}

    monkeypatch.setattr(
        zeit.web.core.security, 'get_user_info_from_sso_cookie',
        sso_cookie_patch)

    server = mockserver_factory(user_xml)
    dummy_request.registry.settings['community_host'] = server.url
    dummy_request.cookies['my_sso_cookie'] = 'foo'
    dummy_request.headers['Cookie'] = ''
    assert 'user' not in dummy_request.session
    assert dummy_request.user['ssoid'] == 'foo'
    policy = zeit.web.core.security.AuthenticationPolicy()
    assert policy.authenticated_userid(dummy_request) == 'foo'
    assert dummy_request.session['user']['ssoid'] == 'foo'

    assert dummy_request.session['user']['uid'] == '457322'
    assert dummy_request.session['user']['name'] == 'test-user'


def test_returns_valid_user_info_from_session(dummy_request, monkeypatch):
    dummy_request.cookies['my_sso_cookie'] = 'present'
    monkeypatch.setattr(zeit.web.core.security, 'get_user_info', lambda x: {
        'ssoid': '123',
        'has_community_data': True,
    })
    assert dummy_request.user['ssoid'] == '123'
    del dummy_request.user
    assert dummy_request.user['ssoid'] == '123'


@pytest.mark.xfail(reason='Testing misconfigurations is an unsolved issue.')
def test_unreachable_agatho_should_not_produce_error():
    mocked_request = mock.MagicMock()
    mocked_request.registry.settings['agatho_host'] = (
        'http://thisurlshouldnotexist.moep/')
    assert get_thread('http://xml.zeit.de/artikel/01', mocked_request) is None


def test_unreachable_community_should_not_produce_error(dummy_request):
    dummy_request.registry.settings['community_host'] = (
        'http://thisurlshouldnotexist.moep/')
    dummy_request.cookies['drupal-userid'] = 23
    dummy_request.headers['Cookie'] = ''
    user_info = dict(uid=0, name=None, picture=None, roles=[],
                     mail=None, premoderation=False, should_invalidate=False,
                     has_community_data=False)
    assert get_user_info(dummy_request) == user_info


def test_unreachable_community_counts_as_logged_in_but_marks_session_invalid(
        dummy_request, monkeypatch):
    dummy_request.registry.settings['community_host'] = (
        'http://thisurlshouldnotexist.moep/')
    dummy_request.cookies['my_sso_cookie'] = 'present'
    monkeypatch.setattr(
        zeit.web.core.security, 'get_user_info_from_sso_cookie',
        lambda *args: {'id': '123'})
    assert dummy_request.user['ssoid']
    assert dummy_request.user['should_invalidate']


def test_session_with_uid_0_marks_session_invalid(dummy_request, monkeypatch):
    dummy_request.cookies['my_sso_cookie'] = 'present'
    monkeypatch.setattr(
        zeit.web.core.security, 'get_user_info_from_sso_cookie',
        lambda *args: {'id': '123'})
    dummy_request.session['user'] = {
        'ssoid': '123',
        'uid': 0,
    }
    assert dummy_request.user['ssoid']
    assert dummy_request.user['should_invalidate']


@pytest.mark.xfail(reason='Testing broken dependencies is an unsolved issue.')
def test_malformed_agatho_response_should_not_produce_error(http_testserver):
    mocked_request = mock.MagicMock()
    mocked_request.registry.settings['agatho_host'] = http_testserver.url
    assert get_thread('http://xml.zeit.de/artikel/01', mocked_request) is None


@pytest.mark.xfail(reason='Testing broken dependencies is an unsolved issue.')
def test_malformed_community_response_should_not_produce_error(
        dummy_request, http_testserver):
    dummy_request.registry.settings['community_host'] = http_testserver.url
    dummy_request.cookies['drupal-userid'] = 23
    dummy_request.headers['Cookie'] = ''
    user_info = dict(uid=0, name=None, picture=None, roles=[], mail=None)
    assert get_user_info(dummy_request) == user_info


def test_get_user_info_strips_malformed_picture_value(
        dummy_request, mockserver_factory):
    user_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <user>
        <picture>0</picture>
    </user>
    """
    server = mockserver_factory(user_xml)
    dummy_request.registry.settings['community_host'] = server.url
    user_info = get_user_info(dummy_request)
    assert user_info['picture'] is None


def test_get_user_info_replaces_community_host(
        dummy_request, mockserver_factory):
    user_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <user>
        <picture>{server}/picture.png</picture>
    </user>
    """
    server = mockserver_factory(user_xml)
    dummy_request.registry.settings['community_host'] = server.url
    user_info = get_user_info(dummy_request)
    assert user_info['picture'] == 'http://static_community/foo/picture.png'


def test_rawr_config_should_contain_login_url(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/article/01' % testserver.url)
    assert driver.execute_script('return rawrConfig.loginUrl') is None
    driver.execute_script('rawrConfig.sso()')
    assert 'http://my_sso/anmelden' in driver.execute_script(
        'return rawrConfig.loginUrl')


def test_no_user_rawr_authentication_is_empty(dummy_request):
    stuff = zeit.web.core.security._rawr_authentication(dummy_request)
    rawr_user, rawr_signature, timestamp = stuff
    data = json.loads(rawr_user.decode('base64'))
    assert data == {}


def test_rawr_authentication_encodes_json_as_base64(dummy_request):
    dummy_request.user = {
        'ssoid': '123',
        'email': 'test@example.org',
        'name': 'jrandom',
    }
    stuff = zeit.web.core.security._rawr_authentication(dummy_request)
    rawr_user, rawr_signature, timestamp = stuff
    data = json.loads(rawr_user.decode('base64'))
    assert data == {'email': 'test@example.org', 'nickname': 'jrandom'}
    # I guess testing the signature would mean copying the production code
    # to the test code, which doesn't tell us anything, so we rely on
    # manual integration tests with the actual rawr system for that.
