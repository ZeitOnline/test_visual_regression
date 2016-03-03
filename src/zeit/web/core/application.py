import ast
import logging
import os.path
import re
import urlparse

import bugsnag
import bugsnag.wsgi.middleware
import jinja2
import jinja2.ext
import pkg_resources
import pyramid.authorization
import pyramid.config
import pyramid.renderers
import pyramid_jinja2
import pyramid_zodbconn
import pysolr
import requests.sessions
import venusian
import zc.sourcefactory.source
import zope.app.appsetup.product
import zope.component
import zope.configuration.xmlconfig
import zope.interface

import zeit.cms.content.sources
import zeit.cms.content.xmlsupport
import zeit.cms.repository.file
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.connector

import zeit.web
import zeit.web.core
import zeit.web.core.cache
import zeit.web.core.interfaces
import zeit.web.core.jinja
import zeit.web.core.security


log = logging.getLogger(__name__)
CONFIG_CACHE = zeit.web.core.cache.get_region('config')


class Application(object):

    DONT_SCAN = [re.compile('test$').search]

    def __init__(self):
        self.settings = Settings()

    def __call__(self, global_config, **settings):
        self.settings.update(settings)
        self.settings['app_servers'] = filter(
            None, settings['app_servers'].split(','))
        self.settings['linkreach_host'] = maybe_convert_egg_url(
            settings.get('linkreach_host', ''))
        self.settings['sso_key'] = self.load_sso_key(
            settings.get('sso_key', None))
        # NOTE: non-pyramid utilities can only access deployment settings,
        # runtime settings are not available until Application setup is done.
        zope.component.provideUtility(
            self.settings, zeit.web.core.interfaces.ISettings)
        self.configure()
        app = self.config.make_wsgi_app()
        # TODO: Try to move bugsnag middleware config to web.ini
        return bugsnag.wsgi.middleware.BugsnagMiddleware(app)

    def load_sso_key(self, keyfile):
        if keyfile:
            with open(keyfile[7:], "r") as myfile:
                return myfile.read()

    def configure(self):
        self.configure_zca()
        self.configure_pyramid()
        self.configure_bugsnag()

    def configure_bugsnag(self):
        bugsnag.configure(
            api_key=self.settings.get('bugsnag_token'),
            project_root=pkg_resources.get_distribution('zeit.web').location,
            app_version=self.settings.get('version'),
            notify_release_stages=['devel', 'staging', 'production'],
            release_stage=self.settings.get('environment', 'dev')
        )

    def configure_pyramid(self):
        registry = pyramid.registry.Registry(
            bases=(zope.component.getGlobalSiteManager(),))

        mapper = zeit.web.core.routing.RoutesMapper()
        registry.registerUtility(mapper, pyramid.interfaces.IRoutesMapper)

        self.settings['version'] = pkg_resources.get_distribution(
            'zeit.web').version

        self.config = config = pyramid.config.Configurator(registry=registry)
        config.setup_registry(settings=self.settings)
        # setup_registry() insists on copying the settings mapping into a new
        # `pyramid.config.settings.Settings` instance. But we want
        # registry.settings and the ISettings utility to be the same object,
        # for easy test setup. So we first copy over any values set by Pyramid
        # or included packages, and then replace the Pyramid instance with our
        # instance again.
        self.settings.deployment.update(config.registry.settings)
        config.registry.settings = self.settings

        # Never commit, always abort. zeit.web should never write anything,
        # anyway, and at least when running in preview mode, not committing
        # neatly avoids ConflictErrors.
        self.config.registry.settings['tm.commit_veto'] = lambda *args: True
        self.config.include('pyramid_tm')
        self.configure_jinja()

        if self.settings.get('zodbconn.uri'):
            self.config.include('pyramid_zodbconn')

        log.debug('Configuring Pyramid')
        config.add_route('framebuilder', '/framebuilder')
        config.add_route('instantarticle', '/instantarticle/*traverse')
        config.add_route(
            'instantarticle-item', '/instantarticle-item/*traverse')
        config.add_route('fbia', '/fbia/*traverse')
        config.add_route('amp', '/amp/*traverse')
        config.add_route('json_delta_time', '/json/delta_time')
        config.add_route('json_update_time', '/json_update_time/{path:.*}')
        config.add_route('json_comment_count', '/json/comment_count')
        config.add_route('comments', '/-comments/collection/*traverse')
        config.add_route('invalidate_comment_thread', '/-comments/invalidate')
        config.add_route(
            'invalidate_community_maintenance',
            '/-comments/invalidate_maintenance')
        config.add_route('newsfeed', '/newsfeed/*traverse')
        config.add_route('home', '/')
        config.add_route('login_state', '/login-state')
        config.add_route('health_check', '/health_check')
        config.add_route('spektrum-image', '/spektrum-image/*path')
        config.add_route('zett-image', '/zett-image/*path')
        config.add_route('blacklist', '/-blacklist', factory=lambda x: None)
        config.add_route(
            'schlagworte_index',
            '/schlagworte/{category}/{item:[A-Z]($|/$|/index$)}')
        config.add_route(
            'schlagworte',
            '/schlagworte/{category}/{item}{subpath:($|/$|/index$)}')

        # Route to post comments to a communit service
        config.add_route('post_test_comments', '/admin/test-comments')

        config.add_static_view(
            name=self.settings.get('asset_prefix', '/static/latest'),
            path='zeit.web.static:',
            cache_max_age=ast.literal_eval(self.settings['assets_max_age']))

        config.add_static_view(name=self.settings.get(
            'jsconf_prefix', '/jsconf'), path='zeit.web.core:data/config')

        config.add_renderer('jsonp', pyramid.renderers.JSONP(
            param_name='callback'))

        config.add_route('xml', '/xml/*traverse')

        config.add_request_method(configure_host('asset'), reify=True)
        config.add_request_method(configure_host('image'), reify=True)
        config.add_request_method(configure_host('jsconf'), reify=True)
        config.add_request_method(configure_host('fbia'), reify=True)

        config.add_request_method(
            zeit.web.core.security.get_user, name='user', reify=True)

        config.set_root_factory(self.get_repository)
        config.scan(package=zeit.web, ignore=self.DONT_SCAN)

        config.include('pyramid_dogpile_cache2')

        config.set_session_factory(zeit.web.core.session.CacheSession)

        config.set_authentication_policy(
            zeit.web.core.security.AuthenticationPolicy())
        config.set_authorization_policy(
            pyramid.authorization.ACLAuthorizationPolicy())

        return config

    def get_repository(self, request):
        if self.settings.get('zodbconn.uri'):
            connection = pyramid_zodbconn.get_connection(request)
            root = connection.root()
            # We probably should not hardcode the name, but use
            # ZopePublication.root_name instead, but since the name is not ever
            # going to be changed, we can safely skip the dependency on
            # zope.app.publication.
            root_folder = root.get('Application', None)
            zope.component.hooks.setSite(root_folder)
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def configure_jinja(self):
        """Sets up names and filters that will be available for all
        templates.
        """
        log.debug('Configuring Jinja')
        self.config.include('pyramid_jinja2')
        self.config.add_renderer('.html', pyramid_jinja2.renderer_factory)
        self.config.add_jinja2_extension(
            jinja2.ext.WithExtension)
        self.config.add_jinja2_extension(
            zeit.web.core.jinja.ProfilerExtension)
        self.config.add_jinja2_extension(
            zeit.web.core.jinja.RequireExtension)

        self.config.commit()
        self.jinja_env = env = self.config.get_jinja2_environment()
        env.finalize = zeit.web.core.jinja.finalize
        env.trim_blocks = True

        default_loader = env.loader
        env.loader = zeit.web.core.jinja.PrefixLoader({
            None: default_loader,
            'dav': zeit.web.core.jinja.HTTPLoader(self.settings.get(
                'load_template_from_dav_url'))
        }, delimiter='://')

        venusian.Scanner(env=env).scan(
            zeit.web.core,
            categories=('jinja',),
            ignore=self.DONT_SCAN)

    def configure_zca(self):
        """Sets up zope.component registrations by reading our
        configure.zcml file.
        """
        log.debug('Configuring ZCA')
        self.configure_product_config()
        zope.component.hooks.setHooks()
        context = zope.configuration.config.ConfigurationMachine()
        zope.configuration.xmlconfig.registerCommonDirectives(context)
        zope.configuration.xmlconfig.include(context, package=zeit.web)
        self.configure_connector(context)
        self.configure_overrides(context)
        context.execute_actions()

    def configure_connector(self, context):
        if not self.settings.get('zodbconn.uri'):
            zope.component.provideUtility(
                zeit.cms.repository.repository.Repository(),
                zeit.cms.repository.interfaces.IRepository)
        typ = self.settings['connector_type']
        allowed = ('real', 'dav', 'filesystem', 'mock')
        if typ not in allowed:
            raise ValueError(
                'Invalid setting connector_type=%s, allowed are {%s}'
                % (typ, ', '.join(allowed)))
        zope.configuration.xmlconfig.include(
            context, package=zeit.connector, file='%s-connector.zcml' % typ)

    def configure_product_config(self):
        """Sets values of Zope Product Config used by vivi for configuration,
        using settings from the WSGI ini file.

        Requires the following naming convention in the ini file:
            vivi_<PACKAGE>_<SETTING> = <VALUE>
        for example
            vivi_zeit.connector_repository-path = egg://zeit.web.core/data

        (XXX This is based on the assumption that vivi never uses an underscore
        in a SETTING name.)

        For convenience we resolve egg:// URLs using pkg_resources into file://
        URLs. This functionality should probably move to vivi, see VIV-288.
        """
        for key, value in self.settings.items():
            if not key.startswith('vivi_'):
                continue

            ignored, package, setting = key.split('_')
            if zope.app.appsetup.product.getProductConfiguration(
                    package) is None:
                zope.app.appsetup.product.setProductConfiguration(package, {})
            config = zope.app.appsetup.product.getProductConfiguration(package)
            value = maybe_convert_egg_url(value)
            # XXX Stopgap until FRIED-12, since MockConnector does not
            # understand file-URLs
            if key == 'vivi_zeit.connector_repository-path':
                value = value.replace('file://', '')
            config[setting] = value

    def configure_overrides(self, context):
        """Local development environments use an overrides zcml to allow
        us to mock external dependencies or tweak the zope product config.
        """
        if self.settings.get('dev_environment'):
            zope.configuration.xmlconfig.includeOverrides(
                context, package=zeit.web.core, file='overrides.zcml')


@zope.interface.implementer(zeit.web.core.interfaces.ISettings)
class Settings(pyramid.config.settings.Settings,
               zeit.cms.content.sources.SimpleXMLSourceBase):

    product_configuration = 'zeit.web'
    config_url = 'runtime-settings-source'

    runtime_config = 'vivi_{}_{}'.format(product_configuration, config_url)

    @property
    def deployment(self):
        return super(Settings, self)

    @property
    def runtime(self):
        if ('backend' not in CONFIG_CACHE.__dict__ or
                not self.deployment.__contains__(self.runtime_config)):
            # We're at an early Application setup stage, no runtime
            # configuration available or needed (e.g. for Pyramid setup).
            return {}
        return self._load_runtime_settings()

    @CONFIG_CACHE.cache_on_arguments()
    def _load_runtime_settings(self):
        result = {}
        for node in self._get_tree().iterfind('setting'):
            result[node.get('name')] = node.pyval
        return result

    @property
    def combined(self):
        result = {}
        result.update(self.runtime)
        result.update(self)
        return result

    def get(self, key, default=None):
        if self.deployment.__contains__(key):
            return self.deployment.get(key)
        return self.runtime.get(key, default)

    def __getitem__(self, key):
        if self.deployment.__contains__(key):
            return self.deployment.get(key)
        return self.runtime[key]

    def __contains__(self, key):
        return (self.deployment.__contains__(key) or
                self.runtime.__contains__(key))

    def keys(self):
        return self.combined.keys()

    def values(self):
        return self.combined.values()

    def items(self):
        return self.combined.items()

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())


factory = Application()


def maybe_convert_egg_url(url):
    if not url.startswith('egg://'):
        return url
    parts = urlparse.urlparse(url)

    return 'file://' + pkg_resources.resource_filename(
        parts.netloc, parts.path[1:])


def join_url_path(base, path):
    parts = urlparse.urlsplit(base)
    path = (parts.path + path).replace('//', '/')
    return urlparse.urlunsplit(
        (parts[0], parts[1], path, parts[3], parts[4]))


def configure_host(key):
    def wrapped(request):
        prefix = request.registry.settings.get(key + '_prefix', '')
        version = request.registry.settings.get('version', 'latest')
        prefix = prefix.format(version=version)
        if not prefix.startswith('http'):
            prefix = join_url_path(
                request.application_url, '/' + prefix.strip('/'))
        return request.route_url('home', _app_url=prefix).rstrip('/')
    wrapped.__name__ = key + '_host'
    return wrapped


class FeatureToggleSource(zeit.cms.content.sources.SimpleContextualXMLSource):
    # Only contextual so we can customize source_class

    product_configuration = 'zeit.web'
    config_url = 'feature-toggle-source'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        def find(self, name):
            return self.factory.find(name)

    def find(self, name):
        try:
            return bool(getattr(self._get_tree(), name, False))
        except TypeError:
            return False

FEATURE_TOGGLES = FeatureToggleSource()(None)


# Monkey-patch so our content provides a marker interface,
# thus Source entries can be ``available`` only for zeit.web, but not vivi.
def getitem_with_marker_interface(self, key):
    unique_id = self._get_id_for_name(key)

    __traceback_info__ = (key, unique_id)
    content = self.repository.getUncontainedContent(unique_id)
    # We copied the original method wholesale since calling alsoProvides only
    # once proved to be a significant performance gain,...
    zope.interface.alsoProvides(
        content,
        zeit.cms.repository.interfaces.IRepositoryContent,
        zeit.web.core.interfaces.IInternalUse)
    # ...and we don't want to locate content here, due to resolve_parent below.
    return content
zeit.cms.repository.repository.Container.__getitem__ = (
    getitem_with_marker_interface)


# Performance optimization: Instead of traversing to the target object (and
# thus instantiating all the folders in between), resolve it directly via the
# connector, if possible. Notable exceptions include variant images and dynamic
# folders, those are retried the traditional way.
# NOTE: We cannot locate the content object here, since not materializing the
# __parent__ folder is kind of the point. Thus, ``resolve_parent`` below.
def getcontent_try_without_traversal(self, unique_id):
    try:
        content = self.getUncontainedContent(unique_id)
    except KeyError:
        return original_getcontent(self, unique_id)
    zope.interface.alsoProvides(
        content, zeit.cms.repository.interfaces.IRepositoryContent,
        zeit.web.core.interfaces.IInternalUse)
    return content
original_getcontent = zeit.cms.repository.repository.Repository.getContent
zeit.cms.repository.repository.Repository.getContent = (
    getcontent_try_without_traversal)


# Determine __parent__ folder on access, instead of having Repository write it.
def resolve_parent(self):
    workingcopy_parent = getattr(self, '_v_workingcopy_parent', None)
    if workingcopy_parent is not None:
        return workingcopy_parent

    unique_id = self.uniqueId
    trailing_slash = unique_id.endswith('/')
    if trailing_slash:
        unique_id = unique_id[:-1]
    parent_id = os.path.dirname(unique_id)
    parent_id = parent_id.rstrip('/') + '/'
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    return original_getcontent(repository, parent_id)


# For checkout (which we use in tests) the parent must be settable.
def set_workingcopy_parent(self, value):
    self._v_workingcopy_parent = value

# XXX Patching all possible content base-classes is a bit of guesswork.
zeit.cms.content.xmlsupport.XMLContentBase.__parent__ = property(
    resolve_parent, set_workingcopy_parent)
zeit.cms.repository.file.RepositoryFile.__parent__ = property(
    resolve_parent, set_workingcopy_parent)
zeit.cms.repository.folder.Folder.__parent__ = property(
    resolve_parent, set_workingcopy_parent)


# Skip superfluous disk accesses, since we never use netrc for authentication.
requests.sessions.get_netrc_auth = lambda *args, **kw: None


# Allow pysolr error handling to deal with non-ascii HTML error pages
def scrape_response_nonascii(self, headers, response):
    if isinstance(response, str):
        response = response.decode('utf-8')
    return original_scrape_response(self, headers, response)
original_scrape_response = pysolr.Solr._scrape_response
pysolr.Solr._scrape_response = scrape_response_nonascii


# Make solr timeout runtime configurable
def solr_timeout_from_settings(self):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return conf.get('solr_timeout', 5)
pysolr.Solr.timeout = property(
    solr_timeout_from_settings, lambda self, value: None)
