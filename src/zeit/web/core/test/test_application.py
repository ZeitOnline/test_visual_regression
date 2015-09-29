# -*- coding: utf-8 -*-
import base64
import pkg_resources

import mock
import plone.testing.zca
import pyramid.interfaces
import pyramid.request
import pyramid.testing
import pytest
import requests

import zeit.content.cp.interfaces
import zeit.cms.interfaces
import zeit.web.core.application
import zeit.web.core.interfaces


@pytest.fixture
def app_request(application, app_settings, request):
    plone.testing.zca.pushGlobalRegistry()
    request.addfinalizer(plone.testing.zca.popGlobalRegistry)
    app = zeit.web.core.application.Application()
    app.settings = app_settings.copy()
    app.settings['asset_prefix'] = '/assets'
    config = app.configure_pyramid()
    config.commit()
    request = pyramid.testing.DummyRequest()
    request.registry = config.registry
    request._set_extensions(config.registry.getUtility(
        pyramid.interfaces.IRequestExtensions))
    return app, request


def test_asset_url_includes_configured_prefix(app_request):
    _, request = app_request
    assert ('http://example.com/assets/css/main.css' in
            request.asset_url('css/main.css'))

    assert ('http://example.com/assets/' in
            request.asset_url('/'))


def test_application_settings_contain_version_hash(app_request):
    app, _ = app_request
    version_hash = app.settings.get('version_hash', '').upper()
    actual_version = pkg_resources.get_distribution('zeit.web').version
    assert actual_version == base64.b16decode(version_hash)


def test_asset_url_appends_version_hash_where_needed(app_request):
    app, request = app_request
    version_hash = app.settings['version_hash']
    assert ('http://example.com/assets/css/main.css?' + version_hash ==
            request.asset_url('css/main.css'))
    assert ('http://example.com/assets/js/app.js?' + version_hash ==
            request.asset_url('js/app.js'))
    assert ('http://example.com/assets/img/favicon.ico' ==
            request.asset_url('img/favicon.ico'))


def test_asset_url_allows_specifying_full_host(app_request):
    app, request = app_request
    app.config.registry.settings['asset_prefix'] = 'http://assets.example.com'
    assert ('http://assets.example.com/css/main.css' in
            request.asset_url('css/main.css'))


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


def test_vgwort_pixel_should_be_present(testserver, testbrowser):
    select = testbrowser('{}/artikel/01'.format(testserver.url)).cssselect
    assert len(select('body img#vgwort_pixel')) == 1

    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect
    assert len(select('body img#vgwort_pixel')) == 1

    select = testbrowser('{}/zeit-online/index'.format(
        testserver.url)).cssselect
    assert len(select('body img#vgwort_pixel')) == 0


def test_content_should_have_marker_interface(application):
    content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    assert zeit.web.core.interfaces.IInternalUse.providedBy(content)


def test_transaction_aborts_after_request(testserver, testbrowser):
    with mock.patch('transaction.TransactionManager.commit') as commit:
        testbrowser('{}/artikel/01'.format(testserver.url))
        assert not commit.called


def test_assets_have_configurable_cache_control_header(
        testbrowser, application):
    b = testbrowser('/css/web.site/screen.css')
    assert b.headers['Cache-control'] == 'max-age=1'
