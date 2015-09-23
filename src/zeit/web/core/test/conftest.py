# -*- coding: utf-8 -*-
import copy
import json
import os.path
import pkg_resources

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
import zeit.web.core.application
import zeit.web.core.comments
import zeit.web.core.traversal
import zeit.web.core.utils
import zeit.web.core.view


settings = {
    'pyramid.reload_templates': 'false',
    'pyramid.debug_authorization': 'false',
    'pyramid.debug_notfound': 'false',
    'pyramid.debug_routematch': 'false',
    'pyramid.debug_templates': 'false',
    'cache.type': 'memory',
    'cache.lock_file': '/tmp/test_lock',
    'cache.regions': 'default_term, second, short_term, long_term',
    'cache.second.expire': '1',
    'cache.short_term.expire': '60',
    'cache.default_term.expire': '300',
    'cache.long_term.expire': '3600',
    'scripts_url': '/js/static',
    'liveblog_backend_url': 'http://localhost:6552/liveblog/backend',
    'liveblog_status_url': 'http://localhost:6552/liveblog/status',
    # XXX I'd rather put None here and change the settings for a specific test,
    # but then I'd need to re-create an Application since assets_max_age
    # is only evaluated once during configuration.
    'assets_max_age': '1',
    'caching_time_content': '5',
    'caching_time_article': '10',
    'caching_time_centerpage': '20',
    'caching_time_gallery': '40',
    'caching_time_image': '30',
    'caching_time_videostill': '35',
    'caching_time_external': '15',
    'community_host': 'http://localhost:6551',
    'community_static_host': 'http://static_community/foo',
    'agatho_host': 'http://localhost:6552/comments',
    'linkreach_host': 'egg://zeit.web.core/data/linkreach/api',
    'google_tag_manager_host': 'foo.baz',
    'app_servers': '',
    'load_template_from_dav_url': 'egg://zeit.web.core/test/newsletter',
    'community_host_timeout_secs': '10',
    'spektrum_hp_feed': 'http://localhost:6552/spektrum/feed.xml',
    'spektrum_img_host': 'http://localhost:6552/spektrum',
    'node_comment_statistics': 'community/node-comment-statistics.xml',
    'default_teaser_images': (
        'http://xml.zeit.de/zeit-magazin/default/teaser_image'),
    'connector_type': 'mock',
    'vgwort_url': 'http://example.com/vgwort',
    'breaking_news_config': (
        'http://xml.zeit.de/eilmeldung/homepage-banner'),
    'breaking_news_timeout': 2 * 60 * 60,
    'enable_third_party_modules': '',
    'vivi_zeit.connector_repository-path': 'egg://zeit.web.core/data',
    'vivi_zeit.cms_keyword-configuration': (
        'egg://zeit.cms.tagging.tests/keywords_config.xml'),
    'vivi_zeit.cms_source-badges': 'egg://zeit.cms.asset/badges.xml',
    'vivi_zeit.cms_source-banners': 'egg://zeit.cms.content/banners.xml',
    'vivi_zeit.cms_source-keyword': (
        'egg://zeit.cms.content/zeit-ontologie-prism.xml'),
    'vivi_zeit.cms_source-navigation': (
        'egg://zeit.cms.content/navigation.xml'),
    'vivi_zeit.cms_source-channels': (
        'egg://zeit.cms.content/navigation.xml'),
    'vivi_zeit.cms_source-products': (
        'egg://zeit.web.core/data/config/products.xml'),
    'vivi_zeit.cms_source-serie': (
        'egg://zeit.web.core/data/config/series.xml'),
    'vivi_zeit.cms_task-queue-async': 'not-applicable',
    'vivi_zeit.cms_whitelist-url': (
        'egg://zeit.web.core/data/config/whitelist.xml'),
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
    'vivi_zeit.content.article_template-source': (
        'egg://zeit.web.core/data/config/article-templates.xml'),
    'vivi_zeit.magazin_article-related-layout-source': (
        'egg://zeit.web.core/data/config/article-related-layouts.xml'),
    'vivi_zeit.content.cp_block-layout-source': (
        'egg://zeit.web.core/data/config/cp-layouts.xml'),
    'vivi_zeit.content.cp_bar-layout-source': (
        'egg://zeit.web.core/data/config/cp-bar-layouts.xml'),
    'vivi_zeit.content.cp_area-config-source': (
        'egg://zeit.web.core/data/config/cp-areas.xml'),
    'vivi_zeit.content.cp_region-config-source': (
        'egg://zeit.web.core/data/config/cp-regions.xml'),
    'vivi_zeit.content.cp_cp-types-url': (
        'egg://zeit.web.core/data/config/cp-types.xml'),
    'vivi_zeit.content.cp_cp-feed-max-items': '30',
    'vivi_zeit.content.image_variant-source': (
        'egg://zeit.web.core/data/config/image-variants.xml'),
    'vivi_zeit.content.image_legacy-variant-source': (
        'egg://zeit.web.core/data/config/image-variants-legacy.xml'),
    'vivi_zeit.web_banner-source': (
        'egg://zeit.web.core/data/config/banner.xml'),
    'vivi_zeit.web_banner-id-mappings': (
        'egg://zeit.web.core/data/config/banner-id-mappings.xml'),
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
    'vivi_zeit.web_servicebox-source': (
        'egg://zeit.web.core/data/config/servicebox.xml'),
    'vivi_zeit.content.gallery_gallery-types-url': (
        'egg://zeit.web.core/data/config/gallery-types.xml'),
    'vivi_zeit.web_series-source': (
        'egg://zeit.web.core/data/config/series.xml'),
    'vivi_zeit.web_whitelist-meta-source': (
        'egg://zeit.web.core/data/config/whitelist_meta.xml'),
    'vivi_zeit.web_blacklist-url': (
        'egg://zeit.web.core/data/config/blacklist.xml'),
    'vivi_zeit.imp_scale-source': 'egg://zeit.web.core/data/config/scales.xml',
    'vivi_zeit.content.link_source-blogs': (
        'egg://zeit.web.core/data/config/blogs_meta.xml'),
    'vivi_zeit.brightcove_read-url': 'http://localhost:6552/video/bc.json',
    'vivi_zeit.brightcove_write-url': 'http://localhost:6552/video/bc.json',
    'vivi_zeit.brightcove_read-token': 'foo',
    'vivi_zeit.brightcove_write-token': 'bar',
    'vivi_zeit.brightcove_index-principal': 'zope.brightcove',
    'vivi_zeit.brightcove_timeout': '300',
    'vivi_zeit.brightcove_video-folder': 'video',
    'vivi_zeit.brightcove_playlist-folder': 'video/playlist',
    'vivi_zeit.content.video_source-serie': (
        'egg://zeit.web.core/data/config/video-serie.xml'),
    'vivi_zeit.newsletter_renderer-host': 'file:///dev/null',

    'vivi_zeit.solr_solr-url': 'http://mock.solr',
    'vivi_zeit.content.cp_cp-types-url': (
        'egg://zeit.web.core/data/config/cp-types.xml'),
    'sso_activate': '',
    'sso_url': 'http://my_sso',
    'sso_cookie': 'http://my_sso_cookie',
    'debug.show_exceptions': True,
    'debug.propagate_jinja_errors': True,
    'debug.enable_profiler': False,
    'dev_environment': True
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
    return zeit.web.core.utils.defaultattrdict(
        lambda *_: None, settings.iteritems())


@pytest.fixture
def jinja2_env(application):
    return application.zeit_app.jinja_env


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

    def getRootFolder(self):  # NOQA
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

    def restore_settings():
        settings = zope.component.getUtility(
            zeit.web.core.interfaces.ISettings)
        settings.__init__(settings_orig)
    request.addfinalizer(restore_settings)
    settings_orig = copy.copy(zope.component.getUtility(
        zeit.web.core.interfaces.ISettings))

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
    app_settings['debug.propagate_jinja_errors'] = ''
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
def dummy_request(request, config, app_settings):
    req = pyramid.testing.DummyRequest(is_xhr=False)
    req.response.headers = set()
    req.registry.settings = app_settings
    req.matched_route = None
    config.manager.get()['request'] = req
    return req


@pytest.fixture(scope='function')
def mockserver_factory(request):
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


class ISettings(pyramid.interfaces.ISettings):
    """Custom interface class to register settings as a utility"""


def sleep_tween(handler, registry):
    """Tween to control whether server should sleep for a little while"""
    def timeout(request):
        # Setting timeout globally can cause race conditions, if tests run
        # parallel.
        # XXX. Set sleep time per request
        conf = zope.component.getUtility(ISettings)
        import time
        time.sleep(conf['sleep'])
        print 'For request %s, mockserver slept %s seconds.' % (request.path,
                                                                conf['sleep'])
        response = handler(request)

        # For comfortability set sleep back to 0
        conf['sleep'] = 0
        return response
    return timeout


@pytest.fixture(scope='session')
def mockserver(request):
    """Used for mocking external HTTP dependencies like agatho or spektrum."""
    from pyramid.config import Configurator

    config = Configurator()
    config.add_static_view('/', 'zeit.web.core:data/')
    settings = {'sleep': 0}
    settings = pyramid.config.settings.Settings(d=settings)
    interface = ISettings
    zope.interface.declarations.alsoProvides(settings, interface)
    zope.component.provideUtility(settings, interface)
    config.add_tween('zeit.web.core.test.conftest.sleep_tween')
    app = config.make_wsgi_app()
    server = gocept.httpserverlayer.wsgi.Layer()
    server.port = 6552
    server.wsgi_app = app
    server.setUp()
    server.settings = settings
    server.url = 'http://%s' % server['http_address']
    request.addfinalizer(server.tearDown)
    return server


@pytest.fixture(scope='session')
def testserver(application_session, request, mockserver):
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
def image_group_factory():
    class MockImageGroup(dict):
        zope.interface.implements(zeit.content.image.interfaces.IImageGroup)
        master_image = None

    class MockRepositoryImage(object):

        def __init__(self, size, name):
            self._size = size
            self.uniqueId = name
            self.master_image = None

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
    return zeit.web.core.traversal.RepositoryTraverser(root)


@pytest.fixture
def testbrowser(application, testserver):
    # We require ``application`` here so that stuff is properly isolated
    # between tests; see comment there for details.
    Browser._testserver = testserver.url
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
def comment_counter(app_settings, application):
    def get_count(**kwargs):
        request = pyramid.testing.DummyRequest()
        request.registry.settings = app_settings
        request.GET = kwargs
        return zeit.web.core.view.json_comment_count(request)
    return get_count


class TestApp(webtest.TestApp):

    def get_json(self, url, params=None, headers=None, *args, **kw):
        if headers is None:
            headers = {}
        headers['Accept'] = 'application/json'
        return self.get(url, params, headers, *args, **kw)


class Browser(zope.testbrowser.browser.Browser):
    """Custom testbrowser class that allows direct access to CSS and XPath
    selection on its content.

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
    _testserver = None

    def __init__(self, url=None, mech_browser=None):
        """Call base constructor and cache a translator instance."""
        super(Browser, self).__init__(url, mech_browser)
        self._translator = cssselect.HTMLTranslator()

    def cssselect(self, selector):
        """Return a list of lxml.HTMLElement instances that match a given CSS
        selector.
        """
        xpath = self._translator.css_to_xpath(selector)
        if self.document is not None:
            return self.document.xpath(xpath)

    def open(self, url, data=None):
        if url and self._testserver and not url.startswith(self._testserver):
            url = '{}/{}'.format(self._testserver, url.lstrip('/'))
        return super(Browser, self).open(url, data)

    def xpath(self, selector):
        """Return a list of lxml.HTMLElement instances that match a given
        XPath selector.
        """
        if self.document is not None:
            return self.document.xpath(selector)

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
