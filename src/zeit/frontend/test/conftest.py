from os import path
from os.path import abspath, dirname, join, sep
from pyramid.testing import setUp, tearDown, DummyRequest
from repoze.bitblt.processor import ImageTransformationMiddleware
from selenium import webdriver
from webtest import TestApp as TestAppBase
from zeit import frontend
import gocept.httpserverlayer.wsgi
import pytest
import zeit.frontend.application


def test_asset_path(*parts):
    """ Return full file-system path for given test asset path. """
    from zeit import frontend
    return abspath(join(dirname(frontend.__file__), 'data', *parts))


def test_asset(path):
    """ Return file-object for given test asset path. """
    return open(test_asset_path(*path.split(sep)), 'rb')


settings = {
    'pyramid.reload_templates': 'false',
    'pyramid.debug_authorization': 'true',
    'pyramid.debug_notfound': 'true',
    'pyramid.debug_routematch': 'true',
    'pyramid.debug_templates': 'true',

    'agatho_url': u'file://%s/' % path.join(
        path.dirname(path.abspath(frontend.__file__)), 'data', 'comments'),

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

    'vivi_zeit.newsletter_renderer-host': 'file:///dev/null',
}


browsers = {
    'firefox': webdriver.Firefox
    #'phantomjs': webdriver.PhantomJS,
}


@pytest.fixture(scope="module")
def jinja2_env():
    app = zeit.frontend.application.Application()
    app.configure_pyramid()
    return app.configure_jinja()


@pytest.fixture
def app_settings():
    return settings.copy()


@pytest.fixture(scope='session')
def application():
    app = zeit.frontend.application.Application()({}, **settings)
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
    return Agatho(agatho_url=settings['agatho_url'])


@pytest.fixture(scope='session')
def testserver(application, request):
    server = gocept.httpserverlayer.wsgi.Layer()
    server.port = 6543  # XXX Why not use the default (random) port?
    server.wsgi_app = application
    server.setUp()
    # Convenience / compatibility with pytest-localserver which was used here
    # previously.
    server.url = 'http://%s' % server['http_address']
    request.addfinalizer(server.tearDown)
    return server


@pytest.fixture(scope='session', params=browsers.keys())
def selenium_driver(request):
    if request.param == 'firefox':
        profile = webdriver.FirefoxProfile()
        profile.set_preference('network.http.use-cache', False)
        b = browsers[request.param](firefox_profile=profile)
    else:
        b = browsers[request.param]()

    request.addfinalizer(lambda *args: b.quit())
    return b


@pytest.fixture
def asset():
    return test_asset


@pytest.fixture
def browser(application):
    """ Returns an instance of `webtest.TestApp`. """
    extra_environ = dict(HTTP_HOST='example.com')
    return TestApp(application, extra_environ=extra_environ)

class TestApp(TestAppBase):

    def get_json(self, url, params=None, headers=None, *args, **kw):
        if headers is None:
            headers = {}
        headers['Accept'] = 'application/json'
        return self.get(url, params, headers, *args, **kw)
