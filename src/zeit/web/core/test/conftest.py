# -*- coding: utf-8 -*-
import json
import os.path
import pkg_resources
import urllib

import cssselect
import gocept.httpserverlayer.wsgi
import lxml.etree
import lxml.html
import plone.testing.zca
import plone.testing.zodb
import pyramid.testing
import pytest
import repoze.bitblt.processor
import selenium.webdriver
import transaction
import webtest
import zope.browserpage.metaconfigure
import zope.event
import zope.interface
import zope.processlifetime
import zope.testbrowser.browser

import zeit.content.image.interfaces
import zeit.cms.interfaces

import zeit.web.core
import zeit.web.core.comments
import zeit.web.core.application


settings = {
    'pyramid.reload_templates': 'false',

    'pyramid.debug_authorization': 'false',
    'pyramid.debug_notfound': 'false',
    'pyramid.debug_routematch': 'false',
    'pyramid.debug_templates': 'false',

    'scripts_url': '/js/static',
    'caching_time_content': '5',
    'caching_time_article': '10',
    'caching_time_centerpage': '20',
    'caching_time_gallery': '40',
    'caching_time_image': '30',
    'caching_time_videostill': '35',
    'caching_time_external': '15',
    'community_host': 'http://localhost:6551/',
    'agatho_host': u'file://%s' % pkg_resources.resource_filename(
        'zeit.web.core', 'data/comments'),
    'linkreach_host': u'file://%s/' % pkg_resources.resource_filename(
        'zeit.web.core', 'data/linkreach/api'),
    'google_tag_manager_host': 'foo.baz',

    'load_template_from_dav_url': 'egg://zeit.web.core/test/newsletter',

    'community_host_timeout_secs': '10',
    'spektrum_hp_feed': 'http://localhost:6552/static/feed.xml',
    'spektrum_img_host': 'http://localhost:6552',
    'node_comment_statistics': 'community/node-comment-statistics.xml',
    'default_teaser_images': (
        'http://xml.zeit.de/zeit-magazin/default/teaser_image'),
    'connector_type': 'mock',

    'breaking_news': (
        'http://xml.zeit.de/eilmeldung/homepage-banner'),

    'vivi_zeit.connector_repository-path': 'egg://zeit.web.core/data',

    'vivi_zeit.cms_keyword-configuration': (
        'egg://zeit.cms.tagging.tests/keywords_config.xml'),
    'vivi_zeit.cms_source-badges': 'egg://zeit.cms.asset/badges.xml',
    'vivi_zeit.cms_source-banners': 'egg://zeit.cms.content/banners.xml',
    'vivi_zeit.cms_source-keyword': (
        'egg://zeit.cms.content/zeit-ontologie-prism.xml'),
    'vivi_zeit.cms_source-navigation': (
        'egg://zeit.cms.content/navigation.xml'),
    'vivi_zeit.cms_source-products': (
        'egg://zeit.web.core/data/config/products.xml'),
    'vivi_zeit.cms_source-serie': (
        'egg://zeit.web.core/data/config/series.xml'),
    'vivi_zeit.cms_whitelist-url': (
        'egg://zeit.cms.tagging.tests/whitelist.xml'),
    'vivi_zeit.web_iqd-mobile-ids': (
        'egg://zeit.web.core/data/config/iqd-mobile-ids.xml'),
    'vivi_zeit.web_image-scales': (
        'egg://zeit.web.core/data/config/scales.xml'),
    'vivi_zeit.content.article_genre-url': (
        'egg://zeit.web.core/data/config/article-genres.xml'),
    'vivi_zeit.content.article_image-layout-source': (
        'egg://zeit.web.core/data/config/article-image-layouts.xml'),
    'vivi_zeit.content.article_video-layout-source': (
        'egg://zeit.web.core/data/config/article-video-layouts.xml'),
    'vivi_zeit.content.article_htmlblock-layout-source': (
        'egg://zeit.web.core/data/config/article-htmlblock-layouts.xml'),
    'vivi_zeit.magazin_article-template-source': (
        'egg://zeit.web.core/data/config/article-templates.xml'),
    'vivi_zeit.magazin_article-related-layout-source': (
        'egg://zeit.web.core/data/config/article-related-layouts.xml'),
    'vivi_zeit.content.cp_block-layout-source': (
        'egg://zeit.web.core/data/config/cp-layouts.xml'),
    'vivi_zeit.content.cp_bar-layout-source': (
        'egg://zeit.web.core/data/config/cp-bar-layouts.xml'),
    'vivi_zeit.web_banner-source': (
        'egg://zeit.web.core/data/config/banner.xml'),
    'vivi_zeit.web_navigation': (
        'egg://zeit.web.core/data/config/navigation.xml'),
    'vivi_zeit.web_navigation-services': (
        'egg://zeit.web.core/data/config/navigation-services.xml'),
    'vivi_zeit.web_navigation-classifieds': (
        'egg://zeit.web.core/data/config/navigation-classifieds.xml'),
    'vivi_zeit.web_navigation-footer-publisher': (
        'egg://zeit.web.core/data/config/navigation-footer-publisher.xml'),
    'vivi_zeit.web_navigation-footer-links': (
        'egg://zeit.web.core/data/config/navigation-footer-links.xml'),
    'vivi_zeit.content.gallery_gallery-types-url': (
        'egg://zeit.web.core/data/config/gallery-types.xml'),
    'vivi_zeit.web_series-source': (
        'egg://zeit.web.core/data/config/series.xml'),
    'vivi_zeit.imp_scale-source': 'egg://zeit.web.core/data/config/scales.xml',
    'vivi_zeit.content.link_source-blogs': (
        'egg://zeit.web.core/data/config/blogs_meta.xml'),

    'vivi_zeit.newsletter_renderer-host': 'file:///dev/null',

    'vivi_zeit.solr_solr-url': 'http://mock.solr',
    'vivi_zeit.content.cp_cp-types-url': (
        'egg://zeit.web.core/data/config/cp-types.xml'),

    'debug.show_exceptions': True,
    'debug.propagate_jinja_errors': True,
    'debug.enable_profiler': False
}


browsers = {
    'firefox': selenium.webdriver.Firefox
}


def test_asset_path(*parts):
    """Return full file-system path for given test asset path."""
    return os.path.abspath(
        os.path.join(os.path.dirname(zeit.web.core.__file__), 'data', *parts)
    )


def test_asset(path):
    """Return file-object for given test asset path."""
    return open(pkg_resources.resource_filename(
        'zeit.web.core', 'data' + path), 'rb')


@pytest.fixture
def app_settings():
    return settings.copy()


@pytest.fixture(scope='module')
def jinja2_env():
    app = zeit.web.core.application.Application()
    app.settings = settings.copy()
    app.configure_pyramid()
    return app.configure_jinja()


class ZODBLayer(plone.testing.zodb.EmptyZODB):
    """Layer which sets up ZODB to be useable for Zope 3.
    We need one to use a workingcopy.
    """

    def setUp(self):
        super(ZODBLayer, self).setUp()
        from zope.app.debug import Debugger
        self['zope_application'] = Debugger(self['zodbDB'])
        # Cause install generation to run.
        zope.event.notify(zope.processlifetime.DatabaseOpenedWithRoot(
            self['zodbDB']))
        transaction.commit()

    def tearDown(self):
        del self['zope_application']
        super(ZODBLayer, self).tearDown()

    def getRootFolder(self):
        # The name never ever changes, so there's no real need to import it
        # from zope.app.publication.
        return self['zodbRoot']['Application']

ZODB_LAYER = ZODBLayer()


@pytest.fixture
def zodb(application_session, request):
    ZODB_LAYER.testSetUp()
    request.addfinalizer(ZODB_LAYER.testTearDown)
    return ZODB_LAYER.getRootFolder()


@pytest.fixture(scope='session')
def application_session(request):
    plone.testing.zca.pushGlobalRegistry()
    zope.browserpage.metaconfigure.clear()
    request.addfinalizer(plone.testing.zca.popGlobalRegistry)
    factory = zeit.web.core.application.Application()
    app = factory({}, **settings)
    # ZODB needs to come after ZCML is set up by the Application.
    # Putting it in here is simpler than adding yet another fixture.
    ZODB_LAYER.setUp()
    request.addfinalizer(ZODB_LAYER.tearDown)
    wsgi = repoze.bitblt.processor.ImageTransformationMiddleware(
        app, secret='time')
    wsgi.zeit_app = factory
    return wsgi


@pytest.fixture
def application(application_session, zodb, request):
    # This application_session/application split is a bit clumsy, but some
    # things (e.g. reset connector, teardown zodb) needs to be called after
    # each test (i.e. in 'function' scope). The many diverse fixtures make this
    # a bit complicated... it's integrated in the most common ones now (e.g.
    # ``application``, ``testbrowser``), but if it's needed elsewhere, it has
    # to be integrated explicitly.
    request.addfinalizer(reset_connector)
    return application_session


def reset_connector():
    connector = zope.component.getUtility(
        zeit.connector.interfaces.IConnector)
    connector._reset()


@pytest.fixture
def workingcopy(application, zodb, request):
    site = zeit.cms.testing.site(zodb)
    site.__enter__()
    interaction = zeit.cms.testing.interaction()
    interaction.__enter__()
    request.addfinalizer(lambda: interaction.__exit__(None, None, None))
    request.addfinalizer(lambda: site.__exit__(None, None, None))


# XXX Toggling the exception view in an existing application would be much more
# convenient than having to create an entirely new one just for that purpose,
# but I can't find a way to temporarily de-register a pyramid view.
@pytest.fixture
def debug_application(request):
    plone.testing.zca.pushGlobalRegistry()
    zope.browserpage.metaconfigure.clear()
    request.addfinalizer(plone.testing.zca.popGlobalRegistry)
    app_settings = settings.copy()
    app_settings['debug.show_exceptions'] = ''
    return repoze.bitblt.processor.ImageTransformationMiddleware(
        zeit.web.core.application.Application()({}, **app_settings),
        secret='time'
    )


@pytest.fixture
def config(application, request):
    config = pyramid.testing.setUp(settings=settings, hook_zca=False)
    request.addfinalizer(lambda: pyramid.testing.tearDown(unhook_zca=False))
    return config


@pytest.fixture
def dummy_request(request, config):
    req = pyramid.testing.DummyRequest(is_xhr=False)
    config.manager.get()['request'] = req
    return req


@pytest.fixture
def agatho():
    return zeit.web.core.comments.Agatho(
        settings['agatho_host'] + '/agatho/thread/')


@pytest.fixture
def debug_testserver(debug_application, request):
    server = gocept.httpserverlayer.wsgi.Layer()
    server.port = 6547
    server.wsgi_app = debug_application
    server.setUp()
    server.url = 'http://%s' % server['http_address']
    request.addfinalizer(server.tearDown)
    return server


@pytest.fixture(scope='function')
def mockcommunity_factory(request):
    def factory(response=None):
        def mock_app(env, start_response):
            start_response('200 OK', [])
            return [response]
        server = gocept.httpserverlayer.wsgi.Layer()
        server.port = 6551
        server.wsgi_app = mock_app
        server.setUp()
        server.url = 'http://%s' % server['http_address']
        request.addfinalizer(server.tearDown)
        return server
    return factory


@pytest.fixture(scope='session')
def mockspektrum(request):

    from pyramid.config import Configurator
    config = Configurator()
    config.add_static_view('static', 'zeit.web.core:data/spektrum/')
    app = config.make_wsgi_app()
    server = gocept.httpserverlayer.wsgi.Layer()
    server.port = 6552
    server.wsgi_app = app
    server.setUp()
    server.url = 'http://%s' % server['http_address']
    request.addfinalizer(server.tearDown)
    return server


@pytest.fixture(scope='session')
def testserver(application_session, request, mockspektrum):
    server = gocept.httpserverlayer.wsgi.Layer()
    server.port = 6543
    server.wsgi_app = application_session
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
def appbrowser(application):
    """Returns an instance of `webtest.TestApp`."""
    extra_environ = dict(HTTP_HOST='example.com')
    return TestApp(application, extra_environ=extra_environ)


@pytest.fixture
def monkeyagatho(monkeypatch):
    def collection_get(self, unique_id):
        path = unique_id.replace(zeit.cms.interfaces.ID_NAMESPACE, '/')
        try:
            return lxml.etree.parse(self.agatho_host + path)
        except IOError:
            return

    monkeypatch.setattr(
        zeit.web.core.comments.Agatho, 'collection_get', collection_get)


@pytest.fixture
def image_group_factory():
    class MockImageGroup(dict):
        zope.interface.implements(zeit.content.image.interfaces.IImageGroup)
        masterimage = None

    class MockRepositoryImage(object):

        def __init__(self, size, name):
            self._size = size
            self.uniqueId = name
            self.masterimage = None

        def getImageSize(self):  # NOQA
            return self._size

    def factory(*args, **kwargs):
        image_group = MockImageGroup()
        arg_dict = zip([('img-%s' % i) for i in range(len(args))], args)
        for name, size in arg_dict + kwargs.items():
            image_group[name] = MockRepositoryImage(size, name)
        return image_group

    return factory


@pytest.fixture
def my_traverser(application):
    root = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    return zeit.web.core.application.RepositoryTraverser(root)


@pytest.fixture
def testbrowser(application):
    # We require ``application`` here so that stuff is properly isolated
    # between tests; see comment there for details.
    return Browser


@pytest.fixture
def css_selector(request):
    def wrapped(selector, document):
        xpath = cssselect.HTMLTranslator().css_to_xpath(selector)
        if not isinstance(document, lxml.html.HtmlElement):
            document = lxml.html.fromstring(document)
        return document.xpath(xpath)
    return wrapped


@pytest.fixture
def comment_counter(testserver, testbrowser):
    def get_count(**kw):
        params = urllib.urlencode(kw)
        url = '%s/json/comment_count?%s' % (testserver.url, params)
        return testbrowser(url)
    return get_count


@pytest.fixture(autouse=True)
def ephemeral_settings(request):
    # Store genuine settings
    settings_orig = pyramid.config.settings.Settings(d=settings)
    interface = zeit.web.core.interfaces.ISettings

    def update_settings(custom_settings):
        settings = pyramid.config.settings.Settings(d=custom_settings)
        zope.interface.declarations.alsoProvides(settings, interface)
        zope.component.provideUtility(settings, interface)

    def restore_settings():
        zope.interface.declarations.alsoProvides(settings_orig, interface)
        zope.component.provideUtility(settings_orig, interface)
    request.addfinalizer(restore_settings)
    return update_settings


class TestApp(webtest.TestApp):

    def get_json(self, url, params=None, headers=None, *args, **kw):
        if headers is None:
            headers = {}
        headers['Accept'] = 'application/json'
        return self.get(url, params, headers, *args, **kw)


class Browser(zope.testbrowser.browser.Browser):
    """Custom testbrowser class that allows direct access to CSS selection on
    its content.

    Usage examples:

    # Create test browser
    browser = Browser('/foo/bar')
    # Test only one h1 exists
    assert len(browser.cssselect('h1.only-once')) == 1
    # Test all divs contain at least one span
    divs = browser.cssselect('div')
    assert all(map(lambda d: d.cssselect('span'), divs))
    # Test the third paragraph has two links with class batz
    paragraph = browser.cssselect('p')[2]
    assert len(paragraph.cssselect('a.batz')) == 2

    """

    _translator = None

    def __init__(self, *args, **kwargs):
        """Call base constructor and cache a translator instance."""
        super(Browser, self).__init__(*args, **kwargs)
        self._translator = cssselect.HTMLTranslator()

    def cssselect(self, selector):
        """Return a list of lxml.HTMLElement instances that match a given CSS
        selector."""
        xpath = self._translator.css_to_xpath(selector)
        if self.document is not None:
            return self.document.xpath(xpath)

    @property
    def document(self):
        """Return an lxml.html.HtmlElement instance of the response body."""
        if self.contents is not None:
            return lxml.html.document_fromstring(self.contents)

    @property
    def json(self):
        """Return a dictionary of the parsed json body if available."""
        if self.contents is not None:
            return json.loads(self.contents)
