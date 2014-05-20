from mock import patch, MagicMock
from pytest import fixture
from zeit.frontend.comments import get_thread
from zeit.frontend.security import CommunityAuthenticationPolicy, ZMO_USER_KEY
from zeit.frontend.security import get_community_user_info


@fixture
def policy():
	return CommunityAuthenticationPolicy()


def test_cookieless_request_returns_nothing(policy, dummy_request):
	assert policy.authenticated_userid(dummy_request) is None


def test_cookieless_request_clears_session(policy, dummy_request):
	dummy_request.session[ZMO_USER_KEY] = dict(uid='bar')
	policy.authenticated_userid(dummy_request)
	assert ZMO_USER_KEY not in dummy_request.session


def test_session_cache_has_precedence(policy, dummy_request):
	dummy_request.cookies['drupal-userid'] = 23
	dummy_request.session[ZMO_USER_KEY] = dict(uid=23, name='s3crit')
	assert policy.authenticated_userid(dummy_request) == 23
	assert dummy_request.session[ZMO_USER_KEY]['name'] == 's3crit'


def test_session_cache_cleared_when_id_changes(policy, dummy_request):
	dummy_request.cookies['drupal-userid'] = 23
	# session still contains old user id and sensitive information
	dummy_request.session[ZMO_USER_KEY] = dict(uid=42, name='s3crit')
	with patch('zeit.frontend.security.Request.get_response') as mocked_getter:
		mocked_response = MagicMock()
		mocked_response.body = '''<user><uid>457322</uid><name>test-friedbert</name><mail>test-friedbert@example.com</mail><picture/><roles><role>authenticated user</role></roles><profile/></user>		
		'''
		mocked_getter.return_value = mocked_response
		dummy_request.cookies['drupal-userid'] = 23
		dummy_request.headers['Cookie'] = ''
		assert policy.authenticated_userid(dummy_request) == '457322'
		assert dummy_request.session[ZMO_USER_KEY]['name'] == 'test-friedbert'


def test_empty_cache_triggers_backend_fills_cache(policy, dummy_request):
	with patch('zeit.frontend.security.Request.get_response') as mocked_getter:
		mocked_response = MagicMock()
		mocked_response.body = '''<user><uid>457322</uid><name>test-friedbert</name><mail>test-friedbert@example.com</mail><picture/><roles><role>authenticated user</role></roles><profile/></user>		
		'''
		mocked_getter.return_value = mocked_response
		dummy_request.cookies['drupal-userid'] = 23
		dummy_request.headers['Cookie'] = ''
		assert ZMO_USER_KEY not in dummy_request.session
		assert policy.authenticated_userid(dummy_request) == '457322'
		assert dummy_request.session[ZMO_USER_KEY]['name'] == 'test-friedbert'
