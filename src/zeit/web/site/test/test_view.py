import mock

import zeit.web.site.view


def test_login_state_view_should_deliver_correct_destination():
    request = mock.Mock()
    request.registry.settings = {}
    request.session = {}
    request.registry.settings['sso_activate'] = False
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

    request.session = {}
    request.registry.settings['sso_activate'] = True
    request.registry.settings['community_host'] = "http://community"
    request.registry.settings['sso_url'] = "http://sso"
    request.registry.settings['community_static_host'] = "community_static"
    request.host = "destination_sso"
    request.params = {}
    result = zeit.web.site.view.login_state(request)
    assert result == {
        'login': 'http://sso/anmelden?url=http://destination_sso',
        'logout': 'http://sso/abmelden?url=http://destination_sso'
    }


def test_login_state_view_should_deliver_correct_user():
    request = mock.Mock()
    request.registry.settings = {}
    request.authenticated_userid = 123
    request.session = {}
    request.session['user'] = {}
    request.registry.settings['sso_activate'] = False
    request.registry.settings['community_host'] = "http://community"
    request.params = {}
    result = zeit.web.site.view.login_state(request)
    assert result['user'] == {}
    assert result['profile'] == 'http://community/user'
