# -*- coding: utf-8 -*-
from mock import patch
from pytest import fixture, yield_fixture, mark
from zeit.web.core.appinfo import get_app_info, assemble_app_info


@fixture
def app_info_request(dummy_request):
    dummy_request.app_info = assemble_app_info(dummy_request)
    return dummy_request


@yield_fixture
def app_info(request, dummy_request):
    """Mocks a the userinfo that the appinfo method gets with
    data from the marked mocked user."""

    username = request.keywords['user'].args[0]
    with patch('pyramid.security.authenticated_userid') as mocked_user_info:
        from zeit.web.core.data import MOCK_USER_DATA
        userinfo = MOCK_USER_DATA.get(username)
        dummy_request.cookies['drupal-userid'] = userinfo['uid']
        dummy_request.session['zmo-user'] = userinfo
        mocked_user_info.return_value = userinfo['uid']
        yield username


def test_cookieless_request_returns_default(app_info_request):
    assert get_app_info(app_info_request)['authenticated'] is False


@mark.user('test-user')
def test_app_info_contains_user(app_info, app_info_request):
    assert assemble_app_info(
        app_info_request)['user']['name'] == 'test-user'
