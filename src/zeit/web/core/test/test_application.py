# -*- coding: utf-8 -*-
import mock
import requests
import zope.component

import zeit.web.core.application
import zeit.web.core.interfaces


def test_asset_host_includes_configured_prefix(dummy_request):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['asset_prefix'] = '/assets'
    assert dummy_request.asset_host == 'http://example.com/assets'


def test_asset_host_allows_specifying_full_host(dummy_request):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['asset_prefix'] = 'http://assets.example.com/'
    assert dummy_request.asset_host == 'http://assets.example.com'


def test_asset_host_supports_url_prefix(dummy_request):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['asset_prefix'] = '/assets'
    dummy_request.application_url = 'http://example.com/foo'
    assert dummy_request.asset_host == 'http://example.com/foo/assets'


def test_acceptable_pagination_should_not_redirect(testserver):
    resp = requests.get('%s/zeit-magazin/article/03/seite-3' % testserver.url,
                        allow_redirects=False)
    assert resp.url == '%s/zeit-magazin/article/03/seite-3' % testserver.url
    assert resp.status_code == 200


def test_malformed_view_spec_should_produce_404_page(testserver):
    resp = requests.get('%s/zeit-magazin/article/03/moep' % testserver.url,
                        allow_redirects=False)
    assert resp.url == '%s/zeit-magazin/article/03/moep' % testserver.url
    assert resp.status_code == 404


def test_page_zero_should_redirect_to_article_base(testserver):
    resp = requests.get('%s/zeit-magazin/article/03/seite-0' % testserver.url,
                        allow_redirects=False)
    assert (resp.headers['location'] ==
            '%s/zeit-magazin/article/03' % testserver.url)
    assert resp.status_code == 301


def test_out_of_scope_pagination_should_produce_404_page(testserver):
    resp = requests.get('%s/zeit-magazin/article/03/seite-8' % testserver.url,
                        allow_redirects=False)
    assert resp.url == '%s/zeit-magazin/article/03/seite-8' % testserver.url
    assert resp.status_code == 404


def test_article_should_redirect_page_one(testserver):
    resp = requests.get('%s/zeit-online/article/01/seite-1' % testserver.url,
                        allow_redirects=False)
    assert (resp.headers['location'] ==
            '%s/zeit-online/article/01' % testserver.url)
    assert resp.status_code == 301


def test_single_page_article_should_error_on_all_pages_view(testserver):
    resp = requests.get('%s/zeit-online/article/01/komplettansicht' %
                        testserver.url, allow_redirects=False)
    assert resp.status_code == 404


def test_malformed_paginaton_should_redirect_to_article_base(testserver):
    resp = requests.get('%s/zeit-magazin/article/03/seite-abc'
                        % testserver.url,
                        allow_redirects=False)
    assert (resp.headers['location'] ==
            '%s/zeit-magazin/article/03' % testserver.url)
    assert resp.status_code == 301


def test_missing_pagination_spec_should_redirect_to_article_base(testserver):
    resp = requests.get('%s/zeit-magazin/article/03/seite-' % testserver.url,
                        allow_redirects=False)
    assert (resp.headers['location'] == '%s/zeit-magazin'
                                        '/article/03' % testserver.url)
    assert resp.status_code == 301


def test_salvageable_pagination_should_redirect_to_article_page(testserver):
    resp = requests.get('%s/zeit-magazin/article/03/seite-7.html'
                        % testserver.url,
                        allow_redirects=False)
    assert (resp.headers['location'] == '%s/zeit-magazin/'
                                        'article/03/seite-7' % testserver.url)
    assert resp.status_code == 301


def test_vgwort_pixel_should_be_present(testbrowser, togglepatch):
    togglepatch({'third_party_modules': True})
    browser = testbrowser('/zeit-magazin/article/01')
    pixel = browser.cssselect('body img[src^="http://example.com"]')
    assert len(pixel) == 1
    assert pixel[0].get('src') == (
        'http://example.com/vgwort/1d19d1df864c492188198be0291ff993')

    browser = testbrowser('/zeit-online/article/01')
    pixel = browser.cssselect('body img[src^="http://example.com"]')
    assert len(pixel) == 1
    assert pixel[0].get('src') == (
        'http://example.com/vgwort/980d578641cd444aa69700ed11b21d63')

    browser = testbrowser('/zeit-online/index')
    pixel = browser.cssselect('body img[src^="http://example.com"]')
    assert len(pixel) == 0


def test_transaction_aborts_after_request(testbrowser):
    with mock.patch('transaction.TransactionManager.commit') as commit:
        testbrowser('/zeit-magazin/article/01')
        assert not commit.called


def test_assets_have_configurable_cache_control_header(testbrowser):
    b = testbrowser('/static/latest/css/web.site/screen.css')
    assert b.headers['Cache-control'] == 'max-age=1'


def test_feature_toggle_source_should_be_parsed(application):
    assert zeit.web.core.application.FEATURE_TOGGLES.find('dtag_navigation')
    assert not zeit.web.core.application.FEATURE_TOGGLES.find('dummy')
    assert not zeit.web.core.application.FEATURE_TOGGLES.find('nonexistent')


def test_settings_merge_web_ini_and_xml_config(application):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    # from web.ini
    assert conf['pyramid.reload_templates'] is False
    # from xml
    assert conf['author_articles_page_size'] == 10


def test_runtime_settings_are_type_converted(application):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    assert isinstance(conf['author_articles_page_size'], int)
    assert isinstance(conf['default_teaser_images'], basestring)
    assert isinstance(conf['default_packshot_diezeit'], basestring)
    assert isinstance(conf['reach_timeout'], float)


def test_deployment_settings_have_precedence_over_runtime(application):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['author_articles_page_size'] = 1
    assert conf['author_articles_page_size'] == 1
    del conf['author_articles_page_size']
    assert conf['author_articles_page_size'] == 10


def test_pyramid_settings_and_settings_utility_are_the_same(application):
    pyramid_settings = application.zeit_app.config.registry.settings
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    assert conf is pyramid_settings


def test_scheme_for_home_route_urls_depends_on_https_feature_toggle(
        dummy_request,
        togglepatch):
    togglepatch({'https': True})
    # This has to be set for our dummy request
    dummy_request.environ['SERVER_NAME'] = "foo"
    assert dummy_request.route_url('home').startswith('https:')
    togglepatch({'https': False})
    assert not dummy_request.route_url('home').startswith('https:')
