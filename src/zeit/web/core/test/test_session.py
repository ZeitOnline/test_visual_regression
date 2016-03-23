import jwt
import mock
import zope.component

from zeit.web.core.session import SESSION_CACHE
import zeit.web.core.interfaces
import zeit.web.core.session


def test_stores_session_data_in_cache(testbrowser, sso_keypair):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['sso_key'] = sso_keypair['public']
    sso_cookie = jwt.encode(
        {'id': 'ssoid'}, sso_keypair['private'], 'RS256')
    testbrowser.cookies.forURL(
        'http://localhost')['my_sso_cookie'] = sso_cookie
    testbrowser.open('/login-state')
    data = SESSION_CACHE.get(sso_cookie)
    assert 'user' in data
    assert data['user']['ssoid'] == 'ssoid'


def test_no_sso_cookie_does_not_store_anything(testbrowser):
    testbrowser('/login-state')
    assert not SESSION_CACHE.backend._cache


def test_reading_session_data_does_not_mark_dirty(dummy_request):
    session = zeit.web.core.session.CacheSession(dummy_request)
    session.get('foo')
    assert not session._dirty


def test_writing_session_data_marks_dirty(dummy_request):
    session = zeit.web.core.session.CacheSession(dummy_request)
    session['foo'] = 'bar'
    assert session._dirty


def test_loads_data_from_cache(dummy_request):
    dummy_request.cookies['my_sso_cookie'] = 'ssoid'
    session = zeit.web.core.session.CacheSession(dummy_request)
    session['foo'] = 'bar'
    session.persist()
    session = zeit.web.core.session.CacheSession(dummy_request)
    assert session['foo'] == 'bar'


def test_stores_only_dict_contents_not_attributes(dummy_request):
    # Attributes like `request` are not pickleable, so don't even try to store
    # them.
    dummy_request.cookies['my_sso_cookie'] = 'ssoid'
    session = zeit.web.core.session.CacheSession(dummy_request)
    session['foo'] = 'bar'
    session.persist()
    data = SESSION_CACHE.get('ssoid')
    assert not hasattr(data, 'request')


# We are lucky that both dogpile.cache and pyramid.session use `time.time()`
# for expiration/reissue, otherwise clock freezing would be a lot of hassle.
# Note that they use greater-than (not equal) for comparison, so we need to
# step `start_time + expiration_time (or reissue_time) + 1` to trigger things.

def test_data_is_removed_after_expiration(dummy_request):
    dummy_request.cookies['my_sso_cookie'] = 'ssoid'
    with mock.patch('time.time') as time:
        time.return_value = 1
        session = zeit.web.core.session.CacheSession(dummy_request)
        session['foo'] = 'bar'
        session.persist()
    with mock.patch('time.time') as time:
        time.return_value = 4
        session = zeit.web.core.session.CacheSession(dummy_request)
        assert 'foo' not in session


def test_reading_does_not_postpone_expiration(dummy_request):
    dummy_request.cookies['my_sso_cookie'] = 'ssoid'
    with mock.patch('time.time') as time:
        time.return_value = 1
        session = zeit.web.core.session.CacheSession(dummy_request)
        session['foo'] = 'bar'
        session.persist()
    with mock.patch('time.time') as time:
        time.return_value = 2
        session = zeit.web.core.session.CacheSession(dummy_request)
        session['foo']
        session.persist()
    with mock.patch('time.time') as time:
        time.return_value = 4
        session = zeit.web.core.session.CacheSession(dummy_request)
        assert 'foo' not in session


def test_writing_postpones_expiration(dummy_request):
    dummy_request.cookies['my_sso_cookie'] = 'ssoid'
    with mock.patch('time.time') as time:
        time.return_value = 1
        session = zeit.web.core.session.CacheSession(dummy_request)
        session['foo'] = 'bar'
        session.persist()
    with mock.patch('time.time') as time:
        time.return_value = 2
        session = zeit.web.core.session.CacheSession(dummy_request)
        session['foo'] = 'baz'
        session.persist()
    with mock.patch('time.time') as time:
        time.return_value = 4
        session = zeit.web.core.session.CacheSession(dummy_request)
        assert session['foo'] == 'baz'
    with mock.patch('time.time') as time:
        time.return_value = 5
        session = zeit.web.core.session.CacheSession(dummy_request)
        assert 'foo' not in session


def test_reading_postpones_expiration_after_reissue_interval(dummy_request):
    dummy_request.cookies['my_sso_cookie'] = 'ssoid'
    with mock.patch('time.time') as time:
        time.return_value = 1
        session = zeit.web.core.session.CacheSession(dummy_request)
        session['foo'] = 'bar'
        session.persist()
    with mock.patch('time.time') as time:
        time.return_value = 3
        session = zeit.web.core.session.CacheSession(dummy_request)
        session['foo']
        session.persist()
    with mock.patch('time.time') as time:
        time.return_value = 4
        session = zeit.web.core.session.CacheSession(dummy_request)
        assert session['foo'] == 'bar'
    with mock.patch('time.time') as time:
        time.return_value = 6
        session = zeit.web.core.session.CacheSession(dummy_request)
        assert 'foo' not in session
