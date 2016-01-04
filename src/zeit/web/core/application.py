import ast
import logging
import os.path
import pkg_resources
import re
import urlparse

import bugsnag
import bugsnag.wsgi.middleware
import jinja2
import jinja2.ext
import pyramid.authorization
import pyramid.config
import pyramid.renderers
import pyramid_beaker
import pyramid_jinja2
import pyramid_zodbconn
import requests.sessions
import venusian
import zope.app.appsetup.product
import zope.component
import zope.configuration.xmlconfig
import zope.interface
import zope.interface.declarations

import zeit.cms.content.xmlsupport
import zeit.cms.repository.file
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.connector

import zeit.web
import zeit.web.core
import zeit.web.core.banner
import zeit.web.core.interfaces
import zeit.web.core.jinja
import zeit.web.core.security


log = logging.getLogger(__name__)


class Application(object):

    DONT_SCAN = [re.compile('test$').search]

    def __init__(self):
        self.settings = {}

    def __call__(self, global_config, **settings):
        settings = pyramid.config.settings.Settings(d=settings)
        settings['app_servers'] = filter(
            None, settings['app_servers'].split(','))
        settings['enable_third_party_modules'] = bool(settings.get(
            'enable_third_party_modules', True))
        settings['enable_trackers'] = bool(settings.get(
            'enable_trackers', True))
        settings['enable_iqd'] = bool(settings.get(
            'enable_iqd', True))
        settings['linkreach_host'] = maybe_convert_egg_url(
            settings.get('linkreach_host', ''))

        settings['sso_key'] = self.load_sso_key(
            settings.get('sso_key', None))
        self.settings.update(settings)
        # Temporarily provide settings for our non-pyramid utilities.
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
        self.configure_banner()
        self.configure_navigation()
        self.configure_bugsnag()

    def configure_banner(self):
        banner_source = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.web_banner-source', ''))
        zeit.web.core.banner.banner_list = (
            zeit.web.core.banner.make_banner_list(banner_source))
        iqd_mobile_ids_source = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.web_iqd-mobile-ids', ''))
        zeit.web.core.banner.iqd_mobile_ids = (
            zeit.web.core.banner.make_iqd_mobile_ids(iqd_mobile_ids_source))
        banner_id_mappings = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.web_banner-id-mappings', ''))
        zeit.web.core.banner.banner_id_mappings = (
            zeit.web.core.banner.make_banner_id_mappings(banner_id_mappings))

    def configure_navigation(self):
        navigation_config = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.web_navigation', ''))
        zeit.web.core.navigation.navigation = (
            zeit.web.core.navigation.make_navigation(navigation_config))
        zeit.web.core.navigation.navigation_by_name = (
            zeit.web.core.navigation.make_navigation_by_name(
                navigation_config))
        navigation_services_config = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.web_navigation-services', ''))
        zeit.web.core.navigation.navigation_services = (
            zeit.web.core.navigation.make_navigation(
                navigation_services_config))
        navigation_classifieds_config = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.web_navigation-classifieds', ''))
        zeit.web.core.navigation.navigation_classifieds = (
            zeit.web.core.navigation.make_navigation(
                navigation_classifieds_config))
        navigation_footer_publisher_config = maybe_convert_egg_url(
            self.settings.get(
                'vivi_zeit.web_navigation-footer-publisher', ''))
        zeit.web.core.navigation.navigation_footer_publisher = (
            zeit.web.core.navigation.make_navigation(
                navigation_footer_publisher_config))
        navigation_footer_links_config = maybe_convert_egg_url(
            self.settings.get(
                'vivi_zeit.web_navigation-footer-links', ''))
        zeit.web.core.navigation.navigation_footer_links = (
            zeit.web.core.navigation.make_navigation(
                navigation_footer_links_config))

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
        zope.component.getSiteManager().unregisterUtility(
            self.settings, zeit.web.core.interfaces.ISettings)
        zope.component.provideUtility(
            config.registry.settings, zeit.web.core.interfaces.ISettings)

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
        config.add_route('instantarticle_feed', '/instantarticle-feed')
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
        config.add_route(
            'schlagworte_index',
            '/schlagworte/{category}/{item:[A-Z]($|/$|/index$)}')
        config.add_route(
            'schlagworte',
            '/schlagworte/{category}/{item}{subpath:($|/$|/index$)}')

        # Route to post comments to a communit service
        config.add_route('post_test_comments', '/admin/test-comments')
        config.add_route('toggle_third_party_modules', '/admin/toggle-tpm')

        config.add_static_view(
            name=self.settings.get('asset_prefix', '/static/latest'),
            path='zeit.web.static:',
            cache_max_age=ast.literal_eval(self.settings['assets_max_age']))

        config.add_static_view(name=self.settings.get(
            'jsconf_prefix', '/jsconf'), path='zeit.web.core:data/config')

        config.add_renderer('jsonp', pyramid.renderers.JSONP(
            param_name='callback'))

        config.add_route('xml', '/xml/*traverse')

        config.set_request_property(configure_host('asset'), reify=True)
        config.set_request_property(configure_host('image'), reify=True)
        config.set_request_property(configure_host('jsconf'), reify=True)

        config.set_root_factory(self.get_repository)
        config.scan(package=zeit.web, ignore=self.DONT_SCAN)

        config.include('pyramid_beaker')

        pyramid_beaker.set_cache_regions_from_settings(self.settings)

        session_factory = pyramid_beaker.session_factory_from_settings(
            self.settings)
        config.set_session_factory(session_factory)

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
        self.config.add_jinja2_extension(jinja2.ext.WithExtension)
        self.config.add_jinja2_extension(
            zeit.web.core.jinja.ProfilerExtension)

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
