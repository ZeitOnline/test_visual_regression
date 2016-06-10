# -*- coding: utf-8 -*-
from StringIO import StringIO
import copy
import json
import logging
import os.path
import pkg_resources
import threading

from cryptography.hazmat.primitives import serialization as cryptoserialization
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
import cryptography.hazmat.backends
import cssselect
import gocept.httpserverlayer.wsgi
import lxml.html
import mock
import plone.testing.zca
import plone.testing.zodb
import pyramid.response
import pyramid.static
import pyramid.testing
import pyramid_dogpile_cache2
import pysolr
import pytest
import repoze.bitblt.processor
import requests
import selenium.webdriver
import selenium.webdriver.firefox.firefox_binary
import transaction
import waitress
import webob.multidict
import webtest
import wesgi
import zope.browserpage.metaconfigure
import zope.event
import zope.interface
import zope.processlifetime
import zope.testbrowser.wsgi

import zeit.content.image.interfaces
import zeit.solr.interfaces

import zeit.web.core
import zeit.web.core.application
import zeit.web.core.routing
import zeit.web.core.utils
import zeit.web.core.view


log = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def app_settings(mockserver):
    return {
        'pyramid.reload_templates': False,
        'pyramid.debug_authorization': False,
        'pyramid.debug_notfound': False,
        'pyramid.debug_routematch': False,
        'pyramid.debug_templates': False,
        'dogpile_cache.backend': 'dogpile.cache.memory',
        'dogpile_cache.regions': (
            'default_term, short_term, long_term, session, config'),
        'dogpile_cache.short_term.expiration_time': '60',
        'dogpile_cache.default_term.expiration_time': '300',
        'dogpile_cache.long_term.expiration_time': '3600',
        'dogpile_cache.session.expiration_time': '2',
        'dogpile_cache.config.expiration_time': '600',
        # XXX This is somewhat duplicate, but in tests we have parts of the
        # vivi config setup too, so we need to satisfy it.
        'vivi_zeit.cms_cache-expiration-config': '600',
        'session.reissue_time': '1',
        'liveblog_backend_url': mockserver.url + '/liveblog/backend',
        'liveblog_status_url': mockserver.url + '/liveblog/status',
        # XXX I'd rather put None here and change the settings for a specific
        # test, but then I'd need to re-create an Application since
        # assets_max_age is only evaluated once during configuration.
        'assets_max_age': '1',
        'comment_page_size': '4',
        'community_host': mockserver.url + '/comments',
        'community_static_host': 'http://static_community/foo',
        'community_maintenance': (
            'http://xml.zeit.de/config/community_maintenance.xml'),
        'agatho_host': mockserver.url + '/comments',
        'linkreach_host': mockserver.url + '/linkreach/api',
        'app_servers': '',
        'health_check_with_fs': True,
        'load_template_from_dav_url': 'egg://zeit.web.core/test/newsletter',
        'spektrum_hp_feed': mockserver.url + '/spektrum/feed.xml',
        'spektrum_img_host': mockserver.url + '/spektrum',
        'zett_hp_feed': mockserver.url + '/zett/feed.xml',
        'zett_img_host': mockserver.url + '/zett',
        'academics_hp_feed': mockserver.url + '/academics/feed.xml',
        'academics_img_host': mockserver.url + '/academics',
        'cardstack_backend': mockserver.url + '/cardstack',
        'connector_type': 'mock',
        'vgwort_url': 'http://example.com/vgwort',
        'breaking_news_config': (
            'http://xml.zeit.de/eilmeldung/homepage-banner'),
        'breaking_news_fallback_image': (
            'http://xml.zeit.de/administratives/eilmeldung-share-image'),
        'vivi_zeit.connector_repository-path': 'egg://zeit.web.core/data',
        'vivi_zeit.cms_keyword-configuration': (
            'egg://zeit.cms.tagging.tests/keywords_config.xml'),
        'vivi_zeit.cms_source-badges': 'egg://zeit.cms.asset/badges.xml',
        'vivi_zeit.cms_source-banners': 'egg://zeit.cms.content/banners.xml',
        'vivi_zeit.cms_source-keyword': (
            'egg://zeit.cms.content/zeit-ontologie-prism.xml'),
        'vivi_zeit.cms_source-navigation': (
            'egg://zeit.web.core/data/config/ressorts.xml'),
        'vivi_zeit.cms_source-channels': (
            'egg://zeit.web.core/data/config/ressorts.xml'),
        'vivi_zeit.cms_source-products': (
            'egg://zeit.web.core/data/config/products.xml'),
        'vivi_zeit.cms_source-serie': (
            'egg://zeit.web.core/data/config/series.xml'),
        'vivi_zeit.cms_task-queue-async': 'not-applicable',
        'vivi_zeit.cms_whitelist-url': (
            'egg://zeit.web.core/data/config/whitelist.xml'),
        'vivi_zeit.web_iqd-mobile-ids-source': (
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
        'vivi_zeit.campus_article-stoa-source': (
            'egg://zeit.web.core/data/config/article-stoa.xml'),
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
        'vivi_zeit.web_banner-id-mappings-source': (
            'egg://zeit.web.core/data/config/banner-id-mappings.xml'),
        'vivi_zeit.web_navigation-source': (
            'egg://zeit.web.core/data/config/navigation.xml'),
        'vivi_zeit.web_navigation-services-source': (
            'egg://zeit.web.core/data/config/navigation-services.xml'),
        'vivi_zeit.web_navigation-classifieds-source': (
            'egg://zeit.web.core/data/config/navigation-classifieds.xml'),
        'vivi_zeit.web_navigation-footer-publisher-source': (
            'egg://zeit.web.core/data/config/navigation-footer-publisher.xml'),
        'vivi_zeit.web_navigation-footer-links-source': (
            'egg://zeit.web.core/data/config/navigation-footer-links.xml'),
        'vivi_zeit.web_servicebox-source': (
            'egg://zeit.web.core/data/config/servicebox.xml'),
        'vivi_zeit.web_zco-servicelinks-source': (
            'egg://zeit.web.core/data/config/servicelinks-zco.xml'),
        'vivi_zeit.web_zco-toolbox-source': (
            'egg://zeit.web.core/data/config/zco-toolbox.xml'),
        'vivi_zeit.content.gallery_gallery-types-url': (
            'egg://zeit.web.core/data/config/gallery-types.xml'),
        'vivi_zeit.web_series-source': (
            'egg://zeit.web.core/data/config/series.xml'),
        'vivi_zeit.web_feature-toggle-source': (
            'egg://zeit.web.core/data/config/feature-toggle.xml'),
        'vivi_zeit.web_blacklist-url': (
            'egg://zeit.web.core/data/config/blacklist.xml'),
        'vivi_zeit.imp_scale-source':
            'egg://zeit.web.core/data/config/scales.xml',
        'vivi_zeit.content.link_source-blogs': (
            'egg://zeit.web.core/data/config/blogs_meta.xml'),
        'vivi_zeit.push_facebook-accounts': (
            'egg://zeit.push.tests/fixtures/facebook-accounts.xml'),
        'vivi_zeit.push_facebook-main-account': 'fb-test',
        'vivi_zeit.push_facebook-magazin-account': 'fb-magazin',
        'vivi_zeit.push_facebook-campus-account': 'fb-campus',
        'vivi_zeit.brightcove_read-url': mockserver.url + '/video/bc.json',
        'vivi_zeit.brightcove_write-url': mockserver.url + '/video/bc.json',
        'vivi_zeit.brightcove_read-token': 'foo',
        'vivi_zeit.brightcove_write-token': 'bar',
        'vivi_zeit.brightcove_index-principal': 'zope.brightcove',
        'vivi_zeit.brightcove_timeout': '300',
        'vivi_zeit.brightcove_video-folder': 'video',
        'vivi_zeit.brightcove_playlist-folder': 'video/playlist',
        'vivi_zeit.content.video_source-serie': (
            'egg://zeit.web.core/data/config/video-serie.xml'),
        'vivi_zeit.content.video_source-storystreams': (
            'egg://zeit.web.core/data/config/storystreams.xml'),
        'vivi_zeit.newsletter_renderer-host': 'file:///dev/null',
        'vivi_zeit.solr_solr-url': 'http://mock.solr',
        'vivi_zeit.content.cp_cp-types-url': (
            'egg://zeit.web.core/data/config/cp-types.xml'),
        'vivi_zeit.content.author_biography-questions':
            'egg://zeit.web.core/data/config/author-biography-questions.xml',
        'sso_activate': '',
        'sso_url': 'http://my_sso',
        'sso_cookie': 'my_sso_cookie',
        'sso_rawr_secret': 'my_rawr_secret',
        'jinja2.show_exceptions': True,
        'jinja2.environment': 'jinja2.environment.Environment',
        'jinja2.enable_profiler': False,
        'use_wesgi': True,
        'mock_solr': True,
        'is_admin': True,
        'advertisement_nextread_folder': 'verlagsangebote',
        'quiz_url': 'http://quiz.zeit.de/#/quiz/{quiz_id}',
        'vivi_zeit.web_runtime-settings-source': (
            'egg://zeit.web.core/data/config/zeitweb-settings.xml'),
        # this relies on the existing alias to the current script
        # http://scripts.zeit.de/static/js/webtrekk/webtrekk_v3.js
        'webtrekk_version': '3',
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
def application_session(app_settings, request):
    plone.testing.zca.pushGlobalRegistry()
    zope.browserpage.metaconfigure.clear()
    request.addfinalizer(plone.testing.zca.popGlobalRegistry)
    factory = zeit.web.core.application.Application()
    app = factory({}, **app_settings)
    zope.component.provideUtility(MockSolr())
    # ZODB needs to come after ZCML is set up by the Application.
    # Putting it in here is simpler than adding yet another fixture.
    ZODB_LAYER.setUp()
    request.addfinalizer(ZODB_LAYER.tearDown)
    wsgi = repoze.bitblt.processor.ImageTransformationMiddleware(
        app, secret='time', limit_to_application_url=True)
    wsgi.zeit_app = factory
    return wsgi


@pytest.fixture
def preserve_settings(application_session, request):
    def restore_settings():
        settings = zope.component.queryUtility(
            zeit.web.core.interfaces.ISettings)
        if settings is not None and settings_orig is not None:
            for key, value in settings_orig.items():
                settings[key] = value
            for key in list(settings):
                if key not in settings_orig:
                    del settings[key]
    settings_orig = None
    settings = zope.component.queryUtility(zeit.web.core.interfaces.ISettings)
    if settings is not None:
        request.addfinalizer(restore_settings)
        settings_orig = copy.copy(settings)


@pytest.fixture
def reset_solr(application_session, request):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    if isinstance(solr, MockSolr):
        solr.reset()


@pytest.fixture
def reset_cache(application_session, request):
    pyramid_dogpile_cache2.clear()


@pytest.fixture
def application(
        application_session, preserve_settings, reset_solr, reset_cache,
        zodb, request):
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
def debug_application(app_settings, request):
    plone.testing.zca.pushGlobalRegistry()
    zope.browserpage.metaconfigure.clear()
    request.addfinalizer(plone.testing.zca.popGlobalRegistry)
    app_settings = app_settings.copy()
    app_settings['jinja2.environment'] = 'zeit.web.core.jinja.Environment'
    app_settings['jinja2.show_exceptions'] = False
    return repoze.bitblt.processor.ImageTransformationMiddleware(
        zeit.web.core.application.Application()({}, **app_settings),
        secret='time', limit_to_application_url=True
    )


@pytest.fixture
def dummy_request(application, request):
    req = pyramid.testing.DummyRequest(is_xhr=False)
    # XXX DummyRequest is not life-like enough out-of-the-box, sigh.
    req.GET = webob.multidict.MultiDict(req.GET)
    req.response.headers = set()
    req.matched_route = None

    # See pyramid.router.Router.invoke_subrequest()
    config = application.zeit_app.config
    req.registry = config.registry
    req._set_extensions(config.registry.getUtility(
        pyramid.interfaces.IRequestExtensions))
    config.begin(req)
    request.addfinalizer(pyramid.threadlocal.manager.clear)

    return req


@pytest.fixture(scope='function')
def mockserver_factory(preserve_settings, request):
    def mock_app(env, start_response):
        start_response('200 OK', [])
        return [mock_response[0].format(server=server.url)]
    mock_response = ['']

    server = gocept.httpserverlayer.wsgi.Layer()
    server.wsgi_app = mock_app
    server.setUp()
    server.url = 'http://%s' % server['http_address']
    settings = zope.component.queryUtility(zeit.web.core.interfaces.ISettings)
    if settings is not None:
        settings['community_host'] = server.url
    request.addfinalizer(server.tearDown)

    def factory(response=''):
        mock_response[0] = response
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
        if conf['sleep_reset']:
            conf['sleep'] = 0
        return response
    return timeout


class StaticViewMaybeReplaceHostURL(pyramid.static.static_view):

    def __call__(self, context, request):
        # XXX Should we make the query string behaviour configurable and use
        # a separate mockserver fixture for agatho instead?
        if (request.environ['PATH_INFO'].startswith('/comments') and
                request.query_string):
            request.environ['PATH_INFO'] += u'?' + request.query_string
        response = super(StaticViewMaybeReplaceHostURL, self).__call__(
            context, request)
        if response.content_type in ['application/xml']:
            # Dear pyramid.response.FileResponse, would it kill you to
            # *remember* the path you are passed? Now we have to copy&paste
            # from the superclass and determine the path again.
            path_tuple = pyramid.traversal.traversal_path_info(
                request.environ['PATH_INFO'])
            path = pyramid.static._secure_path(path_tuple)
            filepath = os.path.normcase(os.path.normpath(os.path.join(
                self.norm_docroot, path)))
            contents = open(filepath).read().replace(
                '%HOST%', request.route_url('static', subpath=''))
            response.app_iter = pyramid.response.FileIter(StringIO(contents))
        return response


@pytest.fixture(scope='session')
def mockserver(request):
    """Used for mocking external HTTP dependencies like agatho or spektrum."""
    from pyramid.config import Configurator

    config = Configurator()
    config.add_route('static', '/*subpath')
    config.add_view(StaticViewMaybeReplaceHostURL(
        pkg_resources.resource_filename('zeit.web.core', 'data')),
        route_name='static')
    settings = {'sleep': 0, 'sleep_reset': True}
    settings = pyramid.config.settings.Settings(d=settings)
    interface = ISettings
    zope.interface.declarations.alsoProvides(settings, interface)
    zope.component.provideUtility(settings, interface)
    config.add_tween('zeit.web.core.test.conftest.sleep_tween')
    app = config.make_wsgi_app()
    server = gocept.httpserverlayer.wsgi.Layer()
    server.wsgi_app = app
    server.setUp()
    server.settings = settings
    server.url = 'http://%s' % server['http_address']
    request.addfinalizer(server.tearDown)
    return server


@pytest.fixture(scope='session')
def testserver(application_session, request):
    wsgi_app = wesgi.MiddleWare(
        application_session, forward_headers=True)
    server = waitress.server.create_server(wsgi_app, host='localhost', port=0)
    server.url = 'http://{host}:{port}'.format(
        host=server.effective_host, port=server.effective_port)
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()

    def tearDown():
        server.task_dispatcher.shutdown()
        thread.join(5)
    request.addfinalizer(tearDown)

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
    server.url = 'http://%s' % server['http_address']
    server.wsgi_app = app
    server.setUp()
    request.addfinalizer(server.tearDown)
    return server


@pytest.fixture(scope='session', params=browsers.keys())
def selenium_driver(request):
    if request.param == 'firefox':
        parameters = {}
        profile = selenium.webdriver.FirefoxProfile(
            os.environ.get('ZEIT_WEB_FF_PROFILE'))
        profile.default_preferences.update({
            'network.http.use-cache': False,
            'browser.startup.page': 0,
            'browser.startup.homepage_override.mstone': 'ignore'})
        profile.update_preferences()
        parameters['firefox_profile'] = profile
        # Old versions: <https://ftp.mozilla.org/pub/firefox/releases/>
        ff_binary = os.environ.get('ZEIT_WEB_FF_BINARY')
        if ff_binary:
            parameters['firefox_binary'] = (
                selenium.webdriver.firefox.firefox_binary.FirefoxBinary(
                    ff_binary))
        browser = browsers[request.param](**parameters)
    else:
        browser = browsers[request.param]()

    request.addfinalizer(lambda *args: browser.quit())
    return browser


@pytest.fixture
def image_group_factory():
    class MockImageGroup(dict):
        zope.interface.implements(
            zeit.content.image.interfaces.IImageGroup,
            zope.annotation.interfaces.IAttributeAnnotatable)
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
    return zeit.web.core.routing.RepositoryTraverser(root)


# inspired by http://stackoverflow.com/a/28073449
@pytest.fixture(scope='function')
def clock(monkeypatch):
    """ Now() manager patches datetime return a fixed, settable, value
        (freezes time)
    """
    import datetime
    original = datetime.datetime

    class FreezeMeta(type):
        def __instancecheck__(self, instance):
            if type(instance) == original or type(instance) == Freeze:
                return True

    class Freeze(datetime.datetime):
        __metaclass__ = FreezeMeta

        @classmethod
        def freeze(cls, val):
            cls.frozen = val

        @classmethod
        def now(cls, tz=None):
            if tz is not None:
                if cls.frozen.tzinfo is None:
                    # https://docs.python.org/2/library/datetime.html says,
                    # the result is equivalent to tz.fromutc(
                    #   datetime.utcnow().replace(tzinfo=tz)).
                    return tz.fromutc(cls.frozen.replace(tzinfo=tz))
                else:
                    return cls.frozen.astimezone(tz)
            return cls.frozen

        @classmethod
        def today(cls, tz=None):
            return Freeze.now(tz)

        @classmethod
        def delta(cls, timedelta=None, **kwargs):
            """ Moves time fwd/bwd by the delta"""
            if not timedelta:
                timedelta = datetime.timedelta(**kwargs)
            cls.frozen += timedelta

    monkeypatch.setattr(datetime, 'datetime', Freeze)
    Freeze.freeze(original.utcnow())
    return Freeze


@pytest.fixture
def mock_metrics(monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.metrics, 'timer',
        zeit.web.core.metrics.mock_contextmanager)


@pytest.fixture
def appbrowser(application):
    """Returns an instance of `webtest.TestApp` for wsgi-level testing"""
    return TestApp(application, extra_environ={'HTTP_HOST': 'example.com'})


@pytest.fixture
def testbrowser(application):
    """Wsgi-level test browser (called testbrowser for bw compat)"""
    return WsgiBrowser(wsgi_app=application)


@pytest.fixture
def tplbrowser(jinja2_env):
    """Jinja template renderer with testbrowser-like API"""
    return TemplateBrowser(jinja2_env)


@pytest.fixture
def httpbrowser(testserver):
    """HTTP-level test browser"""
    return HttpBrowser()


class TestApp(webtest.TestApp):

    def get_json(self, url, params=None, headers=None, *args, **kw):
        if headers is None:
            headers = {}
        headers['Accept'] = 'application/json'
        return self.get(url, params, headers, *args, **kw)


# When testing ESI fragments, autodetection of the encoding may not work (no
# head, so no meta charset declaration), so we specify it explicitly.
HTML_PARSER = lxml.html.HTMLParser(encoding='UTF-8')


class BaseBrowser(object):
    """Base class for custom test browsers that allow direct access to CSS and
    XPath selection on their content.

    Usage examples:

    # Create a test browser
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

    def __call__(self, uri=None, **kw):
        if uri is not None:
            self.open(uri, **kw)
        return self

    @property
    def document(self):
        """Return an lxml.html.HtmlElement instance of the response body."""
        if self.contents is not None:
            return lxml.html.document_fromstring(
                self.contents, parser=HTML_PARSER)

    @property
    def json(self):
        """Return a dictionary of the parsed json body if available."""
        if self.contents is not None:
            return json.loads(self.contents)

    def cssselect(self, selector):
        """Return a list of lxml.HTMLElement instances that match a given CSS
        selector.
        """
        xpath = cssselect.HTMLTranslator().css_to_xpath(selector)
        if self.document is not None:
            return self.document.xpath(xpath)

    def xpath(self, selector):
        """Return a list of lxml.HTMLElement instances that match a given
        XPath selector.
        """
        if self.document is not None:
            return self.document.xpath(selector)


class WsgiBrowser(BaseBrowser, zope.testbrowser.wsgi.Browser):

    def open(self, uri, data=None):
        if not uri.startswith('http://localhost'):
            uri = 'http://localhost/{}'.format(uri.lstrip('/'))
        return super(WsgiBrowser, self).open(uri, data)


class TemplateBrowser(BaseBrowser):

    def __init__(self, environ):
        self.env = environ

    def open(self, uri, **kw):
        kw = zeit.web.core.utils.defaultdict(mock.Mock, **kw)
        self.contents = self.env.get_template(uri).render(**kw)


class HttpBrowser(BaseBrowser):

    def open(self, uri, **kw):
        r = requests.get(uri, **kw)
        self.contents = r.text


class MockSolr(object):

    zope.interface.implements(zeit.solr.interfaces.ISolr)

    def __init__(self):
        self.reset()

    def reset(self):
        self.results = []

    def search(self, q, rows=10, **kw):
        results = []
        for i in range(rows):
            try:
                results.insert(0, self.results.pop())
            except IndexError:
                break
        return pysolr.Results(results, self._hits)

    def update_raw(self, xml, **kw):
        pass

    def delete(self, **kw):
        pass

    @property
    def results(self):
        return self._results

    @results.setter
    def results(self, value):
        self._hits = len(value)
        self._results = value


@pytest.fixture
def datasolr(request):
    previous = zope.component.queryUtility(zeit.solr.interfaces.ISolr)
    if previous is not None:
        request.addfinalizer(lambda: zope.component.provideUtility(previous))
    zope.component.provideUtility(zeit.web.core.utils.DataSolr())


@pytest.fixture(scope='session')
def sso_keypair():
    private = generate_private_key(
        public_exponent=65537, key_size=2048,
        backend=cryptography.hazmat.backends.default_backend())
    public = private.public_key()
    private = private.private_bytes(
        encoding=cryptoserialization.Encoding.PEM,
        format=cryptoserialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=cryptoserialization.NoEncryption())
    public = public.public_bytes(
        encoding=cryptoserialization.Encoding.PEM,
        format=cryptoserialization.PublicFormat.SubjectPublicKeyInfo)
    return {'private': private, 'public': public}
