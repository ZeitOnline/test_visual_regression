import base64
import logging
import os.path
import pkg_resources
import re
import urlparse
import warnings

import grokcore.component
import jinja2
import jinja2.ext
import pyramid.authorization
import pyramid.config
import pyramid.renderers
import pyramid_beaker
import pyramid_jinja2
import pyramid_zodbconn
import venusian
import zope.app.appsetup.product
import zope.component
import zope.configuration.xmlconfig
import zope.interface
import zope.interface.declarations

import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.connector
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.dynamicfolder.interfaces
import zeit.content.gallery.interfaces
import zeit.content.video.interfaces
import zeit.find.search
import zeit.magazin.interfaces
import zeit.solr.interfaces

import zeit.web
import zeit.web.core
import zeit.web.core.article
import zeit.web.core.banner
import zeit.web.core.block
import zeit.web.core.centerpage
import zeit.web.core.gallery
import zeit.web.core.interfaces
import zeit.web.core.jinja
import zeit.web.core.security
import zeit.web.core.sources
import zeit.web.site.module.search_form


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

        interface = zeit.web.core.interfaces.ISettings
        zope.interface.declarations.alsoProvides(settings, interface)
        zope.component.provideUtility(settings, interface)
        self.settings.update(settings)
        self.configure()
        return self.make_wsgi_app(global_config)

    def configure(self):
        self.configure_zca()
        self.configure_pyramid()
        self.configure_banner()
        self.configure_series()
        self.configure_navigation()

    def configure_banner(self):
        banner_source = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.web_banner-source', ''))
        zeit.web.core.banner.banner_list = (
            zeit.web.core.banner.make_banner_list(banner_source))
        zeit.web.core.banner.banner_toggles = (
            zeit.web.core.banner.make_banner_toggles(banner_source))
        iqd_mobile_ids_source = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.web_iqd-mobile-ids', ''))
        zeit.web.core.banner.iqd_mobile_ids = (
            zeit.web.core.banner.make_iqd_mobile_ids(iqd_mobile_ids_source))
        banner_id_mappings = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.web_banner-id-mappings', ''))
        zeit.web.core.banner.banner_id_mappings = (
            zeit.web.core.banner.make_banner_id_mappings(banner_id_mappings))

    def configure_series(self):
        series_source = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.web_series-source', ''))
        zeit.web.core.sources.video_series = (
            zeit.web.core.sources.get_video_series(series_source))

    def configure_navigation(self):
        navigation_config = maybe_convert_egg_url(
            self.settings.get('vivi_zeit.web_navigation', ''))
        zeit.web.core.navigation.navigation = (
            zeit.web.core.navigation.make_navigation(navigation_config))
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

    def configure_pyramid(self):
        registry = pyramid.registry.Registry(
            bases=(zope.component.getGlobalSiteManager(),))

        self.settings['linkreach_host'] = maybe_convert_egg_url(
            self.settings.get('linkreach_host', ''))

        version = pkg_resources.get_distribution('zeit.web').version
        self.settings['version'] = version
        self.settings['version_hash'] = base64.b16encode(version).lower()

        self.config = config = pyramid.config.Configurator(
            settings=self.settings,
            registry=registry)
        config.setup_registry(settings=self.settings)

        self.config.include('pyramid_tm')
        self.configure_jinja()

        if self.settings.get('zodbconn.uri'):
            self.config.include('pyramid_zodbconn')

        log.debug('Configuring Pyramid')
        config.add_route('json_delta_time', '/json/delta_time')
        config.add_route('json_update_time', '/json_update_time/{path:.*}')
        config.add_route('json_comment_count', '/json/comment_count')
        config.add_route('comments', '/-comments/collection/*traverse')
        config.add_route('home', '/')
        config.add_route('beta_toggle', '/beta')
        config.add_route('login_state', '/login-state')
        config.add_route('beta_toggle_json', '/beta/json')
        config.add_route('health_check', '/health_check')
        config.add_route('spektrum-kooperation', '/spektrum-kooperation')
        config.add_route('spektrum-image', '/spektrum-image/*path')

        # Route to post comments to a communit service
        config.add_route('post_test_comments', '/admin/test-comments')
        config.add_route('toggle_third_party_modules', '/admin/toggle-tpm')

        config.add_static_view(name='css', path='zeit.web.static:css/')
        config.add_static_view(name='js', path='zeit.web.static:js/')
        config.add_static_view(name='img', path='zeit.web.static:img/')
        config.add_static_view(name='fonts', path='zeit.web.static:fonts/')
        config.add_renderer('jsonp', pyramid.renderers.JSONP(
            param_name='callback'))

        config.add_route('xml', '/xml/*traverse')

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

        pyramid_beaker.set_cache_regions_from_settings(self.settings)

        session_factory = pyramid_beaker.session_factory_from_settings(
            self.settings)
        config.set_session_factory(session_factory)

        config.set_authentication_policy(
            zeit.web.core.security.CommunityAuthenticationPolicy())
        config.set_authorization_policy(
            pyramid.authorization.ACLAuthorizationPolicy())

        warnings.warn('The authenticated user_id API will be deprecated in'
                      'pyramid 1.5', DeprecationWarning)
        config.add_request_method(pyramid.security.authenticated_userid,
                                  'authenticated_userid', reify=True)

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
        env.trim_blocks = True

        default_loader = env.loader
        env.loader = zeit.web.core.jinja.PrefixLoader({
            None: default_loader,
            'dav': zeit.web.core.jinja.HTTPLoader(self.settings.get(
                'load_template_from_dav_url'))
        }, delimiter='://')

        if not self.settings.get('debug.propagate_jinja_errors'):
            # If the application is not running in debug mode: overlay the
            # jinja environment with a custom, more fault tolerant one.
            env.__class__ = zeit.web.core.jinja.Environment
            env = env.overlay()

        venusian.Scanner(env=env).scan(
            zeit.web.core,
            categories=('jinja',),
            ignore=self.DONT_SCAN
        )

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

    @property
    def pipeline(self):
        """Configuration of a WSGI pipeline.

        Our WSGI application is wrapped in each filter in turn,
        so the first entry in this list is closest to the application,
        and the last entry is closest to the WSGI server.

        Each entry is a tuple (spec, protocol, name, arguments).
        The default meaning is to load an entry point called `name` of type
        `protocol` from the package `spec` and load it, passing
        `arguments` as kw parameters (thus, arguments must be a dict).

        If `protocol` is 'factory', then instead of an entry point the method
        of this object with the name `spec` is called, passing `arguments`
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
    We use this so that if an `asset_prefix` is configured, we respond
    correctly for URLs both with and without the asset_prefix -- otherwise
    the reverse proxy in front of us would need to rewrite URLs with
    `asset_prefix` to strip it.
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


def find_block(context, attrib='cp:__name__', **specs):
    """Find a block (region/area/module/block/container/cluster, you name it)
    in the XML of a given context. You can pass in arbitrary keyword arguments
    that need to match the attributes of your desired block.
    You may also need to override the name of the uuid attribute using the
    attrib keyword.
    """
    # XXX Maybe this would also work with IXMLReference?
    # zope.component.queryAdapter(
    #     context, zeit.cms.content.interfaces.IXMLReference, name='related')

    tpl = jinja2.Template("""
        .//*[{% for k, v in specs %}@{{ k }}="{{ v }}"{% endfor %}]/@{{ attr }}
    """)
    unique_ids = context.xml.xpath(
        tpl.render(attr=attrib, specs=specs.items()).strip(),
        namespaces={'cp': 'http://namespaces.zeit.de/CMS/cp'})
    try:
        block = context.get_recursive(unique_ids[0])
        return zeit.cms.interfaces.ICMSContent(block.uniqueId)
    except (AttributeError, IndexError, TypeError):
        return


@grokcore.component.adapter(zeit.cms.repository.interfaces.IRepository)
@grokcore.component.implementer(pyramid.interfaces.ITraverser)
class RepositoryTraverser(pyramid.traversal.ResourceTreeTraverser):

    def __call__(self, request):
        tdict = super(RepositoryTraverser, self).__call__(request)
        try:
            tdict.setdefault('request', request)
            self.rewrite_cp2015(tdict)
            tdict = zope.component.getMultiAdapter(
                (tdict['context'], tdict),
                zeit.web.core.interfaces.ITraversable)
        except OSError as e:
            if e.errno == 2:
                raise pyramid.httpexceptions.HTTPNotFound()
        except (zope.component.ComponentLookupError, TypeError):
            pass
        finally:
            return tdict

    @staticmethod
    def rewrite_cp2015(tdict):
        # XXX Remove after parallel cp-editor operation period is over (ND).
        try:
            name = '{}.cp2015'.format(tdict['context'].__name__)
            pos = tdict['traversed'].index(tdict['context'].__name__)
            tdict['context'] = tdict['context'].__parent__[name]
        except (KeyError, TypeError, ValueError):
            pass
        else:
            travd = tdict['traversed']
            tdict['traversed'] = travd[:pos] + (name,) + travd[pos + 1:]


@grokcore.component.implementer(zeit.web.core.interfaces.ITraversable)
@grokcore.component.adapter(zeit.content.article.interfaces.IArticle, dict)
class TraversableArticle(dict):

    def __init__(self, context, tdict):
        settings = zeit.magazin.interfaces.IArticleTemplateSettings(context)

        if urlparse.urlparse(context.uniqueId).path.startswith('/feature/'):
            # ToDo: Remove when Longform will be generally used on
            # www.zeit.de. By then do not forget to remove marker
            # interfaces from uniqueID http://xml.zeit.de/feature (RD)
            zope.interface.alsoProvides(
                context, zeit.web.core.article.IFeatureLongform)
        elif settings.template == 'longform':
            zope.interface.alsoProvides(
                context, zeit.web.core.article.ILongformArticle)
        elif settings.template == 'short':
            zope.interface.alsoProvides(
                context, zeit.web.core.article.IShortformArticle)
        elif settings.template == 'column':
            zope.interface.alsoProvides(
                context, zeit.web.core.article.IColumnArticle)
        elif settings.template == 'liveblog':
            zope.interface.alsoProvides(
                context, zeit.web.core.article.ILiveblogArticle)
        elif settings.template == 'photocluster':
            zope.interface.alsoProvides(
                context, zeit.web.core.article.IPhotoclusterArticle)

        if tdict['view_name'].startswith('seite') and not tdict['subpath']:
            tdict['view_name'] = 'seite'

        super(TraversableArticle, self).__init__(tdict)


@grokcore.component.implementer(zeit.web.core.interfaces.ITraversable)
@grokcore.component.adapter(zeit.content.gallery.interfaces.IGallery, dict)
class TraversableGallery(dict):

    def __init__(self, context, tdict):
        context = tdict['context']
        metadata = zeit.content.gallery.interfaces.IGalleryMetadata(context)

        if metadata.type == 'zmo-product':
            zope.interface.alsoProvides(
                context, zeit.web.core.gallery.IProductGallery)
        else:
            zope.interface.alsoProvides(
                context, zeit.web.core.gallery.IGallery)

        super(TraversableGallery, self).__init__(tdict)


@grokcore.component.implementer(zeit.web.core.interfaces.ITraversable)
@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage, dict)
class TraversableCenterPage(dict):

    def __init__(self, context, tdict):
        area = find_block(context, attrib='area', kind='ranking')
        if area:
            area = zeit.web.core.template.get_area(area)
            form = find_block(context, module='search-form')
            # XXX: Pretty inelegant, maybe use pub/subbing in the future? (ND)
            if form:
                form = zeit.web.core.template.get_module(form)
                form['q'] = ' '.join(tdict['request'].GET.getall('q'))
                form['type'] = ' '.join(tdict['request'].GET.getall('type'))
                form['mode'] = tdict['request'].GET.get('mode')
                form['sort'] = tdict['request'].GET.get('sort')
                area.raw_query = form.raw_query
                area.sort_order = form.sort_order
                area.query = form.query
            else:
                form = zeit.web.site.module.search_form.Form(context)

            form['page'] = tdict['request'].GET.get('p')
            area.page = form.page

        super(TraversableCenterPage, self).__init__(tdict)


@grokcore.component.implementer(zeit.web.core.interfaces.ITraversable)
@grokcore.component.adapter(
    zeit.content.dynamicfolder.interfaces.IRepositoryDynamicFolder, dict)
class TraversableDynamic(TraversableCenterPage):

    def __init__(self, context, tdict):
        try:
            tdict['context'] = context = tdict['context'][tdict['view_name']]
        except (IndexError, KeyError, TypeError):
            pass
        else:
            tdict['traversed'] += (tdict['view_name'],)
            tdict['view_name'] = ''
        finally:
            super(TraversableDynamic, self).__init__(context, tdict)


@grokcore.component.implementer(zeit.web.core.interfaces.ITraversable)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo, dict)
class TraversableVideo(dict):

    def __init__(self, context, tdict):
        # XXX: Let's hope no video is ever called 'imagegroup'
        #      or 'comment-form' or 'report-form'. (ND)
        if tdict['view_name'] not in ('imagegroup', 'comment-form',
                                      'report-form'):
            tdict['request'].headers['X-SEO-Slug'] = tdict['view_name']
            tdict['view_name'] = ''
        super(TraversableVideo, self).__init__(tdict)


# Monkey-patch so our content provides a marker interface,
# thus Source entries can be ``available`` only for zeit.web, but not vivi.
def getitem_with_marker_interface(self, key):
    content = original_getitem(self, key)
    zope.interface.alsoProvides(
        content, zeit.web.core.interfaces.IInternalUse)
    return content
original_getitem = zeit.cms.repository.repository.Container.__getitem__
zeit.cms.repository.repository.Container.__getitem__ = (
    getitem_with_marker_interface)
