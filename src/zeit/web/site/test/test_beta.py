import mock

import pytest

import zeit.web.site.view_beta


def test_anon_user_should_see_login_prompt_on_beta_page(
        mockcommunity_factory, testserver, testbrowser):
    user_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <user>
        <uid>0</uid>
        <roles>
            <role>anonymous user</role>
        </roles>
    </user>
    """
    mockcommunity_factory(user_xml)
    browser = testbrowser('{}/beta'.format(testserver.url))
    assert len(browser.cssselect('a.beta-teaser__button')) == 2


def test_community_user_should_see_email_prompt_on_beta_page(
        mockcommunity_factory, testserver, testbrowser):
    user_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <user>
        <uid>223754</uid>
        <roles>
            <role>authenticated user</role>
        </roles>
    </user>
    """
    mockcommunity_factory(user_xml)
    browser = testbrowser('{}/beta'.format(testserver.url))
    assert len(browser.cssselect('a.beta-teaser__button')) == 1


def test_beta_user_should_see_toggle_form_on_beta_page(
        mockcommunity_factory, testserver, testbrowser):
    user_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <user>
        <uid>223754</uid>
        <roles>
            <role>authenticated user</role>
            <role>beta</role>
        </roles>
    </user>
    """
    mockcommunity_factory(user_xml)
    browser = testbrowser('{}/beta'.format(testserver.url))
    assert len(browser.cssselect('input.beta-teaser__button')) == 1


def test_beta_view_should_identify_community_user(
        app_settings, mockcommunity_factory):
    user_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <user>
        <uid>457322</uid>
        <roles>
            <role>authenticated user</role>
        </roles>
    </user>
    """
    mockcommunity_factory(user_xml)
    request = mock.MagicMock()
    request.registry.settings = app_settings
    view = zeit.web.site.view_beta.Beta(None, request)
    assert view.community_user.get('uid') == '457322'


def test_beta_view_should_lookup_beta_role_correctly(
        app_settings, mockcommunity_factory):
    user_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <user>
        <uid>457322</uid>
        <roles>
            <role>authenticated user</role>
            <role>beta</role>
        </roles>
    </user>
    """
    mockcommunity_factory(user_xml)
    request = mock.MagicMock()
    request.registry.settings = app_settings
    view = zeit.web.site.view_beta.Beta(None, request)
    assert view.beta_user is True


@pytest.mark.parametrize('version', [
    'opt_in',
    'opt_out'
])
def test_beta_view_should_pass_through_site_version_from_session(version):
    request = mock.MagicMock()
    request.cookies = {'site-version': 'beta-{}'.format(version)}

    def set_cookie(key, value=''):
        request.cookies[key] = value

    request.response.set_cookie = set_cookie
    request.POST = {}
    view = zeit.web.site.view_beta.Beta(None, request)
    assert view.site_version == version


@pytest.mark.parametrize('opt,version', [
    ('in', 'opt_in'),
    ('in', 'opt_out'),
    ('out', 'foo'),
    ('out', '')
])
def test_beta_view_should_write_updated_site_version_to_session(opt, version):
    request = mock.MagicMock()
    request.cookies = {'site-version': 'beta-{}'.format(version)}

    def set_cookie(key, value=''):
        request.cookie[key] = value

    request.response.set_cookie = set_cookie
    request.POST = {'opt': opt}
    view = zeit.web.site.view_beta.Beta(None, request)
    assert view.site_version == 'opt_{}'.format(opt)


def test_beta_view_should_provide_correct_friedbert_host():
    request = mock.MagicMock()
    request.route_url = lambda *args: 'foo'
    view = zeit.web.site.view_beta.Beta(None, request)
    assert view.friedbert_host == 'foo'


def test_beta_view_should_provide_correct_teaser_image():
    request = mock.MagicMock()
    request.route_url = lambda *args: 'mock://'
    view = zeit.web.site.view_beta.Beta(None, request)
    assert view.beta_teaser_img == 'mock://administratives/beta-teaser.jpg'
