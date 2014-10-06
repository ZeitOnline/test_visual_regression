import base64
import logging
import os.path
import re
import urlparse
import pkg_resources

import grokcore.component
import pyramid.authorization
import pyramid.config
import pyramid_beaker
import pyramid_jinja2
import pyramid_zodbconn
import venusian
import zope.app.appsetup.product
import zope.component
import zope.configuration.xmlconfig
import zope.interface

import zeit.connector
import zeit.content.gallery.interfaces
import zeit.magazin.interfaces

from zeit.web.core.article import IColumnArticle
from zeit.web.core.article import IFeatureLongform
from zeit.web.core.article import ILongformArticle
from zeit.web.core.article import IPhotoclusterArticle
from zeit.web.core.article import IShortformArticle
from zeit.web.core.gallery import IGallery
from zeit.web.core.gallery import IProductGallery
import zeit.web.core
import zeit.web.core.appinfo
import zeit.web.core.banner
import zeit.web.core.block
import zeit.web.core.centerpage
import zeit.web.core.security
import zeit.web.core.template


log = logging.getLogger(__name__)


class Application(object):

    DONT_SCAN_TESTS = [re.compile('test$').search]
    DONT_SCAN = DONT_SCAN_TESTS + [
        'zeit.web.core.preview']

    def __init__(self):
        self.settings = {}

    def __call__(self, global_config, **settings):
        self.settings.update(settings)
        self.configure()
        return self.make_wsgi_app(global_config)

    def configure(self):
        self.configure_zca()
        self.configure_pyramid()
        self.configure_banner()
        self.configure_navigation()

    def configure_banner(self):
        banner_source = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.frontend_banner-source', ''))
        zeit.web.core.banner.banner_list = (
            zeit.web.core.banner.make_banner_list(banner_source))
        iqd_mobile_ids_source = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.frontend_iqd-mobile-ids', ''))
        zeit.web.core.banner.iqd_mobile_ids = (
            zeit.web.core.banner.make_iqd_mobile_ids(iqd_mobile_ids_source))

    def configure_navigation(self):
        navigation_config = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.frontend_navigation', ''))
        zeit.web.core.navigation.navigation = (
            zeit.web.core.navigation.make_navigation(navigation_config))
        navigation_services_config = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.frontend_navigation-services', ''))
        zeit.web.core.navigation.navigation_services = (
            zeit.web.core.navigation.make_navigation(
                navigation_services_config))
        navigation_classifieds_config = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.frontend_navigation-classifieds', ''))
        zeit.web.core.navigation.navigation_classifieds = (
            zeit.web.core.navigation.make_navigation(
                navigation_classifieds_config))

    def configure_pyramid(self):
        registry = pyramid.registry.Registry(
            bases=(zope.component.getGlobalSiteManager(),))

        self.settings['linkreach_host'] = maybe_convert_egg_url(
            self.settings.get('linkreach_host', ''))

        pkg = pkg_resources.get_distribution('zeit.frontend')
        pkg_version = pkg.version
        self.settings['zmo_version'] = pkg_version
        self.settings['version_hash'] = base64.b16encode(pkg_version).lower()

        self.config = config = pyramid.config.Configurator(
            settings=self.settings,
            registry=registry)
        config.setup_registry(settings=self.settings)

        self.config.include('pyramid_tm')
        self.configure_jinja()
        self.config.include('cornice')

        if self.settings.get('zodbconn.uri'):
            self.config.include('pyramid_zodbconn')

        log.debug('Configuring Pyramid')
        config.add_route('json', 'json/*traverse')
        config.add_route('comments', '/-comments/collection/*traverse')
        config.add_route('home', '/')
        config.add_route('health_check', '/health_check')
        config.add_static_view(name='css', path='zeit.web.static:css/')
        config.add_static_view(name='js', path='zeit.web.static:js/')
        config.add_static_view(name='img', path='zeit.web.static:img/')
        config.add_static_view(name='fonts', path='zeit.web.static:fonts/')

        if not self.settings.get('debug.show_exceptions'):
            config.add_view(view=zeit.web.core.view.service_unavailable,
                            context=Exception)

        def asset_url(request, path, **kw):
            kw['_app_url'] = join_url_path(
                request.application_url, request.registry.settings.get(
                    'asset_prefix', ''))
            if path == '/':
                url = request.route_url('home', **kw)
            else:
                prefix = '' if ':' in path else 'zeit.web.static:'
                url = request.static_url(prefix + path, **kw)
            if url.rsplit('.', 1)[-1] in ('css', 'js'):
                url += '?' + request.registry.settings.get('version_hash', '')
            return url

        config.add_request_method(asset_url)

        config.set_root_factory(self.get_repository)
        config.scan(package=zeit.web, ignore=self.DONT_SCAN)

        config.include('pyramid_beaker')

        zeit.web.core.template.default_teaser_images = (
            self.settings['default_teaser_images'])

        zeit.web.core.template.image_scales = dict(
            zeit.web.core.template.get_image_scales(
                self.settings['vivi_zeit.frontend_image-scales']))

        session_factory = pyramid_beaker.session_factory_from_settings(
            self.settings)
        config.set_session_factory(session_factory)

        config.set_authentication_policy(
            zeit.web.core.security.CommunityAuthenticationPolicy())
        config.set_authorization_policy(
            pyramid.authorization.ACLAuthorizationPolicy())

        config.add_request_method(zeit.web.core.appinfo.assemble_app_info,
                                  'app_info', reify=True)

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
        templates."""
        log.debug('Configuring Jinja')
        self.config.include('pyramid_jinja2')
        self.config.add_renderer('.html', pyramid_jinja2.renderer_factory)
        env = self.config.registry.getUtility(
            pyramid_jinja2.IJinja2Environment)

        env.trim_blocks = True

        default_loader = env.loader
        env.loader = zeit.web.core.template.PrefixLoader({
            None: default_loader,
            'dav': zeit.web.core.template.HTTPLoader(self.settings.get(
                'load_template_from_dav_url'))
        }, delimiter='://')

        if not self.settings.get('debug.propagate_jinja_errors'):
            # If the application is not running in debug mode: overlay the
            # jinja environment with a custom, more fault tolerant one.
            env.__class__ = zeit.web.core.template.Environment
            env = env.overlay()

        venusian.Scanner(env=env).scan(
            zeit.web.core,
            categories=('jinja',),
            ignore=self.DONT_SCAN
        )

        return env

    def configure_zca(self):
        """Sets up zope.component registrations by reading our
        configure.zcml file."""
        log.debug('Configuring ZCA')
        self.configure_product_config()
        zope.component.hooks.setHooks()
        context = zope.configuration.config.ConfigurationMachine()
        zope.configuration.xmlconfig.registerCommonDirectives(context)
        zope.configuration.xmlconfig.include(context, package=zeit.web.core)
        self.configure_connector(context)
        context.execute_actions()

    def configure_connector(self, context):
        if not self.settings.get('zodbconn.uri'):
            zope.component.provideUtility(
                zeit.cms.repository.repository.Repository(),
                zeit.cms.repository.interfaces.IRepository)
        typ = self.settings['connector_type']
        allowed = ('dav', 'tbcdav', 'filesystem')
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

    @property
    def pipeline(self):
        """Configuration of a WSGI pipeline.

        Our WSGI application is wrapped in each filter in turn,
        so the first entry in this list is closest to the application,
        and the last entry is closest to the WSGI server.

        Each entry is a tuple (spec, protocol, name, arguments).
        The default meaning is to load an entry point called ``name`` of type
        ``protocol`` from the package ``spec`` and load it, passing
        ``arguments`` as kw parameters (thus, arguments must be a dict).

        If ``protocol`` is 'factory', then instead of an entry point the method
        of this object with the name ``spec`` is called, passing ``arguments``
        as kw parameters.

        """
        return [
            ('repoze.vhm', 'paste.filter_app_factory', 'vhm_xheaders', {}),
            ('remove_asset_prefix', 'factory', '', {})
        ]

    def remove_asset_prefix(self, app):
        return URLPrefixMiddleware(
            app, prefix=self.settings.get('asset_prefix', ''))

    def make_wsgi_app(self, global_config):
        app = self.config.make_wsgi_app()
        for spec, protocol, name, extra in self.pipeline:
            if protocol == 'factory':
                factory = getattr(self, spec)
                app = factory(app, **extra)
                continue
            entrypoint = pkg_resources.get_entry_info(spec, protocol, name)
            app = entrypoint.load()(app, global_config, **extra)
        return app

factory = Application()


class URLPrefixMiddleware(object):
    """Removes a path prefix from the PATH_INFO if it is present.
    We use this so that if an ``asset_prefix`` is configured, we respond
    correctly for URLs both with and without the asset_prefix -- otherwise
    the reverse proxy in front of us would need to rewrite URLs with
    ``asset_prefix`` to strip it.
    """

    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        if path.startswith(self.prefix):
            environ['PATH_INFO'] = path.replace(self.prefix, '', 1)
        return self.app(environ, start_response)


def maybe_convert_egg_url(url):
    if not url.startswith('egg://'):
        return url
    parts = urlparse.urlparse(url)

    return 'file://' + pkg_resources.resource_filename(
        parts.netloc, parts.path[1:])


def join_url_path(base, path):
    parts = urlparse.urlsplit(base)
    path = os.path.join(parts.path, path)
    return urlparse.urlunsplit(
        (parts[0], parts[1], path, parts[3], parts[4]))


@grokcore.component.adapter(zeit.cms.repository.interfaces.IRepository)
@grokcore.component.implementer(pyramid.interfaces.ITraverser)
class RepositoryTraverser(pyramid.traversal.ResourceTreeTraverser):

    def __call__(self, request):
        try:
            tdict = super(RepositoryTraverser, self).__call__(request)

            context = tdict['context']
            if zeit.content.article.interfaces.IArticle.providedBy(context):
                template = zeit.magazin.interfaces.IArticleTemplateSettings(
                    context).template
                # ToDo: Remove when Longform will be generally used on
                # www.zeit.de. By then do not forget to remove marker
                # interfaces from uniqueID http://xml.zeit.de/feature (RD)
                path = urlparse.urlparse(context.uniqueId).path
                if path[:9] == '/feature/':
                    zope.interface.alsoProvides(context, IFeatureLongform)
                elif template == 'longform':
                    zope.interface.alsoProvides(context, ILongformArticle)
                elif template == 'short':
                    zope.interface.alsoProvides(context, IShortformArticle)
                elif template == 'column':
                    zope.interface.alsoProvides(context, IColumnArticle)
                elif template == 'photocluster':
                    zope.interface.alsoProvides(context, IPhotoclusterArticle)
            elif zeit.content.gallery.interfaces.IGallery.providedBy(context):
                ctx = zeit.content.gallery.interfaces.IGalleryMetadata(context)
                if ctx.type == 'zmo-product':
                    zope.interface.alsoProvides(context, IProductGallery)
                else:
                    zope.interface.alsoProvides(context, IGallery)
            return self._change_viewname(tdict)
        except OSError as e:
            if e.errno == 2:
                raise pyramid.httpexceptions.HTTPNotFound()

    def _change_viewname(self, tdict):
        if tdict['view_name'][0:5] == 'seite' and not tdict['subpath']:
            tdict['view_name'] = 'seite'
        return tdict
