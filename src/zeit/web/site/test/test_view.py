import mock

import zeit.web.site.view


def test_login_state_view_should_deliver_correct_destination():
    request = mock.Mock()
    request.registry.settings = {}
    request.session = {}
    request.registry.settings['community_host'] = "http://community"
    request.registry.settings['community_static_host'] = "community_static"
    request.host = "destination"
    request.params = {}
    result = zeit.web.site.view.login_state(request)
    assert result == {
        'login': 'http://community/user/login?destination=http://destination',
        'logout': 'http://community/user/logout?destination=http://destination'
    }
    request.params = {'context-uri': 'http://context-uri'}
    result = zeit.web.site.view.login_state(request)
    assert result == {
        'login': 'http://community/user/login?destination=http://context-uri',
        'logout': 'http://community/user/logout?destination=http://context-uri'
    }


def test_login_state_view_should_deliver_correct_user():
    request = mock.Mock()
    request.registry.settings = {}
    request.authenticated_userid = 123
    request.session = {}
    request.session['user'] = {}
    request.registry.settings['community_host'] = "http://community"
    request.registry.settings['community_static_host'] = (
        "http://community_static")
    request.host = "destination"
    request.params = {}
    result = zeit.web.site.view.login_state(request)
    assert result['user'] == {
        'profile': 'http://community/user/123'
    }

    request.session['user']['picture'] = 'http://community/pic'
    result = zeit.web.site.view.login_state(request)
    assert result['user']['picture'] == 'http://community_static/pic'

    # community bug
    request.session['user']['picture'] = '0'
    result = zeit.web.site.view.login_state(request)
    assert 'picture' not in result['user']
