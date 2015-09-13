import mock
import requests

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


def test_article_should_have_breadcrumbs(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    breadcrumbs = browser.cssselect('.footer-breadcrumbs__list')
    assert len(breadcrumbs) == 1


def test_article_should_have_correct_breadcrumb_structure(
        testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    breadcrumbs_items = browser.cssselect('.footer-breadcrumbs__item')
    assert len(breadcrumbs_items) == 3
    breadcrumbs_links = browser.cssselect('.footer-breadcrumbs__link')
    assert len(breadcrumbs_links) == 2


def test_keyword_index_pages_should_fall_back_to_xslt(testserver, testbrowser):
    resp = requests.get(
        '%s/schlagworte/index/A/index' % testserver.url,
        allow_redirects=False)
    assert resp.status_code == 200
    assert resp.headers['x-render-with'] == 'default'


def test_keyword_pages_should_send_redirect(testserver, testbrowser):
    resp = requests.get(
        '%s/schlagworte/orte/Xy/index' % testserver.url,
        allow_redirects=False)
    assert resp.status_code == 301
    assert resp.headers['Location'] == '%s/thema/xy' % testserver.url


def test_commentstart_param_should_trigger_redirect(testserver):
    resp = requests.get(
        '%s/zeit-online/article/zeit?commentstart=2' % testserver.url,
        allow_redirects=False)
    assert resp.status_code == 301
    assert (resp.headers['location'] == (
            '%s/zeit-online/article/zeit' % testserver.url))
