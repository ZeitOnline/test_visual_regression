# -*- coding: utf-8 -*-
import base64
import pkg_resources

import pyramid.interfaces
import pyramid.testing
import pytest

from zeit.frontend.test import Browser
import zeit.frontend.application


@pytest.fixture
def app_request(app_settings):
    app_settings['asset_prefix'] = '/assets'
    app = zeit.frontend.application.Application()
    app.settings = app_settings
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
    actual_version = pkg_resources.get_distribution('zeit.frontend').version
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


def test_out_of_scope_pagination_should_redirect_to_article_base(testserver):
    browser = Browser('%s/artikel/03/seite-0' % testserver.url)
    assert browser.url == '%s/artikel/03' % testserver.url

    browser = Browser('%s/artikel/03/seite-8' % testserver.url)
    assert browser.url == '%s/artikel/03' % testserver.url


def test_non_numeric_paginaton_should_redirect_to_article_base(testserver):
    browser = Browser('%s/artikel/03/seite-abc' % testserver.url)
    assert browser.url == '%s/artikel/03' % testserver.url


def test_missing_pagination_spec_should_redirect_to_article_base(testserver):
    browser = Browser('%s/artikel/03/seite-' % testserver.url)
    assert browser.url == '%s/artikel/03' % testserver.url
