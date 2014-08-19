# -*- coding: utf-8 -*-
import pkg_resources
import pytest

from lxml import etree
from pyramid.testing import setUp, tearDown, DummyRequest
from repoze.bitblt.processor import ImageTransformationMiddleware
import gocept.httpserverlayer.wsgi
import selenium.webdriver
import webtest

import zeit.frontend.application
import zeit.frontend.comments


settings = {
    'pyramid.reload_templates': 'false',

    'pyramid.debug_authorization': 'false',
    'pyramid.debug_notfound': 'false',
    'pyramid.debug_routematch': 'false',
    'pyramid.debug_templates': 'false',

    'community_host': u'file://%s/' % pkg_resources.resource_filename(
        'zeit.frontend', 'data/comments'),
    'agatho_host': u'file://%s/' % pkg_resources.resource_filename(
        'zeit.frontend', 'data/comments'),
    'linkreach_host': u'file://%s/' % pkg_resources.resource_filename(
        'zeit.frontend', 'data/linkreach/api'),

    'load_template_from_dav_url': 'egg://zeit.frontend/test/newsletter',

    'community_host_timeout_secs': '10',
    'hp': 'zeit-magazin/index',
    'node_comment_statistics': 'data/node-comment-statistics.xml',
    'default_teaser_images': (
        'http://xml.zeit.de/zeit-magazin/default/teaser_image'),
    'connector_type': 'filesystem',

    'vivi_zeit.connector_repository-path': 'egg://zeit.frontend/data',

    'vivi_zeit.cms_keyword-configuration': (
        'egg://zeit.cms.tagging.tests/keywords_config.xml'),
    'vivi_zeit.cms_source-badges': 'egg://zeit.cms.asset/badges.xml',
    'vivi_zeit.cms_source-banners': 'egg://zeit.cms.content/banners.xml',
    'vivi_zeit.cms_source-keyword': (
        'egg://zeit.cms.content/zeit-ontologie-prism.xml'),
    'vivi_zeit.cms_source-navigation': (
        'egg://zeit.cms.content/navigation.xml'),
    'vivi_zeit.cms_source-products': 'egg://zeit.cms.content/products.xml',
    'vivi_zeit.cms_source-serie': 'egg://zeit.cms.content/serie.xml',
    'vivi_zeit.cms_whitelist-url': (
        'egg://zeit.cms.tagging.tests/whitelist.xml'),
    'vivi_zeit.frontend_iqd-mobile-ids': (
        'egg://zeit.frontend/data/config/iqd-mobile-ids.xml'),
    'vivi_zeit.content.article_genre-url': (
        'egg://zeit.frontend/data/config/article-genres.xml'),
    'vivi_zeit.content.article_image-layout-source': (
        'egg://zeit.frontend/data/config/article-image-layouts.xml'),
    'vivi_zeit.content.article_video-layout-source': (
        'egg://zeit.frontend/data/config/article-video-layouts.xml'),
    'vivi_zeit.content.article_htmlblock-layout-source': (
        'egg://zeit.frontend/data/config/article-htmlblock-layouts.xml'),
    'vivi_zeit.magazin_article-template-source': (
        'egg://zeit.frontend/data/config/article-templates.xml'),
    'vivi_zeit.magazin_article-related-layout-source': (
        'egg://zeit.frontend/data/config/article-related-layouts.xml'),
    'vivi_zeit.content.cp_block-layout-source': (
        'egg://zeit.frontend/data/config/cp-layouts.xml'),
    'vivi_zeit.content.cp_bar-layout-source': (
        'egg://zeit.frontend/config/cp-bar-layouts.xml'),
    'vivi_zeit.frontend_banner-source': (
        'egg://zeit.frontend/data/config/banner.xml'),
    'vivi_zeit.content.gallery_gallery-types-url': (
        'egg://zeit.frontend/data/config/gallery-types.xml'),

    'vivi_zeit.newsletter_renderer-host': 'file:///dev/null',

    'debug.show_exceptions': 'True',
    'debug.propagate_jinja_errors': 'True'
}


browsers = {
    'firefox': selenium.webdriver.Firefox
}


@pytest.fixture
def app_settings():
    return settings.copy()


@pytest.fixture(scope='module')
def jinja2_env():
    app = zeit.frontend.application.Application()
    app.settings = settings.copy()
    app.configure_pyramid()
    return app.configure_jinja()


@pytest.fixture(scope='session')
def application():
    app = zeit.frontend.application.Application()({}, **settings)
    return ImageTransformationMiddleware(app, secret='time')


@pytest.fixture(scope='session')
def debug_application():
    app_settings = settings.copy()
    app_settings['debug.show_exceptions'] = ''
    app = zeit.frontend.application.Application()({}, **app_settings)
    return ImageTransformationMiddleware(app, secret='time')


@pytest.fixture
def config(request):
    config = setUp(settings=settings)
    request.addfinalizer(tearDown)
    return config


@pytest.fixture
def dummy_request(request, config):
    config.manager.get()['request'] = req = DummyRequest(is_xhr=False)
    return req


@pytest.fixture
def agatho():
    from zeit.frontend.comments import Agatho
    return Agatho(agatho_url='%s/agatho/thread/' % settings['agatho_host'])


@pytest.fixture
def linkreach():
    from zeit.frontend.reach import LinkReach
    return LinkReach(settings['node_comment_statistics'],
                     settings['linkreach_host'])


@pytest.fixture(scope='session')
def testserver(application, request):
    server = gocept.httpserverlayer.wsgi.Layer()
    server.port = 6543
    server.wsgi_app = application
    server.setUp()
    server.url = 'http://%s' % server['http_address']
    request.addfinalizer(server.tearDown)
    return server


@pytest.fixture(scope='session')
def debug_testserver(debug_application, request):
    server = gocept.httpserverlayer.wsgi.Layer()
    server.port = 6547
    server.wsgi_app = debug_application
    server.setUp()
    server.url = 'http://%s' % server['http_address']
    request.addfinalizer(server.tearDown)
    return server


@pytest.fixture(scope='session', params=[503])
def http_testserver(request):
    from pyramid.config import Configurator
    from pyramid.response import Response

    def hello_world(r):
        resp = Response(status=request.param)
        return resp

    config = Configurator()
    config.add_route('any', '/*url')
    config.add_view(hello_world, route_name='any')
    app = config.make_wsgi_app()

    server = gocept.httpserverlayer.wsgi.Layer()
    server.port = 8889  # XXX Why not use the default (random) port?
    server.wsgi_app = app
    server.setUp()
    request.addfinalizer(server.tearDown)
    return server


@pytest.fixture(scope='session', params=browsers.keys())
def selenium_driver(request):
    if request.param == 'firefox':
        profile = selenium.webdriver.FirefoxProfile()
        profile.set_preference('network.http.use-cache', False)
        browser = browsers[request.param](firefox_profile=profile)
    else:
        browser = browsers[request.param]()

    request.addfinalizer(lambda *args: browser.quit())
    return browser


@pytest.fixture
def asset():
    """Return file-object for given test asset path."""
    return lambda path: open(pkg_resources.resource_filename(
        'zeit.frontend', 'data' + path), 'rb')


@pytest.fixture
def browser(application):
    """Returns an instance of `webtest.TestApp`."""
    class TestApp(webtest.TestApp):
        def get_json(self, url, params=None, headers=None, *args, **kw):
            if headers is None:
                headers = {}
            headers['Accept'] = 'application/json'
            return self.get(url, params, headers, *args, **kw)

    return TestApp(application, extra_environ={'HTTP_HOST': 'example.com'})


@pytest.fixture
def monkeyagatho(monkeypatch):
    def collection_get(self, unique_id):
        path = zeit.frontend.comments.path_of_article(unique_id)
        response = etree.parse(''.join([self.entry_point, path]))
        return zeit.frontend.comments._place_answers_under_parent(response)

    monkeypatch.setattr(
        zeit.frontend.comments.Agatho, 'collection_get', collection_get)
