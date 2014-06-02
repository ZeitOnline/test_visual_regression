from grokcore.component import adapter, implementer
from zeit.content.gallery.interfaces import IGalleryMetadata
from zeit.frontend.article import IColumnArticle
from zeit.frontend.article import ILongformArticle
from zeit.frontend.article import IShortformArticle
from zeit.frontend.gallery import IGallery
from zeit.frontend.gallery import IProductGallery
from zeit.magazin.interfaces import IArticleTemplateSettings
import base64
import logging
import os.path
import pkg_resources
import pyramid.config
import pyramid_jinja2
import urlparse
import zeit.connector
import zeit.frontend
import zeit.frontend.banner
import zeit.frontend.block
import zeit.frontend.centerpage
import zeit.frontend.utils
import zeit.frontend.navigation
import zope.app.appsetup.product
import zope.component
import zope.configuration.xmlconfig
import zope.interface


log = logging.getLogger(__name__)


class Application(object):

    DONT_SCAN = ['.testing', '.test', '.preview']

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

    def configure_banner(self):
        banner_source = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.frontend_banner-source', ''))
        zeit.frontend.banner.banner_list = \
            zeit.frontend.banner.make_banner_list(banner_source)

    def configure_pyramid(self):
        registry = pyramid.registry.Registry(
            bases=(zope.component.getGlobalSiteManager(),))

        self.settings['linkreach_host'] = maybe_convert_egg_url(
            self.settings.get('linkreach_host', ''))

        pkg = pkg_resources.get_distribution('zeit.frontend')
        self.settings['version_hash'] = base64.b16encode(pkg.version).lower()

        self.config = config = pyramid.config.Configurator(
            settings=self.settings,
            registry=registry)
        config.setup_registry(settings=self.settings)

        self.config.include('pyramid_tm')
        self.configure_jinja()
        self.config.include("cornice")

        log.debug('Configuring Pyramid')
        config.add_route('json', 'json/*traverse')
        config.add_route('comments', '/-comments/collection/*traverse')
        config.add_route('home', '/')
        config.add_route('health_check', '/health_check')
        config.add_static_view(name='css', path='zeit.frontend:css/')
        config.add_static_view(name='js', path='zeit.frontend:js/')
        config.add_static_view(name='img', path='zeit.frontend:img/')
        config.add_static_view(name='fonts', path='zeit.frontend:fonts/')

        # ToDo: Is this still needed. Can it be removed?
        config.add_static_view(name='mocks', path='zeit.frontend:dummy_html/')

        def asset_url(request, path, **kw):
            kw['_app_url'] = join_url_path(
                request.application_url, request.registry.settings.get(
                    'asset_prefix', ''))
            if path == '/':
                url = request.route_url('home', **kw)
            else:
                prefix = '' if ':' in path else 'zeit.frontend:'
                url = request.static_url(prefix + path, **kw)
            if url.rsplit('.', 1)[-1] in ('css', 'js'):
                url += '?' + request.registry.settings.get('version_hash', '')
            return url

        config.add_request_method(asset_url)

        config.set_root_factory(self.get_repository)
        config.scan(package=zeit.frontend, ignore=self.DONT_SCAN)

        from pyramid.authorization import ACLAuthorizationPolicy
        from .security import CommunityAuthenticationPolicy
        import pyramid_beaker
        config.include("pyramid_beaker")
        session_factory = pyramid_beaker.session_factory_from_settings(
            self.settings)
        config.set_session_factory(session_factory)
        config.set_authentication_policy(CommunityAuthenticationPolicy())
        config.set_authorization_policy(ACLAuthorizationPolicy())
        from zeit.frontend.appinfo import assemble_app_info
        config.add_request_method(assemble_app_info, 'app_info', reify=True)
        return config

    def get_repository(self, request):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def configure_jinja(self):
        """Sets up names and filters that will be available for all
        templates."""
        log.debug('Configuring Jinja')
        self.config.include('pyramid_jinja2')
        self.config.add_renderer('.html', pyramid_jinja2.renderer_factory)
        jinja = self.config.registry.getUtility(
            pyramid_jinja2.IJinja2Environment)

        default_loader = jinja.loader
        jinja.loader = zeit.frontend.utils.PrefixLoader({
            None: default_loader,
            'dav': zeit.frontend.utils.HTTPLoader(self.settings.get(
                'load_template_from_dav_url'))
        }, delimiter='://')

        jinja.trim_blocks = True

        jinja.globals.update(zeit.frontend.navigation.get_sets())
        jinja.globals['get_teaser_template'] = (
            zeit.frontend.utils.most_sufficient_teaser_tpl)
        jinja.globals['get_teaser_image'] = (
            zeit.frontend.utils.most_sufficient_teaser_image)
        jinja.globals['create_image_url'] = (
            zeit.frontend.utils.create_image_url)

        jinja.tests['elem'] = zeit.frontend.block.is_block

        # XXX Use scanning to register filters instead of listing them here
        # again.
        jinja.filters['block_type'] = zeit.frontend.block.block_type
        for name in [
                'auto_select_asset', 'get_all_assets',
                ]:
            jinja.filters[name] = getattr(zeit.frontend.centerpage, name)

        jinja.filters['auto_select_asset'] = (
            zeit.frontend.centerpage.auto_select_asset)
        for name in [
                'format_date', 'format_date_ago',
                'replace_list_seperator', 'translate_url',
                'default_image_url', 'get_image_metadata',
                'obj_debug', 'substring_from', 'hide_none',
                'create_url',
                ]:
            jinja.filters[name] = getattr(zeit.frontend.utils, name)

        return jinja

    def configure_zca(self):
        """Sets up zope.component registrations by reading our
        configure.zcml file."""
        log.debug('Configuring ZCA')
        self.configure_product_config()
        context = zope.configuration.config.ConfigurationMachine()
        zope.configuration.xmlconfig.registerCommonDirectives(context)
        zope.configuration.xmlconfig.include(context, package=zeit.frontend)
        self.configure_connector(context)
        context.execute_actions()

    def configure_connector(self, context):
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
            vivi_zeit.connector_repository-path = egg://zeit.frontend/data

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


@adapter(zeit.cms.repository.interfaces.IRepository)
@implementer(pyramid.interfaces.ITraverser)
class RepositoryTraverser(pyramid.traversal.ResourceTreeTraverser):

    def __call__(self, request):
        try:
            tdict = super(RepositoryTraverser, self).__call__(request)
            context = tdict['context']
            if zeit.content.article.interfaces.IArticle.providedBy(context):
                if IArticleTemplateSettings(context).template == 'longform':
                    zope.interface.alsoProvides(context, ILongformArticle)
                if IArticleTemplateSettings(context).template == 'short':
                    zope.interface.alsoProvides(context, IShortformArticle)
                if IArticleTemplateSettings(context).template == 'column':
                    zope.interface.alsoProvides(context,
                                                IColumnArticle)
            elif zeit.content.gallery.interfaces.IGallery.providedBy(context):
                if IGalleryMetadata(context).type == 'zmo-product':
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
