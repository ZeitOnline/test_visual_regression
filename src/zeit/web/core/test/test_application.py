# -*- coding: utf-8 -*-
import mock
import plone.testing.zca
import pyramid.interfaces
import pyramid.testing
import pytest
import requests
import zope.component

import zeit.cms.interfaces

import zeit.web.core.application
import zeit.web.core.interfaces


@pytest.fixture
def app_request(application, app_settings, request):
    plone.testing.zca.pushGlobalRegistry()
    request.addfinalizer(plone.testing.zca.popGlobalRegistry)
    app = zeit.web.core.application.Application()
    app.settings.update(app_settings)
    config = app.configure_pyramid()
    config.commit()
    request = pyramid.testing.DummyRequest()
    request.registry = config.registry
    request._set_extensions(config.registry.getUtility(
        pyramid.interfaces.IRequestExtensions))
    return app, request


def test_asset_host_includes_configured_prefix(app_request):
    app, request = app_request
    app.config.registry.settings['asset_prefix'] = '/assets'
    assert request.asset_host == 'http://example.com/assets'


def test_asset_host_allows_specifying_full_host(app_request):
    app, request = app_request
    app.config.registry.settings['asset_prefix'] = 'http://assets.example.com/'
    assert request.asset_host == 'http://assets.example.com'


def test_asset_host_supports_url_prefix(app_request):
    app, request = app_request
    app.config.registry.settings['asset_prefix'] = '/assets'
    request.application_url = 'http://example.com/foo'
    assert request.asset_host == 'http://example.com/foo/assets'


def test_acceptable_pagination_should_not_redirect(testserver):
    resp = requests.get('%s/artikel/03/seite-3' % testserver.url,
                        allow_redirects=False)
    assert resp.url == '%s/artikel/03/seite-3' % testserver.url
    assert resp.status_code == 200


def test_malformed_view_spec_should_produce_404_page(testserver):
    resp = requests.get('%s/artikel/03/moep' % testserver.url,
                        allow_redirects=False)
    assert resp.url == '%s/artikel/03/moep' % testserver.url
    assert resp.status_code == 404


def test_page_zero_should_redirect_to_article_base(testserver):
    resp = requests.get('%s/artikel/03/seite-0' % testserver.url,
                        allow_redirects=False)
    assert resp.headers['location'] == '%s/artikel/03' % testserver.url
    assert resp.status_code == 301


def test_out_of_scope_pagination_should_produce_404_page(testserver):
    resp = requests.get('%s/artikel/03/seite-8' % testserver.url,
                        allow_redirects=False)
    assert resp.url == '%s/artikel/03/seite-8' % testserver.url
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
    resp = requests.get('%s/artikel/03/seite-abc' % testserver.url,
                        allow_redirects=False)
    assert resp.headers['location'] == '%s/artikel/03' % testserver.url
    assert resp.status_code == 301


def test_missing_pagination_spec_should_redirect_to_article_base(testserver):
    resp = requests.get('%s/artikel/03/seite-' % testserver.url,
                        allow_redirects=False)
    assert resp.headers['location'] == '%s/artikel/03' % testserver.url
    assert resp.status_code == 301


def test_salvageable_pagination_should_redirect_to_article_page(testserver):
    resp = requests.get('%s/artikel/03/seite-7.html' % testserver.url,
                        allow_redirects=False)
    assert resp.headers['location'] == '%s/artikel/03/seite-7' % testserver.url
    assert resp.status_code == 301


def test_vgwort_pixel_should_be_present(testbrowser):
    browser = testbrowser('/artikel/01')
    pixel = browser.cssselect('body img[src^="http://example.com"]')
    assert len(pixel) == 1
    assert pixel[0].get('src').startswith('http://example.com/vgwort/')
    # check for http://example.com/vgwort/1d19d1df864c492188198be0291ff993
    # doesn't work because bitblt is processing all image sources in tests

    browser = testbrowser('/zeit-online/article/01')
    pixel = browser.cssselect('body img[src^="http://example.com"]')
    assert len(pixel) == 1
    assert pixel[0].get('src').startswith('http://example.com/vgwort/')
    # check for http://example.com/vgwort/1d19d1df864c492188198be0291ff993
    # doesn't work because bitblt is processing all image sources in tests

    browser = testbrowser('/zeit-online/index')
    pixel = browser.cssselect('body img[src^="http://example.com"]')
    assert len(pixel) == 0


def test_content_should_have_marker_interface(application):
    content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    assert zeit.web.core.interfaces.IInternalUse.providedBy(content)


def test_dynamic_content_should_have_marker_interface(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/dynamic/angela-merkel')
    assert zeit.web.core.interfaces.IInternalUse.providedBy(content)


def test_transaction_aborts_after_request(testbrowser):
    with mock.patch('transaction.TransactionManager.commit') as commit:
        testbrowser('/artikel/01')
        assert not commit.called


def test_assets_have_configurable_cache_control_header(testbrowser):
    b = testbrowser('/static/latest/css/web.site/screen.css')
    assert b.headers['Cache-control'] == 'max-age=1'


def test_feature_toggle_source_should_be_parsed(application):
    assert zeit.web.core.application.FEATURE_TOGGLES.find('article_lineage')
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
