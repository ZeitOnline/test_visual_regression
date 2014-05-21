from mock import patch
from pytest import fixture, yield_fixture, mark
from zeit.frontend.security import ZMO_USER_KEY
from zeit.frontend.appinfo import get_app_info, assemble_app_info


@fixture
def app_info_request(dummy_request):
    dummy_request.app_info = assemble_app_info(dummy_request)
    return dummy_request


@yield_fixture
def app_info(request, dummy_request):
    """
    mocks a the userinfo that the appinfo method gets with
    data from the marked mocked user
    """
    username = request.keywords['user'].args[0]
    with patch(
            'zeit.frontend.appinfo.authenticated_userid') as mocked_user_info:
        from zeit.frontend.data import MOCK_USER_DATA
        userinfo = MOCK_USER_DATA.get(username)
        dummy_request.cookies['drupal-userid'] = userinfo['uid']
        dummy_request.session[ZMO_USER_KEY] = userinfo
        mocked_user_info.return_value = userinfo['uid']
        yield username


def test_cookieless_request_returns_default(app_info_request):
    assert get_app_info(app_info_request)['authenticated'] is False


@mark.user('test-friedbert')
def test_app_info_contains_user(app_info, app_info_request):
    assert assemble_app_info(
        app_info_request)['user']['name'] == 'test-friedbert'
