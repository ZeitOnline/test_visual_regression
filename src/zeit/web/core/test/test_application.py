# -*- coding: utf-8 -*-
import base64
import pkg_resources

import pyramid.interfaces
import pyramid.request
import pyramid.testing
import pyramid.traversal
import pytest
import requests

from zeit.content.cp.interfaces import ICenterPage
from zeit.content.dynamicfolder.interfaces import IRepositoryDynamicFolder
import zeit.web.core.application


@pytest.fixture
def app_request(app_settings, application):
    app_settings['asset_prefix'] = '/assets'
    app = zeit.web.core.application.Application()
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


def test_feature_longform_should_be_discovered_during_traversal(my_traverser):
    req = pyramid.request.Request.blank('/feature/feature_longform')
    tdict = my_traverser(req)
    assert zeit.web.core.article.IFeatureLongform.providedBy(tdict['context'])


def test_parallel_cps_should_be_discovered_during_traversal(my_traverser):
    req = pyramid.request.Request.blank('/parallel_cps/index')
    tdict = my_traverser(req)
    assert tdict['context'].uniqueId == (
        'http://xml.zeit.de/parallel_cps/index.cp2015')
    assert ICenterPage.providedBy(tdict['context'])


def test_parallel_folders_should_be_discovered_during_traversal(my_traverser):
    req = pyramid.request.Request.blank('/parallel_cps/serie/index')
    tdict = my_traverser(req)
    assert tdict['context'].uniqueId == (
        'http://xml.zeit.de/parallel_cps/serie.cp2015/')
    assert IRepositoryDynamicFolder.providedBy(tdict['context'])


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
